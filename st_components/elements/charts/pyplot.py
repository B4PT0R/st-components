from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import Width
from .._utils import child_or_prop


class pyplot(Element):
    def __init__(self, fig: Any = None, clear_figure: Optional[bool] = None, *, key: str, ref: Optional[Ref] = None, width: Width = "stretch", use_container_width: Optional[bool] = None, **kwargs: Any):
        Element.__init__(self, key=key, fig=fig, ref=ref, clear_figure=clear_figure, width=width, use_container_width=use_container_width, **kwargs)

    def render(self):
        return st.pyplot(child_or_prop(self, "fig"), **self.props.exclude("key", "children", "fig", "ref"))
