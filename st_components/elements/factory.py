"""Element factory and widget helpers — bridge between Component props and st.* calls.

Components or Elements passed as props are rendered by the receiving element
using ``render()`` at the appropriate location in its own ``render()`` method,
exactly like children. No automatic resolution — the element author decides.

Public:
    widget_key, widget_output, callback — re-exported from core.access.
    widget_child(prop_name) — resolve the first child or named prop for the label argument.
    widget_props(*excluded) — build the kwargs dict for the st.* call.
    widget_callback(prop_name) — wrap a prop as a Streamlit callback.
    render_handle / get_render_target — container handle tracking.
    element_factory — generate an Element subclass from an st.* callable.
"""
from contextlib import contextmanager

from ..core import Element  # noqa: F401
from ..core.access import callback, widget_key, widget_output  # noqa: F401
from ..core.context import ctx, set_context


# ── Render target tracking ───────────────────────────────────────────────────

@contextmanager
def render_handle(handle, path=None):
    """Context manager that pushes a Streamlit container handle onto the context.

    Used by container-like elements to track the active render target.
    Code inside callbacks or effects can read it via :func:`get_render_target`
    to render dynamically into the current container::

        target = get_render_target()
        with target.handle:
            MyComponent(key="dynamic").render()

    The *path* is the fiber path of the owning element, so dynamically
    rendered components can root their fibers correctly.
    """
    with set_context(render_handle=handle, render_path=path):
        with handle:
            yield handle


def get_render_target():
    """Return the active render target (handle + path), or ``None``.

    ::

        target = get_render_target()
        if target:
            with target.handle:
                with set_context(keys=target.path):
                    MyComponent(key="dyn").render()
    """
    from modict import modict
    handle = ctx.current("render_handle")
    if handle is None:
        return None
    path = ctx.current("render_path")
    return modict(handle=handle, path=path)


def _props():
    """Return the props of the currently rendering Component/Element."""
    from ..core.context import get_rendering_component
    component = get_rendering_component()
    if component is None:
        raise RuntimeError("widget helpers must be called from within a Component.render() method.")
    return component.props



def widget_child(prop_name, default=None):
    """Resolve the first child or named prop as the positional label argument."""
    props = _props()
    return props.children[0] if props.children else props.get(prop_name, default)


def widget_props(*excluded):
    """Build the kwargs dict for the ``st.*`` call, excluding framework props."""
    return _props().exclude("key", "children", "ref", *excluded)


def widget_callback(prop_name="on_change"):
    """Wrap the *prop_name* prop of the currently rendering Element as a widget callback.

    Shorthand for ``callback(props.get(prop_name))``: resolves props from the
    active render context and delegates to ``callback()``.

    Returns ``None`` when the prop is absent or ``None``.
    """
    return callback(_props().get(prop_name))


__all__ = [
    "Element",
    "element_factory",
    "callback",
    "get_render_target",
    "render_handle",
    "widget_callback",
    "widget_child",
    "widget_key",
    "widget_output",
    "widget_props",
]


def element_factory(streamlit_fn, *, child_prop=None, callback_prop=None, default_prop=None, props_schema=None, spec_prop=None, spec_type="int", has_key=True):
    """Generate an Element subclass wrapping *streamlit_fn*.

    Args:
        streamlit_fn:   the ``st.*`` callable to wrap.
        child_prop:     prop name (or ``(name, default)`` tuple) forwarded as the
                        first positional argument via ``widget_child()``.
        callback_prop:  prop name of the event callback, forwarded via
                        ``widget_callback(prop_name)``.  ``None`` means no callback.
        default_prop:   prop name used as the initial output value when the widget
                        has not yet been registered in session state.  ``None`` means
                        the output defaults to ``None`` before first render.
        spec_prop:      prop name for a *spec* argument (e.g. ``"spec"`` for
                        ``st.columns``, ``"tabs"`` for ``st.tabs``).  When the prop
                        is absent, the spec is derived from the number of children:
                        ``len(children)`` when ``spec_type="int"`` (columns-like) or
                        ``[str(i) for i in range(len(children))]`` when
                        ``spec_type="list"`` (tabs-like).
        spec_type:      ``"int"`` or ``"list"`` — controls how the spec is derived
                        from children count when ``spec_prop`` is not supplied by the
                        caller.  Ignored when ``spec_prop`` is ``None``.
        has_key:        whether to pass ``key=widget_key()`` to *streamlit_fn*.
                        Set to ``False`` for layout containers that do not accept a
                        ``key`` parameter (e.g. ``st.columns``, ``st.tabs``).

    If *streamlit_fn* returns a single context manager, all children are rendered
    inside it.  If it returns an iterable of context managers (e.g. ``st.columns``),
    children are zipped with the containers and each child is rendered inside the
    corresponding one.

    Convenience helper for the common case.  Subclass ``Element`` directly when
    you need a typed ``__init__`` or custom ``get_output``.

    Example::

        text_input = element_factory(st.text_input,  child_prop="label", callback_prop="on_change", default_prop="value")
        button     = element_factory(st.button,       child_prop="label", callback_prop="on_click")
        multiselect = element_factory(st.multiselect, child_prop="label", callback_prop="on_change", default_prop="default")
        columns = element_factory(st.columns, spec_prop="spec", spec_type="int",  has_key=False)
        tabs    = element_factory(st.tabs,    spec_prop="tabs", spec_type="list", has_key=False)
    """
    if isinstance(child_prop, tuple):
        child_name, child_default = child_prop
    elif child_prop is not None:
        child_name, child_default = child_prop, None
    else:
        child_name = child_default = None

    excluded = [x for x in (child_name, callback_prop, spec_prop) if x is not None]

    def render(self):
        from ..core.context import get_rendering_component
        from ..core.base import render as render_child
        children = get_rendering_component().props.children
        if spec_prop is not None:
            spec = _props().get(spec_prop)
            if spec is None:
                spec = len(children) if spec_type == "int" else [str(i) for i in range(len(children))]
            args = [spec]
        elif child_name is not None:
            args = [widget_child(child_name, child_default)]
        else:
            args = []
        kw = {callback_prop: widget_callback(callback_prop)} if callback_prop is not None else {}
        if has_key:
            kw["key"] = widget_key()
        result = streamlit_fn(*args, **kw, **widget_props(*excluded))
        if isinstance(result, (list, tuple)) and result and hasattr(result[0], "__enter__"):
            for ctx, child in zip(result, children):
                with ctx:
                    render_child(child)
        elif hasattr(result, "__enter__"):
            with result:
                for child in children:
                    render_child(child)

    cls_attrs = {"render": render, "_default_output_prop": default_prop}
    if props_schema is not None:
        cls_attrs["__props_class__"] = props_schema
    return type(streamlit_fn.__name__, (Element,), cls_attrs)
