from typing import Any

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Width
from ..factory import widget_child


class pyplot(Element):
    def __init__(self, fig: Any = None, clear_figure: bool | None = None, *, key: str, ref: Ref | None = None, width: Width = "stretch", use_container_width: bool | None = None, **kwargs: Any):
        Element.__init__(self, key=key, fig=fig, ref=ref, clear_figure=clear_figure, width=width, use_container_width=use_container_width, **kwargs)

    def render(self):
        st.pyplot(widget_child("fig"), **self.props.exclude("key", "children", "fig", "ref"))
