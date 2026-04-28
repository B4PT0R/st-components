from typing import Any, Sequence

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Height, Width
from ..factory import widget_child


class bar_chart(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Ref | None = None, x: str | None = None, y: str | Sequence[str] | None = None, x_label: str | None = None, y_label: str | None = None, color: Any | None = None, horizontal: bool = False, sort: bool | str = True, stack: bool | str | None = None, width: Width = "stretch", height: Height = "content", use_container_width: bool | None = None):
        Element.__init__(self, key=key, data=data, ref=ref, x=x, y=y, x_label=x_label, y_label=y_label, color=color, horizontal=horizontal, sort=sort, stack=stack, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        st.bar_chart(widget_child("data"), **self._st_props("data"))
