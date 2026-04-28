from datetime import date, time, timedelta
from typing import Any

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, LabelVisibility, WidgetCallback, Width, WidthWithoutContent
from ..factory import widget_callback, widget_child, widget_props


class date_input(Element):
    _slots = {"root": "", "input": '[data-baseweb="input"]', "label": "label"}
    _default_slot = "input"

    def __init__(
        self,
        label: str | None = None,
        value: Any = "today",
        min_value: date | Any | None = None,
        max_value: date | Any | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        format: str = "YYYY/MM/DD",
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, min_value=min_value, max_value=max_value, ref=ref, help=help, on_change=on_change, format=format, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.date_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class time_input(Element):
    _slots = {"root": "", "input": '[data-baseweb="input"]', "label": "label"}
    _default_slot = "input"

    def __init__(
        self,
        label: str | None = None,
        value: time | str | None = "now",
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        step: int | timedelta = timedelta(seconds=900),
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, step=step, width=width, bind=bind)

    def render(self):
        st.time_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class color_picker(Element):
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        value: str | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Width | None = "content",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.color_picker(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class datetime_input(Element):
    _slots = {"root": "", "input": '[data-baseweb="input"]', "label": "label"}
    _default_slot = "input"

    def __init__(
        self,
        label: str | None = None,
        value: Any = "now",
        min_value: Any | None = None,
        max_value: Any | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        format: str = "YYYY/MM/DD",
        step: int | timedelta = timedelta(seconds=900),
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, value=value, min_value=min_value, max_value=max_value, ref=ref, help=help, on_change=on_change, format=format, step=step, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.datetime_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))
