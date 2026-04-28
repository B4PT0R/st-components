from typing import Any

import streamlit as st

from ...core import Element, Ref
from ..prop_types import HeightWithoutContent, WidthWithoutContent
from ..factory import widget_child


class map(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Ref | None = None, latitude: str | None = None, longitude: str | None = None, color: Any | None = None, size: str | float | None = None, zoom: int | None = None, width: WidthWithoutContent = "stretch", height: HeightWithoutContent = 500, use_container_width: bool | None = None):
        Element.__init__(self, key=key, data=data, ref=ref, latitude=latitude, longitude=longitude, color=color, size=size, zoom=zoom, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        st.map(widget_child("data"), **self._st_props("data"))
