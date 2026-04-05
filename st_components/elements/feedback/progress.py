from typing import Optional

import streamlit as st

from ...core import Element, Ref, render
from .._types import Width, WidthWithoutContent


class progress(Element):
    def __init__(self, value: int | float = 0, text: Optional[str] = None, width: WidthWithoutContent = "stretch", *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, value=value, ref=ref, text=text, width=width)

    def render(self):
        value = self.children[0] if self.children else self.props.get("value", 0)
        st.progress(value, **self.props.exclude("key", "children", "value", "ref"))


class spinner(Element):
    def __init__(self, text: str = "In progress...", *, key: str, ref: Optional[Ref] = None, show_time: bool = False, _cache: bool = False, width: Width = "content"):
        Element.__init__(self, key=key, text=text, ref=ref, show_time=show_time, _cache=_cache, width=width)

    def render(self):
        with st.spinner(self.props.get("text", "In progress..."), **self.props.exclude("key", "children", "text", "ref")):
            for child in self.children:
                render(child)


class balloons(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        st.balloons()


class snow(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        st.snow()
