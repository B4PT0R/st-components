from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from .._utils import child_or_prop


class bokeh_chart(Element):
    def __init__(self, figure: Any = None, use_container_width: bool = True, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, figure=figure, ref=ref, use_container_width=use_container_width)

    def render(self):
        st.bokeh_chart(child_or_prop(self, "figure"), **self.props.exclude("key", "children", "figure", "ref"))
