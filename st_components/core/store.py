import inspect
from copy import deepcopy

from modict import modict
from streamlit import session_state as state


class State(modict):
    pass


class Fiber(modict):
    state = modict.factory(State)
    component = None
    rendered_state = None


def shared_states():
    if "__st_components_shared__" not in state:
        state.__st_components_shared__ = modict()
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
            f"Shared state {namespace!r} is not declared. Declare it with App.shared_state(...)."
        )
    return store[namespace]


def clear_shared_state(namespace=None):
    store = shared_states()
    if namespace is None:
        store.clear()
        return
    if namespace in store:
        del store[namespace]


def fibers():
    if "__fibers__" not in state:
        state.__fibers__ = modict()
    return state.__fibers__


def _render_cycle_fibers():
    if "__render_cycle_fibers__" not in state:
        state.__render_cycle_fibers__ = set()
    return state.__render_cycle_fibers__


def _render_cycle_previous_states():
    if "__render_cycle_previous_states__" not in state:
        state.__render_cycle_previous_states__ = {}
    return state.__render_cycle_previous_states__


def track_rendered_fiber(fiber_key):
    if "__render_cycle_fibers__" in state:
        _render_cycle_fibers().add(fiber_key)


def begin_render_cycle():
    state.__render_cycle_fibers__ = set()
    state.__render_cycle_previous_states__ = {
        fiber_key: deepcopy(fiber.rendered_state)
        for fiber_key, fiber in fibers().items()
        if fiber.rendered_state is not None
    }


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
        if fiber is not None and fiber.component is not None:
            fiber.component.component_did_unmount()
        if fiber_key in fibers():
            del fibers()[fiber_key]

    for fiber_key in updated_fiber_keys:
        fiber = fibers().get(fiber_key)
        if fiber is not None and fiber.component is not None:
            fiber.component.component_did_update(previous_states[fiber_key])

    for fiber_key in rendered_fibers:
        fiber = fibers().get(fiber_key)
        if fiber is not None:
            fiber.rendered_state = deepcopy(fiber.state)

    del state.__render_cycle_fibers__
    del state.__render_cycle_previous_states__
