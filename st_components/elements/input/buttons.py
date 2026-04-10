from typing import Any, Literal

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import ButtonType, IconPosition, WidgetCallback, Width
from ..factory import widget_callback, widget_child, widget_props


class button(Element):
    def __init__(
        self,
        label: str | None = None,
        help: str | None = None,
        on_click: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        type: ButtonType = "secondary",
        icon: str | None = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: bool | None = None,
        width: Width | None = "content",
        shortcut: str | None = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.button(widget_child("label", ""), key=widget_key(), on_click=widget_callback("on_click"), **widget_props("label", "on_click"))


class download_button(Element):
    def __init__(
        self,
        label: str | None = None,
        data: Any | None = None,
        file_name: str | None = None,
        mime: str | None = None,
        help: str | None = None,
        on_click: WidgetCallback | Literal["rerun", "ignore"] | None = "rerun",
        *,
        key: str,
        ref: Ref | None = None,
        type: ButtonType = "secondary",
        icon: str | None = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: bool | None = None,
        width: Width | None = "content",
        shortcut: str | None = None,
    ):
        Element.__init__(self, key=key, label=label, data=data, ref=ref, file_name=file_name, mime=mime, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.download_button(widget_child("label", ""), key=widget_key(), **self.props.exclude("key", "children", "label", "ref"))


class link_button(Element):
    def __init__(
        self,
        label: str | None = None,
        url: str = "",
        *,
        key: str,
        ref: Ref | None = None,
        on_click: WidgetCallback | Literal["rerun", "ignore"] | None = "ignore",
        help: str | None = None,
        type: ButtonType = "secondary",
        icon: str | None = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: bool | None = None,
        width: Width | None = "content",
        shortcut: str | None = None,
    ):
        Element.__init__(self, key=key, label=label, url=url, ref=ref, on_click=on_click, help=help, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.link_button(widget_child("label", ""), key=widget_key(), **self.props.exclude("key", "children", "label", "ref"))


class form_submit_button(Element):
    def __init__(
        self,
        label: str | None = "Submit",
        help: str | None = None,
        on_click: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        type: ButtonType = "secondary",
        icon: str | None = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: bool | None = None,
        width: Width | None = "content",
        shortcut: str | None = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.form_submit_button(widget_child("label", ""), key=widget_key(), on_click=widget_callback("on_click"), **widget_props("label", "on_click"))


class menu_button(Element):
    def __init__(
        self,
        label: str | None = None,
        options: list[Any] | tuple[Any, ...] | None = (),
        *,
        key: str,
        ref: Ref | None = None,
        help: str | None = None,
        on_click: WidgetCallback | None = None,
        type: ButtonType = "secondary",
        icon: str | None = None,
        disabled: bool = False,
        width: Width | None = "content",
        format_func: Any = str,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, help=help, on_click=on_click, type=type, icon=icon, disabled=disabled, width=width, format_func=format_func)

    def render(self):
        st.menu_button(widget_child("label", ""), key=widget_key(), on_click=widget_callback("on_click"), **widget_props("label", "on_click"))
