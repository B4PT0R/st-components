from typing import Optional

import streamlit as st

from ...core import Element, Ref, get_element_path, render, set_element_value


class sidebar(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        set_element_value(get_element_path(), st.sidebar)
        with st.sidebar:
            for child in self.children:
                render(child)


class empty(Element):
    def __init__(self, *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        placeholder = st.empty()
        set_element_value(get_element_path(), placeholder)
        if self.children:
            with placeholder:
                render(self.children[0])
