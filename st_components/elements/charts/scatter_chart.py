from typing import Any, Sequence

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Height, Width
from ..factory import widget_child


class scatter_chart(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Ref | None = None, x: str | None = None, y: str | Sequence[str] | None = None, x_label: str | None = None, y_label: str | None = None, color: Any | None = None, size: str | float | int | None = None, width: Width = "stretch", height: Height = "content", use_container_width: bool | None = None):
        Element.__init__(self, key=key, data=data, ref=ref, x=x, y=y, x_label=x_label, y_label=y_label, color=color, size=size, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        st.scatter_chart(widget_child("data"), **self.props.exclude("key", "children", "data", "ref"))
