"""
Fragment element — grouping with optional scoped re-rendering.

Transparent by default (like React Fragment).  When ``scoped=True``,
wraps children in ``st.fragment()`` for independent re-rendering.

Supports fiber overrides via ``self.ref.path(children)`` from callbacks.
"""
import streamlit as st

from ...core.base import Element, _auto_key_children, render as render_child
from ...core.context import KEY, get_key_stack, set_context
from ...core.models import ElementFiber
from ...core.refs import bind_ref
from ...core.store import fibers, register_component, track_rendered_fiber


class fragment(Element):
    """Group children, optionally inside a Streamlit fragment.

    ::

        fragment(key="grp")(child_a, child_b)                    # transparent
        fragment(key="live", scoped=True, run_every="2s")(chart)  # scoped
    """

    def __init__(
        self,
        *,
        key: str | None = None,
        scoped: bool = False,
        run_every: str | int | float | None = None,
    ):
        Element.__init__(self, key=key, scoped=scoped, run_every=run_every)

    def _render_decorator(self, render_func):
        """Custom decorator: creates a fiber (for overrides) + wraps in st.fragment if scoped."""

        def decorated():
            from ...core.access import widget_key

            _auto_key_children([self])
            element_path = KEY(self.key)
            self._fiber_key = element_path
            bind_ref(self, element_path, "element")

            if not self.is_mounted:
                self.mount()
            else:
                self.fiber.widget_key = widget_key(element_path)

            self._apply_overrides()
            track_rendered_fiber(element_path)

            if not self.props.get("scoped"):
                # Transparent — render children directly
                with set_context(key=self.key, component=self):
                    render_func()
                return

            # Scoped — wrap in st.fragment for independent reruns
            parent_keys = get_key_stack()
            run_every = self.props.get("run_every")
            scope_id = f"{element_path}"

            def run_scoped():
                with set_context(keys=parent_keys, key=self.key,
                                 component=self, rerun_scope=scope_id):
                    render_func()
                    from ...core.rerun import check_rerun
                    check_rerun(scope=scope_id)

            st.fragment(run_every=run_every)(run_scoped)()

        decorated._decorated = True
        return decorated

    def render(self):
        for child in self.children:
            render_child(child)
