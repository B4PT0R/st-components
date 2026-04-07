import inspect
from copy import deepcopy

from modict import modict
from streamlit import session_state as state
from .models import Fibers, PreviousStates, SharedStates, State

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except Exception:  # pragma: no cover - fallback for bare mode / test doubles
    get_script_run_ctx = None


_COMPONENT_REGISTRY = {}


def _session_registry_key():
    if get_script_run_ctx is None:
        return "bare"
    ctx = get_script_run_ctx()
    if ctx is None:
        return "bare"
    return getattr(ctx, "session_id", "bare")


def _component_registry():
    session_key = _session_registry_key()
    return _COMPONENT_REGISTRY.setdefault(session_key, {})


def register_component(component_id, component):
    _component_registry()[component_id] = component


def resolve_component(component_id):
    if component_id is None:
        return None
    return _component_registry().get(component_id)


def unregister_component(component_id):
    if component_id is None:
        return
    registry = _component_registry()
    if component_id in registry:
        del registry[component_id]


def shared_states() -> SharedStates:
    if "__st_components_shared__" not in state:
        state.__st_components_shared__ = SharedStates()
    return state.__st_components_shared__


def _shared_state_instance(spec):
    if isinstance(spec, State):
        return spec
    if inspect.isclass(spec) and issubclass(spec, State):
        return spec()
    raise TypeError(
        "Shared state spec must be a State instance or a State subclass."
    )


def declare_shared_state(namespace, spec):
    store = shared_states()
    if namespace not in store:
        store[namespace] = _shared_state_instance(spec)
    return store[namespace]


def get_shared_state(namespace, /):
    store = shared_states()
    if namespace not in store:
        raise RuntimeError(
            f"Shared state {namespace!r} is not declared. Declare it with App.create_shared_state(...)."
        )
    return store[namespace]


def clear_shared_state(namespace=None):
    store = shared_states()
    if namespace is None:
        store.clear()
        return
    if namespace in store:
        del store[namespace]


def fibers() -> Fibers:
    if "__fibers__" not in state:
        state.__fibers__ = Fibers()
    return state.__fibers__


def _render_cycle_fibers():
    if "__render_cycle_fibers__" not in state:
        state.__render_cycle_fibers__ = set()
    return state.__render_cycle_fibers__


def _render_cycle_previous_states() -> PreviousStates:
    if "__render_cycle_previous_states__" not in state:
        state.__render_cycle_previous_states__ = PreviousStates()
    return state.__render_cycle_previous_states__


def track_rendered_fiber(fiber_key):
    if "__render_cycle_fibers__" in state:
        _render_cycle_fibers().add(fiber_key)


def mark_subtree_keep_alive(prefix):
    for key, fiber in fibers().items():
        if key == prefix or key.startswith(prefix + "."):
            fiber.keep_alive = True


def begin_render_cycle():
    for fiber in fibers().values():
        fiber.keep_alive = False
    state.__render_cycle_fibers__ = set()
    state.__render_cycle_previous_states__ = PreviousStates({
        fiber_key: deepcopy(fiber.previous_state)
        for fiber_key, fiber in fibers().items()
        if fiber.previous_state is not None
    })


def end_render_cycle():
    rendered_fibers = _render_cycle_fibers()
    previous_states = _render_cycle_previous_states()

    updated_fiber_keys = [
        fiber_key
        for fiber_key in rendered_fibers
        if fiber_key in previous_states
        and fiber_key in fibers()
        and fibers()[fiber_key].state != previous_states[fiber_key]
    ]

    stale_fiber_keys = [fiber_key for fiber_key in list(fibers().keys()) if fiber_key not in rendered_fibers]
    for fiber_key in stale_fiber_keys:
        fiber = fibers().get(fiber_key)
        if fiber is not None and fiber.keep_alive:
            continue
        component = resolve_component(fiber.component_id) if fiber is not None else None
        if component is not None:
            component._cleanup_hook_effects()
            component.component_did_unmount()
        if fiber is not None:
            unregister_component(fiber.component_id)
        if fiber_key in fibers():
            del fibers()[fiber_key]

    for fiber_key in updated_fiber_keys:
        fiber = fibers().get(fiber_key)
        component = resolve_component(fiber.component_id) if fiber is not None else None
        if component is not None:
            component.component_did_update(previous_states[fiber_key])

    for fiber_key in rendered_fibers:
        fiber = fibers().get(fiber_key)
        component = resolve_component(fiber.component_id) if fiber is not None else None
        if component is not None:
            component._flush_hook_effects()

    for fiber_key in rendered_fibers:
        fiber = fibers().get(fiber_key)
        if fiber is not None:
            fiber.previous_state = deepcopy(fiber.state)

    del state.__render_cycle_fibers__
    del state.__render_cycle_previous_states__
