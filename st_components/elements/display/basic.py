from typing import Any

import streamlit as st

from ...core import Element, KEY, Ref
from ..prop_types import Height, Width, WidthWithoutContent
from ..factory import widget_child


class write(Element):
    def __init__(self, *children: Any, key: str, ref: Ref | None = None, unsafe_allow_html: bool = False):
        Element.__init__(self, key=key, ref=ref, unsafe_allow_html=unsafe_allow_html)
        if children:
            self.children = list(children)

    def render(self):
        st.write(*self.children, **self.props.exclude("key", "children", "ref"))


class json(Element):
    def __init__(self, body: Any = None, *, key: str, ref: Ref | None = None, expanded: bool | int = True, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, expanded=expanded, width=width)

    def render(self):
        st.json(widget_child("body"), **self.props.exclude("key", "children", "body", "ref"))


class html(Element):
    def __init__(self, body: str = "", *, key: str, ref: Ref | None = None, width: Width = "stretch", unsafe_allow_javascript: bool = False):
        Element.__init__(self, key=key, body=body, ref=ref, width=width, unsafe_allow_javascript=unsafe_allow_javascript)

    def render(self):
        st.html(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))


class iframe(Element):
    def __init__(self, src: Any = None, *, key: str, ref: Ref | None = None, width: int | Width = "stretch", height: int | Height = "content", tab_index: int | None = None):
        Element.__init__(self, key=key, src=src, ref=ref, width=width, height=height, tab_index=tab_index)

    def render(self):
        st.iframe(widget_child("src"), **self.props.exclude("key", "children", "src", "ref"))


class pdf(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Ref | None = None, height: int = 500):
        Element.__init__(self, key=key, data=data, ref=ref, height=height)

    def render(self):
        st.pdf(widget_child("data"), key=KEY("raw"), **self.props.exclude("key", "children", "data", "ref"))


class exception(Element):
    def __init__(self, exception: BaseException | None = None, width: WidthWithoutContent = "stretch", *, key: str, ref: Ref | None = None):
        Element.__init__(self, key=key, exception=exception, ref=ref, width=width)

    def render(self):
        st.exception(widget_child("exception"), **self.props.exclude("key", "children", "exception", "ref"))


class help(Element):
    def __init__(self, obj: Any = st, *, key: str, ref: Ref | None = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, obj=obj, ref=ref, width=width)

    def render(self):
        st.help(widget_child("obj"), **self.props.exclude("key", "children", "obj", "ref"))


class write_stream(Element):
    def __init__(self, stream: Any = None, *, key: str, ref: Ref | None = None, cursor: str | None = None):
        Element.__init__(self, key=key, stream=stream, ref=ref, cursor=cursor)

    def render(self):
        from ...core.access import widget_key
        result = st.write_stream(widget_child("stream"), **self.props.exclude("key", "children", "stream", "ref"))
        st.session_state[widget_key()] = result
