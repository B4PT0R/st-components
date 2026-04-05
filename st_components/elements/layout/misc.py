from typing import Optional

import streamlit as st

from ...core import Element, Ref, render


class sidebar(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        with st.sidebar:
            for child in self.children:
                render(child)


class empty(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        placeholder = st.empty()
        if self.children:
            with placeholder:
                render(self.children[0])
        return placeholder
