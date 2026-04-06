from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import HeightWithoutContent, WidthWithoutContent
from .._utils import child_or_prop


class map(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Optional[Ref] = None, latitude: Optional[str] = None, longitude: Optional[str] = None, color: Optional[Any] = None, size: Optional[str | float] = None, zoom: Optional[int] = None, width: WidthWithoutContent = "stretch", height: HeightWithoutContent = 500, use_container_width: Optional[bool] = None):
        Element.__init__(self, key=key, data=data, ref=ref, latitude=latitude, longitude=longitude, color=color, size=size, zoom=zoom, width=width, height=height, use_container_width=use_container_width)

    def render(self):
        st.map(child_or_prop(self, "data"), **self.props.exclude("key", "children", "data", "ref"))
