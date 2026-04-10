from copy import deepcopy

from . import _session as ss
from .models import ElementFiber, Fiber, Fibers, SharedStates, State

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except Exception:  # pragma: no cover - fallback for bare mode / test doubles
    get_script_run_ctx = None


# ── Component registry ───────────────────────────────────────────────────────
# Maps component_id → live Component instance.  Module-level dict (not in
# session_state) because Component objects are not serializable.  Partitioned
# by Streamlit session id so concurrent sessions don't collide.  Entries are
# pruned each render cycle by begin_render_cycle → _reset_registry().

_COMPONENT_REGISTRIES: dict[str, dict] = {}


def _session_id():
    if get_script_run_ctx is None:
        return "bare"
    ctx = get_script_run_ctx()
    return getattr(ctx, "session_id", "bare") if ctx else "bare"


def _component_registry():
    return _COMPONENT_REGISTRIES.setdefault(_session_id(), {})


def register_component(component_id, component):
    _component_registry()[component_id] = component


def resolve_component(component_id):
    return _component_registry().get(component_id) if component_id else None


def unregister_component(component_id):
    if component_id is not None:
        _component_registry().pop(component_id, None)


def _reset_registry():
    """Drop all entries for the current session.

    Called at the start of each render cycle — components are re-created on
    every Streamlit rerun, so stale entries are never needed.
    """
    _COMPONENT_REGISTRIES[_session_id()] = {}


# ── Shared state ─────────────────────────────────────────────────────────────

def shared_states() -> SharedStates:
    return ss.get_or_init(ss.SHARED_STATES, SharedStates)


def _shared_state_instance(spec):
    if isinstance(spec, State):
        return spec
    if isinstance(spec, type) and issubclass(spec, State):
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


# ── Fibers ───────────────────────────────────────────────────────────────────

_fibers_cache: Fibers | None = None


def fibers() -> Fibers:
    global _fibers_cache
    if _fibers_cache is not None:
        return _fibers_cache
    f = ss.get_or_init(ss.FIBERS, Fibers)
    _fibers_cache = f
    return f


def _invalidate_fibers_cache():
    global _fibers_cache
    _fibers_cache = None


def _render_cycle_fibers():
    return ss.get_or_init(ss.CYCLE_FIBERS, set)


def track_rendered_fiber(fiber_key):
    if ss.has(ss.CYCLE_FIBERS):
        _render_cycle_fibers().add(fiber_key)


def mark_subtree_keep_alive(prefix):
    for key, fiber in fibers().items():
        if key == prefix or key.startswith(prefix + "."):
            fiber.keep_alive = True


# ── Render cycle ─────────────────────────────────────────────────────────────

def begin_render_cycle():
    """Prepare a new render cycle.

    Resets the transient render context, clears keep_alive flags, and starts
    tracking which fibers are rendered.  Change detection uses
    ``fiber.previous_state`` directly — no upfront deepcopy needed.
    """
    from .context import _reset_runtime_context

    # Reset transient render context and caches
    _reset_runtime_context()
    _invalidate_fibers_cache()

    # Prepare fiber tracking
    for fiber in fibers().values():
        fiber.keep_alive = False
    ss.put(ss.CYCLE_FIBERS, set())


def _cleanup_effect_slots(hooks):
    """Run and clear cleanup callbacks for all effect hooks.

    All cleanups run even if one raises — the first exception is re-raised
    after all cleanups have been attempted.
    """
    first_error = None
    for slot in hooks:
        if slot.kind == "effect" and slot.cleanup is not None:
            try:
                slot.cleanup()
            except Exception as exc:
                if first_error is None:
                    first_error = exc
            slot.cleanup = None
    if first_error is not None:
        raise first_error


def _unmount_stale_fibers(rendered_fibers):
    """Remove fibers that were not rendered (unless keep_alive)."""
    all_fibers = fibers()
    stale_keys = [k for k in all_fibers if k not in rendered_fibers]
    for fiber_key in stale_keys:
        fiber = all_fibers.get(fiber_key)
        if fiber is None or fiber.keep_alive:
            continue
        if isinstance(fiber, ElementFiber):
            _cleanup_effect_slots(fiber.hooks)
        else:
            component = resolve_component(fiber.component_id)
            if component is not None:
                component._cleanup_hook_effects()
                component.component_did_unmount()
            unregister_component(fiber.component_id)
        del all_fibers[fiber_key]


def end_render_cycle():
    """Finalize a render cycle: unmount stale fibers, run lifecycle hooks, flush effects."""
    rendered_fibers = _render_cycle_fibers()
    all_fibers = fibers()

    # 1. Unmount stale fibers
    _unmount_stale_fibers(rendered_fibers)

    # 2. Notify updated components & flush effects, then snapshot state.
    #    previous_state holds the snapshot from the last cycle — compare
    #    directly instead of maintaining a separate copy.
    for fiber_key in rendered_fibers:
        fiber = all_fibers.get(fiber_key)
        if fiber is None or isinstance(fiber, ElementFiber):
            continue

        component = resolve_component(fiber.component_id)

        if fiber.previous_state is not None and fiber.state != fiber.previous_state:
            if component is not None:
                component.component_did_update(fiber.previous_state)

        if component is not None:
            component._flush_hook_effects()

        fiber.previous_state = deepcopy(fiber.state)

    ss.delete(ss.CYCLE_FIBERS)
