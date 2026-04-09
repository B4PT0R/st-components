from streamlit import session_state as state
from modict import MISSING

from .context import Context, callback_context, get_element_path


_WIDGET_REVISIONS_KEY = "__st_components_widget_revisions__"


def _raw_key(path: str) -> str:
    """Key under which layout element Streamlit objects are stored (e.g. container, form)."""
    return f"{path}.raw"


def _base_value_key(path: str) -> str:
    """Key under which input widget Streamlit values are stored."""
    return f"{path}.raw"


def _resolve_path(path_or_ref=None, *, expected_kind=None, fn_name="operation"):
    if path_or_ref is None:
        return get_element_path()

    try:
        from .refs import Ref
    except Exception:
        Ref = None

    if Ref is not None and isinstance(path_or_ref, Ref):
        if path_or_ref.path is None:
            raise RuntimeError(
                f"{fn_name}() requires a resolved Ref. Attach it to a Component or Element and render the tree first."
            )
        if expected_kind is not None and path_or_ref.kind != expected_kind:
            raise RuntimeError(
                f"{fn_name}() expected a {expected_kind} Ref, got {path_or_ref.kind!r}."
            )
        return path_or_ref.path

    return path_or_ref


def _widget_revisions():
    revisions = state.get(_WIDGET_REVISIONS_KEY)
    if revisions is None:
        revisions = {}
        state[_WIDGET_REVISIONS_KEY] = revisions
    return revisions


def widget_key(path=None):
    element_path = path or get_element_path()
    if element_path is None:
        raise RuntimeError(
            "widget_key() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    revision = _widget_revisions().get(base_key, 0)
    if revision == 0:
        return base_key
    return f"{base_key}#{revision}"


def widget_output(path=None):
    """Return the raw Streamlit widget value for the element at *path* (or the current context).

    Reads directly from ``st.session_state`` using the canonical widget key.
    Returns ``MISSING`` (from modict) if the key is not present — ``None`` is a valid widget value.
    Intended for use inside element ``render()`` implementations to read the
    current widget value before deriving element state from it.
    """
    from .store import fibers
    from .models import ElementFiber

    element_path = _resolve_path(path, expected_kind="element", fn_name="widget_output") if path is not None else get_element_path()
    if element_path is None:
        if Context.callback.widget_key is not None:
            return state.get(Context.callback.widget_key, MISSING)
        return MISSING

    fiber = fibers().get(element_path)
    wk = fiber.widget_key if isinstance(fiber, ElementFiber) else widget_key(element_path)
    return state.get(wk, MISSING)


def get_state(path_or_ref=None):
    """Return the current state for any Component or Element.

    - For a **Component**: returns the live ``State`` object (mutable).
    - For an **Element**: returns a frozen snapshot of the element's state (read-only).
    - Returns ``None`` if the path doesn't resolve to a live fiber.
    """
    from .store import fibers
    from .models import ElementFiber

    path = _resolve_path(path_or_ref) if path_or_ref is not None else get_element_path()
    if path is None:
        return None
    fiber = fibers().get(path)
    if fiber is None:
        return None

    if isinstance(fiber, ElementFiber):
        return fiber.state

    return fiber.state


def set_state(path_or_ref=None, other=None, /, **kwargs):
    """Set or update the state of a Component.

    - *path_or_ref* — path string, ``Ref``, or ``None`` (defaults to the current context component).
    - *other* — a ``dict`` or ``State`` instance that replaces the current state wholesale.
    - **kwargs — field updates applied on top (or instead) of *other*.

    Raises ``RuntimeError`` if the path resolves to an Element; element state is
    managed exclusively by the element's own ``render()`` method.
    """
    from .store import fibers
    from .models import ElementFiber

    path = _resolve_path(path_or_ref) if path_or_ref is not None else get_element_path()
    if path is None:
        raise RuntimeError(
            "set_state() requires a path/ref or an active component context."
        )
    fiber = fibers().get(path)
    if fiber is None:
        raise RuntimeError(f"set_state(): no live fiber found at {path!r}.")
    if isinstance(fiber, ElementFiber):
        raise RuntimeError(
            "set_state() cannot target an Element — element state is managed by the element itself. "
            "Pass a Component path or Ref."
        )

    if other is not None:
        state_cls = type(fiber.state)
        if isinstance(other, state_cls):
            fiber.state = other
        elif isinstance(other, dict):
            fiber.state = state_cls(**other)
        else:
            raise TypeError(
                f"set_state() expected a dict or {state_cls.__name__}, got {type(other).__name__!r}."
            )
    if kwargs:
        fiber.state.update(**kwargs)


def callback(fn):
    """Wrap *fn* as a widget callback for the currently rendering Element.

    Resolves the element from the active render context, captures its path and
    widget key, and returns a zero-argument callable suitable for ``on_change`` /
    ``on_click`` / ``on_select`` parameters of ``st.*`` widgets.  When invoked,
    reads the element's current output, writes it to ``state.output``, and calls
    ``fn(value)``.

    Returns ``None`` when *fn* is ``None``.
    """
    if fn is None:
        return None

    from .context import get_rendering_component
    from .base import Element

    element = get_rendering_component()
    if not isinstance(element, Element):
        raise RuntimeError(
            "callback() must be called from within an Element.render() method."
        )

    element_path = element._fiber_key
    wk = element.fiber.widget_key if element.fiber else None

    def wrapped():
        with callback_context(element_path=element_path, widget_key=wk):
            value = element._current_output()
            with element.state._writable():
                element.state.output = value
            return fn(value)

    return wrapped


def reset_element(path=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="reset_element")
    if element_path is None:
        raise RuntimeError(
            "reset_element() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    current_key = widget_key(element_path)
    if base_key in state:
        del state[base_key]
    if current_key in state and current_key != base_key:
        del state[current_key]

    revisions = _widget_revisions()
    revisions[base_key] = revisions.get(base_key, 0) + 1
    state[_WIDGET_REVISIONS_KEY] = revisions

    from .store import fibers
    from .models import ElementFiber, ElementState
    fiber = fibers().get(element_path)
    if isinstance(fiber, ElementFiber):
        # Reset state to a fresh default instance of the same class
        state_cls = type(fiber.state)
        fiber.state = state_cls()


