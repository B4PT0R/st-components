from datetime import timedelta
from typing import Any, Literal, Optional

from ...core import Element, Ref
from ...core.access import _get_widget_key
from ._common import BindOption, LabelVisibility, WidgetCallback, WidthWithoutContent, label_or_prop, st, widget_callback, widget_props


class text_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Optional[str | Any] = "",
        max_chars: Optional[int] = None,
        type: Literal["default", "password"] = "default",
        help: Optional[str] = None,
        autocomplete: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        placeholder: Optional[str] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        icon: Optional[str] = None,
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, max_chars=max_chars, ref=ref, type=type, help=help, autocomplete=autocomplete, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, icon=icon, width=width, bind=bind)

    def render(self):
        st.text_input(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class number_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        min_value: Optional[int | float] = None,
        max_value: Optional[int | float] = None,
        value: Optional[int | float | Literal["min"]] = "min",
        step: Optional[int | float] = None,
        format: Optional[str] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        placeholder: Optional[str] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        icon: Optional[str] = None,
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, ref=ref, help=help, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, icon=icon, width=width, bind=bind)

    def render(self):
        st.number_input(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class text_area(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Optional[str | Any] = "",
        height: Optional[int | str] = None,
        max_chars: Optional[int] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        placeholder: Optional[str] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, height=height, max_chars=max_chars, ref=ref, help=help, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.text_area(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))
