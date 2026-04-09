from .base import Component
from .context import get_context_value, get_rendering_component


class RefValue:
    def __init__(self, current=None):
        self.current = current


def _current_node():
    current = get_rendering_component()
    if current is None:
        raise RuntimeError("Hooks must be called while rendering a Component or Element.")
    return current


def _use_hook_slot(kind):
    return _current_node()._use_hook_slot(kind)


def _claim_hook_slot(kind):
    return _current_node()._claim_hook_slot(kind)


def _normalize_deps(deps):
    if deps is None:
        return None
    return tuple(deps)


def use_state(other=None, /, **kwargs):
    from .base import Element
    current = _current_node()
    if isinstance(current, Element):
        raise RuntimeError("use_state() cannot be used inside Element.render(). Use self.state directly to manage element state.")
    slot = current._use_hook_slot("state")

    if not slot.initialized:
        if other is not None:
            current.set_state(other)
        elif kwargs:
            current.set_state(kwargs)
        slot.initialized = True

    return current.state


def use_context(context):
    _current_node()
    return get_context_value(context)


def use_memo(factory, deps=None):
    if not callable(factory):
        raise TypeError(f"use_memo() expects a callable factory, got {type(factory)}")

    slot = _current_node()._use_hook_slot("memo")
    normalized_deps = _normalize_deps(deps)

    if not slot.initialized or normalized_deps is None or slot.deps != normalized_deps:
        slot.value = factory()
        slot.deps = normalized_deps
        slot.initialized = True

    return slot.value


def use_ref(initial=None):
    slot = _current_node()._use_hook_slot("ref")

    if not slot.initialized:
        slot.value = RefValue(initial)
        slot.initialized = True

    return slot.value


def use_callback(callback, deps=None):
    if not callable(callback):
        raise TypeError(f"use_callback() expects a callable, got {type(callback)}")
    return use_memo(lambda: callback, deps)


def use_previous(value, initial=None):
    ref = use_ref(initial)
    previous = ref.current
    ref.current = value
    return previous


def use_id():
    current = _current_node()
    index, slot = current._claim_hook_slot("id")

    if not slot.initialized:
        fiber_key = getattr(current, "_fiber_key", None) or type(current).__name__
        slot.value = f"{fiber_key}:hook:{index}"
        slot.initialized = True

    return slot.value


def use_effect(effect, deps=None):
    if not callable(effect):
        raise TypeError(f"use_effect() expects a callable effect, got {type(effect)}")

    current = _current_node()
    index, slot = current._claim_hook_slot("effect")
    normalized_deps = _normalize_deps(deps)

    should_run = (
        not slot.initialized
        or normalized_deps is None
        or slot.deps != normalized_deps
    )

    if should_run:
        slot.deps = normalized_deps
        slot.initialized = True
        current._queue_hook_effect(index, effect)
