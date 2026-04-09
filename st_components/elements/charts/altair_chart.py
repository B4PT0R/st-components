from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import Height, SelectionBehavior, Width
from ..factory import widget_child


class altair_chart(Element):
    def __init__(self, altair_chart: Any = None, *, key: str, ref: Optional[Ref] = None, width: Optional[Width] = None, height: Height = "content", use_container_width: Optional[bool] = None, theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: Optional[str | Iterable[str]] = None):
        Element.__init__(self, key=key, altair_chart=altair_chart, ref=ref, width=width, height=height, use_container_width=use_container_width, theme=theme, on_select=on_select, selection_mode=selection_mode)

    def render(self):
        altair_obj = widget_child("altair_chart")
        on_select = self.props.get("on_select", "ignore")
        st.altair_chart(
            altair_obj,
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **self.props.exclude("key", "children", "altair_chart", "ref", "on_select"),
        )
