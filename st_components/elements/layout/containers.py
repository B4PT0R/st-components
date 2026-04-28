from typing import Any, Literal, Sequence

import streamlit as st

from ...core import Element, KEY, Ref, render, set_context
from ..factory import render_handle
from ..prop_types import Gap, Height, HorizontalAlignment, VerticalAlignment, Width, WidthWithoutContent


class column(Element):
    """Explicit child of :class:`columns` — gives you control over the key.

    When passed as a child of ``columns``, the column's own key is used
    instead of the auto-generated ``col_0``, ``col_1``, etc.::

        columns(key="grid")(
            column(key="filters")(FilterPanel(key="f")),
            column(key="data")(DataTable(key="t")),
        )
    """

    def __init__(self, *, key: str | None = None, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref)

    def _render_in_handle(self, col_handle, parent_path):
        """Called by the parent ``columns`` element."""
        col_path = f"{parent_path}.{self.key}"
        with self.state._writable():
            self.state.handle = col_handle
        with set_context(key=self.key):
            with render_handle(col_handle, col_path):
                for child in self.children:
                    render(child)

    def render(self):
        # Standalone render (shouldn't happen normally — columns calls _render_in_handle)
        for child in self.children:
            render(child)


class tab(Element):
    """Explicit child of :class:`tabs` — gives you control over the key.

    ::

        tabs(key="sections")(
            tab(key="overview")(OverviewPanel(key="p")),
            tab(key="details")(DetailsPanel(key="p")),
        )
    """

    def __init__(self, *, key: str | None = None, ref: Ref | None = None, label: str | None = None):
        Element.__init__(self, key=key, ref=ref, label=label)

    def _render_in_handle(self, tab_handle, parent_path):
        """Called by the parent ``tabs`` element."""
        tab_path = f"{parent_path}.{self.key}"
        with self.state._writable():
            self.state.handle = tab_handle
        with set_context(key=self.key):
            with render_handle(tab_handle, tab_path):
                for child in self.children:
                    render(child)

    def render(self):
        for child in self.children:
            render(child)


class container(Element):
    def __init__(
        self,
        *,
        key: str | None = None,
        ref: Ref | None = None,
        border: bool | None = None,
        width: Width = "stretch",
        height: Height = "content",
        horizontal: bool = False,
        horizontal_alignment: HorizontalAlignment = "left",
        vertical_alignment: VerticalAlignment = "top",
        gap: Gap = "small",
        autoscroll: bool | None = None,
    ):
        Element.__init__(self, key=key, ref=ref, border=border, width=width, height=height, horizontal=horizontal, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, gap=gap, autoscroll=autoscroll)

    def render(self):
        handle = st.container(key=KEY("raw"), **self._st_props())
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)


class columns(Element):
    def __init__(
        self,
        spec: Any = None,
        *,
        key: str | None = None,
        ref: Ref | None = None,
        gap: Gap = "small",
        vertical_alignment: Literal["top", "center", "bottom"] = "top",
        border: bool = False,
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, ref=ref, spec=spec, gap=gap, vertical_alignment=vertical_alignment, border=border, width=width)

    def render(self):
        spec = self.props.get("spec")
        if spec is None:
            spec = len(self.children)
        cols = st.columns(spec=spec, **self._st_props("spec"))
        self.state.handle = cols
        for i, (child, col_handle) in enumerate(zip(self.children, cols)):
            if isinstance(child, column):
                child._render_in_handle(col_handle, self._fiber_key)
            else:
                col_path = f"{self._fiber_key}.col_{i}"
                with set_context(key=f"col_{i}"):
                    with render_handle(col_handle, col_path):
                        render(child)


class tabs(Element):
    def __init__(
        self,
        tabs: Sequence[str] | None = None,
        *,
        key: str | None = None,
        ref: Ref | None = None,
        width: WidthWithoutContent = "stretch",
        default: str | None = None,
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
    ):
        Element.__init__(self, key=key, ref=ref, tabs=tabs, width=width, default=default, on_change=on_change)

    def render(self):
        children = self.children
        # Derive labels from tab children if they have a label prop
        has_tab_children = children and isinstance(children[0], tab)
        if has_tab_children:
            labels = [c.props.get("label") or str(i) for i, c in enumerate(children)]
        else:
            labels = self.props.get("tabs", self.props.get("labels", [str(i) for i in range(len(children))]))
        tab_objs = st.tabs(labels, **self._st_props("tabs", "labels"))
        self.state.handle = tab_objs
        for i, (child, tab_handle) in enumerate(zip(children, tab_objs)):
            if isinstance(child, tab):
                child._render_in_handle(tab_handle, self._fiber_key)
            else:
                tab_path = f"{self._fiber_key}.tab_{i}"
                with set_context(key=f"tab_{i}"):
                    with render_handle(tab_handle, tab_path):
                        render(child)


class form(Element):
    _slots = {"root": ""}
    _default_slot = "root"

    def __init__(
        self,
        clear_on_submit: bool = False,
        *,
        key: str | None = None,
        ref: Ref | None = None,
        enter_to_submit: bool = True,
        border: bool = True,
        width: Width = "stretch",
        height: Height = "content",
    ):
        Element.__init__(self, key=key, ref=ref, clear_on_submit=clear_on_submit, enter_to_submit=enter_to_submit, border=border, width=width, height=height)

    def render(self):
        handle = st.form(KEY("raw"), **self._st_props())
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)


class expander(Element):
    _slots = {"root": "", "header": "summary", "body": "details > div"}
    _default_slot = "root"

    def __init__(
        self,
        label: str = "",
        expanded: bool = False,
        *,
        key: str | None = None,
        ref: Ref | None = None,
        icon: str | None = None,
        width: WidthWithoutContent = "stretch",
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, expanded=expanded, icon=icon, width=width, on_change=on_change)

    def render(self):
        handle = st.expander(**self._st_props())
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)


class popover(Element):
    _slots = {"root": "", "trigger": "button", "label": "button p"}
    _default_slot = "root"

    def __init__(
        self,
        label: str = "",
        *,
        key: str | None = None,
        ref: Ref | None = None,
        type: Literal["primary", "secondary", "tertiary"] = "secondary",
        help: str | None = None,
        icon: str | None = None,
        disabled: bool = False,
        use_container_width: bool | None = None,
        width: Width = "content",
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, type=type, help=help, icon=icon, disabled=disabled, use_container_width=use_container_width, width=width, on_change=on_change)

    def render(self):
        handle = st.popover(**self._st_props())
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)
