
import streamlit as st

from ...core import Element, Ref, render
from ..factory import render_handle
from ..prop_types import WidthWithoutContent


class balloons(Element):
    def __init__(self, *, key: str, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        st.balloons()


class snow(Element):
    def __init__(self, *, key: str, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref)

    def render(self):
        st.snow()


class spinner(Element):
    def __init__(
        self,
        *children,
        key: str,
        ref: Ref | None = None,
        text: str = "In progress...",
        show_time: bool = False,
        width: WidthWithoutContent = "content",
    ):
        Element.__init__(self, key=key, ref=ref, text=text, show_time=show_time, width=width)
        if children:
            self.children = list(children)

    def render(self):
        handle = st.spinner(
            self.props.text,
            show_time=self.props.show_time,
            width=self.props.width,
        )
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)


class progress(Element):
    def __init__(
        self,
        value=0,
        *,
        key: str,
        ref: Ref | None = None,
        text: str | None = None,
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
