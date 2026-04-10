from datetime import timedelta
from typing import Any, Literal

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, LabelVisibility, WidgetCallback, WidthWithoutContent
from ..factory import widget_callback, widget_child, widget_props


class text_input(Element):
    def __init__(
        self,
        label: str | None = None,
        value: str | Any | None = "",
        max_chars: int | None = None,
        type: Literal["default", "password"] = "default",
        help: str | None = None,
        autocomplete: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        icon: str | None = None,
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, max_chars=max_chars, ref=ref, type=type, help=help, autocomplete=autocomplete, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, icon=icon, width=width, bind=bind)

    _default_output_prop = "value"

    def render(self):
        st.text_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class number_input(Element):
    def __init__(
        self,
        label: str | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        value: int | float | Literal["min"] | None = "min",
        step: int | float | None = None,
        format: str | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        icon: str | None = None,
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, ref=ref, help=help, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, icon=icon, width=width, bind=bind)

    def render(self):
        st.number_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class text_area(Element):
    def __init__(
        self,
        label: str | None = None,
        value: str | Any | None = "",
        height: int | str | None = None,
        max_chars: int | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, height=height, max_chars=max_chars, ref=ref, help=help, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    _default_output_prop = "value"

    def render(self):
        st.text_area(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))
