from typing import Optional

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, LabelVisibility, WidgetCallback, Width
from ..factory import widget_callback
from ..factory import widget_child,  widget_props


class checkbox(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
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
        Element.__init__(self, key=key, label=label, ref=ref, value=value, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def get_output(self, raw):
        return self.props.get("value") if raw is None else raw

    def render(self):
        st.checkbox(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class toggle(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
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
        Element.__init__(self, key=key, label=label, ref=ref, value=value, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def get_output(self, raw):
        return self.props.get("value") if raw is None else raw

    def render(self):
        st.toggle(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))
