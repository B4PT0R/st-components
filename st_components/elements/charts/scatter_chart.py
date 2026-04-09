from typing import Any, Optional, Sequence

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Height, Width
from ..factory import widget_child


class scatter_chart(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Optional[Ref] = None, x: Optional[str] = None, y: Optional[str | Sequence[str]] = None, x_label: Optional[str] = None, y_label: Optional[str] = None, color: Optional[Any] = None, size: Optional[str | float | int] = None, width: Width = "stretch", height: Height = "content", use_container_width: Optional[bool] = None):
        Element.__init__(self, key=key, data=data, ref=ref, x=x, y=y, x_label=x_label, y_label=y_label, color=color, size=size, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        st.scatter_chart(widget_child("data"), **self.props.exclude("key", "children", "data", "ref"))
