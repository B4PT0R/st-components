"""Error boundary — catches render errors in child subtrees.

Prevents a single broken component from crashing the entire app.
Displays a fallback UI when an error occurs, and exposes the error
in its state for programmatic handling::

    ErrorBoundary(key="safe")(
        RiskyComponent(key="risky"),
    )

    # Custom fallback:
    ErrorBoundary(key="safe", fallback=MyFallback(key="fb"))(
        RiskyComponent(key="risky"),
    )

    # Callable fallback receiving the error:
    ErrorBoundary(key="safe", fallback=lambda e: f"Broke: {e}")(
        RiskyComponent(key="risky"),
    )

    # Read captured error:
    state = get_state("app.safe")
    if state.error is not None:
        log(state.error)
"""
import traceback

import streamlit as st

from ..core.base import Component, Element, render as render_child
from ..core.models import Props, State


class ErrorBoundaryProps(Props):
    fallback: object = None


class ErrorBoundaryState(State):
    error: BaseException | None = None
    error_traceback: str | None = None


class ErrorBoundary(Component):
    """Catch render errors in children and display a fallback.

    Props:
        fallback: A Component, Element, string, or callable(error) -> renderable.
                  Defaults to an ``st.error()`` message showing the traceback.

    State:
        error:            The caught exception, or ``None``.
        error_traceback:  Formatted traceback string, or ``None``.
    """
    __props_class__ = ErrorBoundaryProps
    __initial_state_class__ = ErrorBoundaryState

    def render(self):
        # Reset error state each cycle — if children render fine, error clears.
        self.state.error = None
        self.state.error_traceback = None

        # Render children immediately inside a try/except.
        # We return an _ErrorBoundaryAnchor that does the actual rendering
        # with error catching, instead of returning children directly
        # (which would defer rendering to the parent Anchor).
        return _ErrorBoundaryAnchor(
            key=self.key,
            boundary=self,
        )(*self.children)


class _ErrorBoundaryAnchor(Element):
    """Internal element that renders children with error catching."""

    def render(self):
        boundary = self.props.get("boundary")
        try:
            for child in self.children:
                render_child(child)
        except Exception as exc:
            boundary.state.error = exc
            boundary.state.error_traceback = traceback.format_exc()
            _show_fallback(
                boundary.props.fallback,
                exc,
                boundary.state.error_traceback,
            )


def _show_fallback(fallback, error, tb):
    """Resolve and display the fallback."""
    if fallback is None:
        _default_fallback(error, tb)
        return

    if callable(fallback) and not isinstance(fallback, (Component, Element)):
        result = fallback(error)
        if result is not None:
            render_child(result)
        return

    render_child(fallback)


def _default_fallback(error, tb):
    """Default fallback: st.error + collapsible traceback."""
    label = f"{type(error).__name__}: {error}"
    st.error(label, icon=":material/error:")
    if tb:
        with st.expander("Traceback"):
            st.code(tb, language="python")
