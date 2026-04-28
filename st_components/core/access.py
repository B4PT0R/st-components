"""State access API — read/write component state from anywhere.

Public:
    widget_key(path) — canonical session_state key for a widget.
    widget_output(path) — raw widget value from session_state.
    get_state(path) — read any component/element state.
    set_state(path, ...) — update a component's state.
    callback(fn) — wrap a function as a Streamlit widget callback.
    reset_element(path) — reset an element's widget and state.

Internal:
    _resolve_path, _resolve_or_context — path/Ref resolution.
    _accepts_value — inspect whether a callback expects a value argument.
"""
import inspect

from modict import MISSING

from . import _session as ss
from .context import CallbackState, ctx, get_element_path, get_rendering_component, set_context
from .errors import CallbackError, ContextError, FiberNotFoundError, RefError, StateError, StcTypeError, UnresolvedRefError
from .models import ElementFiber
from .store import fibers


def _resolve_path(path_or_ref=None, *, expected_kind=None, fn_name="operation"):
    """Resolve a path-or-Ref argument to a fiber path string."""
    if path_or_ref is None:
        return get_element_path()

    from .refs import Ref  # circular: refs → access

    if isinstance(path_or_ref, Ref):
        if path_or_ref.path is None:
            raise UnresolvedRefError(
                f"{fn_name}() requires a resolved Ref. "
                f"Attach it to a Component or Element via the ref= prop and render the tree first."
            )
        if expected_kind is not None and path_or_ref.kind != expected_kind:
            raise RefError(
                f"{fn_name}() expected a {expected_kind} Ref, got {path_or_ref.kind!r} "
                f"(path={path_or_ref.path!r}). Pass a Ref pointing to a {expected_kind}."
            )
        return path_or_ref.path

    return path_or_ref


def _resolve_or_context(path_or_ref=None, **kwargs):
    """Resolve *path_or_ref* or fall back to the current element path."""
    return _resolve_path(path_or_ref, **kwargs) if path_or_ref is not None else get_element_path()


def widget_key(path=None):
    """Return the canonical ``session_state`` key for the widget at *path*.

    Uses the current element context if *path* is not provided.
    The key includes a revision suffix after ``reset_element()`` calls.
    """
    element_path = path or get_element_path()
    if element_path is None:
        raise ContextError(
            "widget_key() requires an element path or an active element/widget callback context. "
            "Call it from within an Element.render() method or pass an explicit path."
        )

    base_key = f"{element_path}.raw"
    revision = ss.get_or_init(ss.WIDGET_REVISIONS, dict).get(base_key, 0)
    return base_key if revision == 0 else f"{base_key}#{revision}"


def widget_output(path=None):
    """Return the raw Streamlit widget value for the element at *path* (or the current context).

    Reads directly from ``st.session_state`` using the canonical widget key.
    Returns ``MISSING`` (from modict) if the key is not present — ``None`` is a valid widget value.
    """
    element_path = _resolve_or_context(path, expected_kind="element", fn_name="widget_output")
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

    Returns ``None`` if the fiber has not been rendered yet.
    Raises ``ContextError`` if called without arguments and no active context.
    """
    path = _resolve_or_context(path_or_ref)
    if path is None:
        if path_or_ref is None:
            raise ContextError(
                "get_state() requires a path/ref or an active component context. "
                "Call it from within a render cycle or pass an explicit path/Ref."
            )
        return None
    fiber = fibers().get(path)
    return fiber.state if fiber is not None else None


def set_state(path_or_ref=None, other=None, /, **kwargs):
    """Set or update the state of a Component.

    Raises ``StateError`` if the path resolves to an Element.
    """
    path = _resolve_or_context(path_or_ref)
    if path is None:
        raise ContextError(
            "set_state() requires a path/ref or an active component context. "
            "Call it from within a render cycle or pass an explicit path/Ref."
        )
    fiber = fibers().get(path)
    if fiber is None:
        raise FiberNotFoundError(
            f"set_state(): no live fiber found at {path!r}. "
            f"Ensure the component has been rendered at least once."
        )
    if isinstance(fiber, ElementFiber):
        raise StateError(
            f"set_state() cannot target an Element (path={path!r}) — "
            f"element state is managed by the element itself. Pass a Component path or Ref."
        )

    if other is not None:
        state_cls = type(fiber.state)
        if isinstance(other, state_cls):
            fiber.state = other
        elif isinstance(other, dict):
            fiber.state = state_cls(**other)
        else:
            raise StcTypeError(
                f"set_state() expected a dict or {state_cls.__name__}, "
                f"got {type(other).__name__!r}."
            )
    if kwargs:
        fiber.state.update(**kwargs)


def _accepts_value(fn):
    """Return True if *fn* accepts at least one positional argument (beyond self)."""
    try:
        sig = inspect.signature(fn)
    except (ValueError, TypeError):
        return True  # assume it does if we can't tell
    return any(
        p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for p in sig.parameters.values()
    )


def callback(fn):
    """Wrap *fn* as a widget callback for the currently rendering Element.

    If *fn* accepts a positional argument, it receives the widget's current
    value.  Zero-argument callbacks are called without it — convenient for
    simple ``on_click`` handlers that don't need the value.

    Captures the current ``rerun_scope`` at wrap time so that ``rerun()`` /
    ``wait()`` calls inside the callback target the same scope as the
    enclosing render — typically the scoped fragment that owns the widget.
    Without this, callbacks fired by Streamlit run outside the fragment's
    context stack and would default to the ``"app"`` scope.

    Returns ``None`` when *fn* is ``None``.
    """
    if fn is None:
        return None

    from .base import Element  # circular: base → access

    element = get_rendering_component()
    if not isinstance(element, Element):
        raise CallbackError(
            "callback() must be called from within an Element.render() method. "
            "It wraps a function as a Streamlit widget callback tied to the current element."
        )

    element_path = element._fiber_key
    wk = element.fiber.widget_key if element.fiber else None
    wants_value = _accepts_value(fn)
    rerun_scope = ctx.current("rerun_scope", "app")

    def wrapped():
        with set_context(
            callback={"element_path": element_path, "widget_key": wk},
            rerun_scope=rerun_scope,
        ):
            value = element._current_output()
            with element.state._writable():
                element.state.output = value
            return fn(value) if wants_value else fn()

    return wrapped


def reset_element(path=None):
    """Reset an Element's widget value in session_state and bump its revision key.

    The element will re-initialize with its default value on the next render.
    """
    element_path = _resolve_path(path, expected_kind="element", fn_name="reset_element")
    if element_path is None:
        raise ContextError(
            "reset_element() requires an element path or an active element/widget callback context. "
            "Call it from within an Element render or pass an explicit path/Ref."
        )

    base_key = f"{element_path}.raw"
    current_key = widget_key(element_path)
    for key in {base_key, current_key}:
        ss.delete(key)

    revisions = ss.get_or_init(ss.WIDGET_REVISIONS, dict)
    revisions[base_key] = revisions.get(base_key, 0) + 1
    ss.put(ss.WIDGET_REVISIONS, revisions)

    fiber = fibers().get(element_path)
    if isinstance(fiber, ElementFiber):
        fiber.state = type(fiber.state)()
