from typing import Optional

import streamlit as st

from ...core import Element, Ref, render
from ..prop_types import WidthWithoutContent


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


class spinner(Element):
    def __init__(
        self,
        *children,
        key: str,
        ref: Optional[Ref] = None,
        text: str = "In progress...",
        show_time: bool = False,
        width: WidthWithoutContent = "content",
    ):
        Element.__init__(self, key=key, ref=ref, text=text, show_time=show_time, width=width)
        if children:
            self.children = list(children)

    def render(self):
        with st.spinner(
            self.props.text,
            show_time=self.props.show_time,
            width=self.props.width,
        ):
            for child in self.children:
                render(child)


class progress(Element):
    def __init__(
        self,
        value=0,
        *,
        key: str,
        ref: Optional[Ref] = None,
        text: Optional[str] = None,
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, ref=ref, value=value, text=text, width=width)

    def render(self):
        handle = st.progress(
            self.props.value,
            text=self.props.text,
            width=self.props.width,
        )
        self.state.handle = handle
