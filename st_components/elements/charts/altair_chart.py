from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref, get_element_path
from ...core.access import _get_widget_key
from .._types import Height, SelectionBehavior, Width
from .._utils import child_or_prop, selection_prop, store_element_value


class altair_chart(Element):
    def __init__(self, altair_chart: Any = None, *, key: str, ref: Optional[Ref] = None, width: Optional[Width] = None, height: Height = "content", use_container_width: Optional[bool] = None, theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: Optional[str | Iterable[str]] = None):
        Element.__init__(self, key=key, altair_chart=altair_chart, ref=ref, width=width, height=height, use_container_width=use_container_width, theme=theme, on_select=on_select, selection_mode=selection_mode)

    def render(self):
        altair_obj = child_or_prop(self, "altair_chart")
        element_path = get_element_path()
        value = st.altair_chart(
            altair_obj,
            key=_get_widget_key(element_path),
            on_select=selection_prop(self),
            **self.props.exclude("key", "children", "altair_chart", "ref", "on_select"),
        )
        store_element_value(element_path, value)
        return value
