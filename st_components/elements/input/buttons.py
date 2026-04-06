from typing import Any, Literal, Optional

from ...core import Element, Ref
from ...core.access import _get_widget_key
from ._common import ButtonType, IconPosition, WidgetCallback, Width, label_or_prop, st, widget_callback, widget_props


class button(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        help: Optional[str] = None,
        on_click: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        type: ButtonType = "secondary",
        icon: Optional[str] = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Optional[Width] = "content",
        shortcut: Optional[str] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.button(label_or_prop(self), key=_get_widget_key(), on_click=widget_callback(self, "on_click"), **widget_props(self, "on_click"))


class download_button(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        data: Optional[Any] = None,
        file_name: Optional[str] = None,
        mime: Optional[str] = None,
        help: Optional[str] = None,
        on_click: Optional[WidgetCallback | Literal["rerun", "ignore"]] = "rerun",
        *,
        key: str,
        ref: Optional[Ref] = None,
        type: ButtonType = "secondary",
        icon: Optional[str] = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Optional[Width] = "content",
        shortcut: Optional[str] = None,
    ):
        Element.__init__(self, key=key, label=label, data=data, ref=ref, file_name=file_name, mime=mime, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.download_button(label_or_prop(self), key=_get_widget_key(), **self.props.exclude("key", "children", "label", "ref"))


class link_button(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        url: str = "",
        *,
        key: str,
        ref: Optional[Ref] = None,
        on_click: Optional[WidgetCallback | Literal["rerun", "ignore"]] = "ignore",
        help: Optional[str] = None,
        type: ButtonType = "secondary",
        icon: Optional[str] = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Optional[Width] = "content",
        shortcut: Optional[str] = None,
    ):
        Element.__init__(self, key=key, label=label, url=url, ref=ref, on_click=on_click, help=help, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.link_button(label_or_prop(self), key=_get_widget_key(), **self.props.exclude("key", "children", "label", "ref"))


class form_submit_button(Element):
    def __init__(
        self,
        label: Optional[str] = "Submit",
        help: Optional[str] = None,
        on_click: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        type: ButtonType = "secondary",
        icon: Optional[str] = None,
        icon_position: IconPosition = "left",
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Optional[Width] = "content",
        shortcut: Optional[str] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_click=on_click, type=type, icon=icon, icon_position=icon_position, disabled=disabled, use_container_width=use_container_width, width=width, shortcut=shortcut)

    def render(self):
        st.form_submit_button(label_or_prop(self), key=_get_widget_key(), on_click=widget_callback(self, "on_click"), **widget_props(self, "on_click"))


class menu_button(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[list[Any] | tuple[Any, ...]] = (),
        *,
        key: str,
        ref: Optional[Ref] = None,
        help: Optional[str] = None,
        on_click: Optional[WidgetCallback] = None,
        type: ButtonType = "secondary",
        icon: Optional[str] = None,
        disabled: bool = False,
        width: Optional[Width] = "content",
        format_func: Any = str,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, help=help, on_click=on_click, type=type, icon=icon, disabled=disabled, width=width, format_func=format_func)

    def render(self):
        st.menu_button(label_or_prop(self), key=_get_widget_key(), on_click=widget_callback(self, "on_click", pass_value=True), **widget_props(self, "on_click"))
