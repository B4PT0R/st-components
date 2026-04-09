from datetime import date, time, timedelta
from typing import Any, Optional

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, LabelVisibility, WidgetCallback, Width, WidthWithoutContent
from ..factory import widget_callback
from ..factory import widget_child, widget_props


class date_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Any = "today",
        min_value: Optional[date | Any] = None,
        max_value: Optional[date | Any] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        format: str = "YYYY/MM/DD",
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, min_value=min_value, max_value=max_value, ref=ref, help=help, on_change=on_change, format=format, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.date_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class time_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Optional[time | str] = "now",
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        step: int | timedelta = timedelta(seconds=900),
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, step=step, width=width, bind=bind)

    def render(self):
        st.time_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class color_picker(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Optional[str] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.color_picker(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class datetime_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: Any = "now",
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        format: str = "YYYY/MM/DD",
        step: int | timedelta = timedelta(seconds=900),
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, min_value=min_value, max_value=max_value, ref=ref, help=help, on_change=on_change, format=format, step=step, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.datetime_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))
