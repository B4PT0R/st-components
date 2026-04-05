from typing import Any, Optional, Sequence

import streamlit as st

from ...core import Element, Ref
from .._types import Height, Width
from .._utils import child_or_prop


class area_chart(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Optional[Ref] = None, x: Optional[str] = None, y: Optional[str | Sequence[str]] = None, x_label: Optional[str] = None, y_label: Optional[str] = None, color: Optional[Any] = None, stack: Optional[bool | str] = None, width: Width = "stretch", height: Height = "content", use_container_width: Optional[bool] = None):
        Element.__init__(self, key=key, data=data, ref=ref, x=x, y=y, x_label=x_label, y_label=y_label, color=color, stack=stack, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        return st.area_chart(child_or_prop(self, "data"), **self.props.exclude("key", "children", "data", "ref"))
