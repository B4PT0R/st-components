from typing import Any, Iterable

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import Height, SelectionBehavior, Width
from ..factory import widget_child


class altair_chart(Element):
    def __init__(self, altair_chart: Any = None, *, key: str, ref: Ref | None = None, width: Width | None = None, height: Height = "content", use_container_width: bool | None = None, theme: str | None = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: str | Iterable[str] | None = None):
        Element.__init__(self, key=key, altair_chart=altair_chart, ref=ref, width=width, height=height, use_container_width=use_container_width, theme=theme, on_select=on_select, selection_mode=selection_mode)

    def render(self):
        altair_obj = widget_child("altair_chart")
        on_select = self.props.get("on_select", "ignore")
        st.altair_chart(
            altair_obj,
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **self._st_props("altair_chart", "on_select"),
        )
