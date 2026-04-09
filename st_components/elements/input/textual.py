from datetime import timedelta
from typing import Any, Literal, Optional

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, LabelVisibility, WidgetCallback, WidthWithoutContent
from ..factory import widget_callback
from ..factory import widget_child,  widget_props


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

    def get_output(self, raw):
        return self.props.get("value") if raw is None else raw

    def render(self):
        st.text_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


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
        st.number_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


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

    def get_output(self, raw):
        return self.props.get("value") if raw is None else raw

    def render(self):
        st.text_area(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))
