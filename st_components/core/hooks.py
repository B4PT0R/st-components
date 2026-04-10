"""React-style hooks for functional and class-based components.

All hooks must be called **during render** and always in the **same order**
across reruns — no hooks inside conditions or loops.
"""
from .context import get_context_value, get_rendering_component


class RefValue:
    """Mutable container returned by :func:`use_ref`.  Access via ``.current``."""
    def __init__(self, current=None):
        self.current = current

    def __repr__(self):
        return f"RefValue({self.current!r})"


def _current_node():
    node = get_rendering_component()
    if node is None:
        raise RuntimeError("Hooks must be called while rendering a Component or Element.")
    return node


def _use_hook_slot(kind):
    return _current_node()._use_hook_slot(kind)


def _normalize_deps(deps):
    return tuple(deps) if deps is not None else None


def use_state(other=None, /, **kwargs):
    """Declare local component state.  Returns the live ``State`` object.

    Initializes once on mount, then returns the persisted state on reruns::

        @component
        def Counter(props):
            state = use_state(count=0)
            return button(key="inc", on_click=lambda: state.update(count=state.count + 1))(
                str(state.count)
            )

    Accepts a dict, keyword args, or a ``State`` instance.
    Cannot be used inside an Element — use ``self.state`` directly.
    """
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
    """Read the nearest provider's value for *context*.

    Returns the default value if no provider is above this component::

        theme = use_context(ThemeContext)
        # theme.mode, theme.accent, etc.
    """
    _current_node()
    return get_context_value(context)


def use_memo(factory, deps=None):
    """Memoize the return value of *factory*, recomputing only when *deps* change.

    - ``deps=None`` → recompute every render.
    - ``deps=[]`` → compute once, never recompute.
    - ``deps=[x, y]`` → recompute when x or y changes.

    ::

        filtered = use_memo(lambda: expensive_filter(data), deps=[data])
    """
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
    """Return a mutable :class:`RefValue` that persists across reruns.

    Unlike state, mutating a ref does **not** trigger a rerun::

        render_count = use_ref(0)
        render_count.current += 1
    """
    slot = _current_node()._use_hook_slot("ref")
    if not slot.initialized:
        slot.value = RefValue(initial)
        slot.initialized = True
    return slot.value


def use_callback(callback, deps=None):
    """Memoize *callback* — returns the same function object while *deps* are unchanged.

    Equivalent to ``use_memo(lambda: callback, deps)``.
    """
    if not callable(callback):
        raise TypeError(f"use_callback() expects a callable, got {type(callback)}")
    return use_memo(lambda: callback, deps)


def use_previous(value, initial=None):
    """Return the value of *value* from the **previous** render.

    Returns *initial* on the first render::

        prev_count = use_previous(state.count)
        if prev_count is not None and prev_count != state.count:
            # count just changed
    """
    ref = use_ref(initial)
    previous = ref.current
    ref.current = value
    return previous


def use_id():
    """Generate a stable, unique identifier for this hook position.

    The ID is deterministic (based on the component's fiber path and hook
    index) and persists across reruns.  Useful for Streamlit widget keys
    that must be unique but stable.
    """
    current = _current_node()
    index, slot = current._claim_hook_slot("id")
    if not slot.initialized:
        fiber_key = current._fiber_key or type(current).__name__
        slot.value = f"{fiber_key}:hook:{index}"
        slot.initialized = True
    return slot.value


def use_effect(effect, deps=None):
    """Run *effect* after render when *deps* change.  *effect* may return a cleanup function.

    - ``deps=None`` → run after every render.
    - ``deps=[]`` → run once on mount, cleanup on unmount.
    - ``deps=[x]`` → run when x changes, cleanup before re-running.

    ::

        def effect():
            conn = open_connection()
            return conn.close          # cleanup

        use_effect(effect, deps=[url])
    """
    if not callable(effect):
        raise TypeError(f"use_effect() expects a callable effect, got {type(effect)}")
    current = _current_node()
    index, slot = current._claim_hook_slot("effect")
    normalized_deps = _normalize_deps(deps)
    if not slot.initialized or normalized_deps is None or slot.deps != normalized_deps:
        slot.deps = normalized_deps
        slot.initialized = True
        current._queue_hook_effect(index, effect)
