from . import _session as ss
from .context import CallbackState, ctx, set_context, get_element_path


def _base_value_key(path: str) -> str:
    """Key under which Streamlit widget values / layout objects are stored."""
    return f"{path}.raw"


def _resolve_path(path_or_ref=None, *, expected_kind=None, fn_name="operation"):
    if path_or_ref is None:
        return get_element_path()

    from .refs import Ref

    if isinstance(path_or_ref, Ref):
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
    return ss.get_or_init(ss.WIDGET_REVISIONS, dict)


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
    """
    from modict import MISSING
    from .store import fibers
    from .models import ElementFiber

    element_path = _resolve_path(path, expected_kind="element", fn_name="widget_output") if path is not None else get_element_path()
    if element_path is None:
        cb = ctx.current("callback")
        if isinstance(cb, CallbackState) and cb.widget_key is not None:
            return ss.get(cb.widget_key, MISSING)
        return MISSING

    fiber = fibers().get(element_path)
    wk = fiber.widget_key if isinstance(fiber, ElementFiber) else widget_key(element_path)
    return ss.get(wk, MISSING)


def get_state(path_or_ref=None):
    """Return the current state for any Component or Element.

    Returns ``None`` if the path doesn't resolve to a live fiber.
    """
    from .store import fibers

    path = _resolve_path(path_or_ref) if path_or_ref is not None else get_element_path()
    if path is None:
        return None
    fiber = fibers().get(path)
    return fiber.state if fiber is not None else None


def set_state(path_or_ref=None, other=None, /, **kwargs):
    """Set or update the state of a Component.

    Raises ``RuntimeError`` if the path resolves to an Element.
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


def _accepts_value(fn):
    """Return True if *fn* accepts at least one positional argument (beyond self)."""
    import inspect
    try:
        sig = inspect.signature(fn)
    except (ValueError, TypeError):
        return True  # assume it does if we can't tell
    params = [
        p for p in sig.parameters.values()
        if p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    # For bound methods, `self` is already consumed — params are the remaining ones.
    # For plain functions / lambdas, first param is the value.
    return len(params) >= 1


def callback(fn):
    """Wrap *fn* as a widget callback for the currently rendering Element.

    If *fn* accepts a positional argument, it receives the widget's current
    value.  Zero-argument callbacks are called without it — convenient for
    simple ``on_click`` handlers that don't need the value.

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
    wants_value = _accepts_value(fn)

    def wrapped():
        with set_context(callback={"element_path": element_path, "widget_key": wk}):
            value = element._current_output()
            with element.state._writable():
                element.state.output = value
            return fn(value) if wants_value else fn()

    return wrapped


def reset_element(path=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="reset_element")
    if element_path is None:
        raise RuntimeError(
            "reset_element() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    current_key = widget_key(element_path)
    for key in {base_key, current_key}:
        ss.delete(key)

    revisions = _widget_revisions()
    revisions[base_key] = revisions.get(base_key, 0) + 1
    ss.put(ss.WIDGET_REVISIONS, revisions)

    from .store import fibers
    from .models import ElementFiber
    fiber = fibers().get(element_path)
    if isinstance(fiber, ElementFiber):
        fiber.state = type(fiber.state)()
