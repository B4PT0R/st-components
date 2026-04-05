from typing import Any, Literal, Optional, Sequence

import streamlit as st

from ...core import Element, KEY, Ref, render
from .._types import Gap, Height, HorizontalAlignment, VerticalAlignment, Width, WidthWithoutContent


class container(Element):
    def __init__(
        self,
        *,
        key: str,
        ref: Optional[Ref] = None,
        border: Optional[bool] = None,
        width: Width = "stretch",
        height: Height = "content",
        horizontal: bool = False,
        horizontal_alignment: HorizontalAlignment = "left",
        vertical_alignment: VerticalAlignment = "top",
        gap: Gap = "small",
        autoscroll: Optional[bool] = None,
    ):
        Element.__init__(self, key=key, ref=ref, border=border, width=width, height=height, horizontal=horizontal, horizontal_alignment=horizontal_alignment, vertical_alignment=vertical_alignment, gap=gap, autoscroll=autoscroll)

    def render(self):
        with st.container(key=KEY("st_container"), **self.props.exclude("key", "children", "ref")):
            for child in self.children:
                render(child)


class columns(Element):
    def __init__(
        self,
        spec: Any = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
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
        cols = st.columns(spec=spec, **self.props.exclude("key", "children", "spec", "ref"))
        for child, col in zip(self.children, cols):
            with col:
                render(child)


class tabs(Element):
    def __init__(
        self,
        tabs: Optional[Sequence[str]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        width: WidthWithoutContent = "stretch",
        default: Optional[str] = None,
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ):
        Element.__init__(self, key=key, ref=ref, tabs=tabs, width=width, default=default, on_change=on_change, args=args, kwargs=kwargs)

    def render(self):
        labels = self.props.get("tabs", self.props.get("labels", [str(i) for i in range(len(self.children))]))
        tab_objs = st.tabs(labels, **self.props.exclude("key", "children", "tabs", "labels", "ref"))
        for child, tab_obj in zip(self.children, tab_objs):
            with tab_obj:
                render(child)


class form(Element):
    def __init__(
        self,
        clear_on_submit: bool = False,
        *,
        key: str,
        ref: Optional[Ref] = None,
        enter_to_submit: bool = True,
        border: bool = True,
        width: Width = "stretch",
        height: Height = "content",
    ):
        Element.__init__(self, key=key, ref=ref, clear_on_submit=clear_on_submit, enter_to_submit=enter_to_submit, border=border, width=width, height=height)

    def render(self):
        with st.form(KEY("st_form"), **self.props.exclude("key", "children", "ref")):
            for child in self.children:
                render(child)


class expander(Element):
    def __init__(
        self,
        label: str = "",
        expanded: bool = False,
        *,
        key: str,
        ref: Optional[Ref] = None,
        icon: Optional[str] = None,
        width: WidthWithoutContent = "stretch",
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, expanded=expanded, icon=icon, width=width, on_change=on_change, args=args, kwargs=kwargs)

    def render(self):
        with st.expander(**self.props.exclude("key", "children", "ref")):
            for child in self.children:
                render(child)


class popover(Element):
    def __init__(
        self,
        label: str = "",
        *,
        key: str,
        ref: Optional[Ref] = None,
        type: Literal["primary", "secondary", "tertiary"] = "secondary",
        help: Optional[str] = None,
        icon: Optional[str] = None,
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Width = "content",
        on_change: Literal["ignore", "rerun"] | Any = "ignore",
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, type=type, help=help, icon=icon, disabled=disabled, use_container_width=use_container_width, width=width, on_change=on_change, args=args, kwargs=kwargs)

    def render(self):
        with st.popover(**self.props.exclude("key", "children", "ref")):
            for child in self.children:
                render(child)
