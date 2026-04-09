from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Height, Width
from ..factory import widget_child


class graphviz_chart(Element):
    def __init__(self, figure_or_dot: Any = None, use_container_width: Optional[bool] = None, *, key: str, ref: Optional[Ref] = None, width: Width = "content", height: Height = "content"):
        Element.__init__(self, key=key, figure_or_dot=figure_or_dot, ref=ref, use_container_width=use_container_width, width=width, height=height)

    def render(self):
        st.graphviz_chart(widget_child("figure_or_dot"), **self.props.exclude("key", "children", "figure_or_dot", "ref"))
