from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import HeightWithoutContent, PydeckSelectionMode, SelectionBehavior, WidthWithoutContent
from ..factory import widget_child


class pydeck_chart(Element):
    def __init__(self, pydeck_obj: Any = None, *, key: str, ref: Optional[Ref] = None, width: WidthWithoutContent = "stretch", use_container_width: Optional[bool] = None, height: HeightWithoutContent = 500, selection_mode: PydeckSelectionMode = "single-object", on_select: SelectionBehavior = "ignore"):
        Element.__init__(self, key=key, pydeck_obj=pydeck_obj, ref=ref, width=width, use_container_width=use_container_width, height=height, selection_mode=selection_mode, on_select=on_select)

    def render(self):
        pydeck_obj = widget_child("pydeck_obj")
        on_select = self.props.get("on_select", "ignore")
        st.pydeck_chart(
            pydeck_obj,
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **self.props.exclude("key", "children", "pydeck_obj", "ref", "on_select"),
        )
