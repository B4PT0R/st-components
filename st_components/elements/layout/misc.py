
import streamlit as st

from ...core import Element, Ref, render
from ..factory import render_handle


class sidebar(Element):
    def __init__(self, *, key: str | None = None, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        self.state.handle = st.sidebar
        with render_handle(st.sidebar, self._fiber_key):
            for child in self.children:
                render(child)


class empty(Element):
    def __init__(self, *, key: str | None = None, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        placeholder = st.empty()
        self.state.handle = placeholder
        if self.children:
            with render_handle(placeholder, self._fiber_key):
                render(self.children[0])
