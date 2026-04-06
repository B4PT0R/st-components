from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref, get_element_path
from ...core.access import _get_widget_key
from .._types import HeightWithoutContent, PydeckSelectionMode, SelectionBehavior, WidthWithoutContent
from .._utils import child_or_prop, selection_prop, store_element_value


class pydeck_chart(Element):
    def __init__(self, pydeck_obj: Any = None, *, key: str, ref: Optional[Ref] = None, width: WidthWithoutContent = "stretch", use_container_width: Optional[bool] = None, height: HeightWithoutContent = 500, selection_mode: PydeckSelectionMode = "single-object", on_select: SelectionBehavior = "ignore"):
        Element.__init__(self, key=key, pydeck_obj=pydeck_obj, ref=ref, width=width, use_container_width=use_container_width, height=height, selection_mode=selection_mode, on_select=on_select)

    def render(self):
        pydeck_obj = child_or_prop(self, "pydeck_obj")
        element_path = get_element_path()
        value = st.pydeck_chart(
            pydeck_obj,
            key=_get_widget_key(element_path),
            on_select=selection_prop(self),
            **self.props.exclude("key", "children", "pydeck_obj", "ref", "on_select"),
        )
        store_element_value(element_path, value)
