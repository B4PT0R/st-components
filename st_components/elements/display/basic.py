from typing import Any, Optional

import streamlit as st

from ...core import Element, KEY, Ref, get_element_path, set_element_value
from .._types import Height, Width, WidthWithoutContent
from .._utils import child_or_prop


class write(Element):
    def __init__(self, *children: Any, key: str, ref: Optional[Ref] = None, unsafe_allow_html: bool = False):
        Element.__init__(self, key=key, ref=ref, unsafe_allow_html=unsafe_allow_html)
        if children:
            self.children = list(children)

    def render(self):
        st.write(*self.children, **self.props.exclude("key", "children", "ref"))


class json(Element):
    def __init__(self, body: Any = None, *, key: str, ref: Optional[Ref] = None, expanded: bool | int = True, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, expanded=expanded, width=width)

    def render(self):
        st.json(child_or_prop(self, "body"), **self.props.exclude("key", "children", "body", "ref"))


class html(Element):
    def __init__(self, body: str = "", *, key: str, ref: Optional[Ref] = None, width: Width = "stretch", unsafe_allow_javascript: bool = False):
        Element.__init__(self, key=key, body=body, ref=ref, width=width, unsafe_allow_javascript=unsafe_allow_javascript)

    def render(self):
        st.html(child_or_prop(self, "body", ""), **self.props.exclude("key", "children", "body", "ref"))


class iframe(Element):
    def __init__(self, src: Any = None, *, key: str, ref: Optional[Ref] = None, width: int | Width = "stretch", height: int | Height = "content", tab_index: Optional[int] = None):
        Element.__init__(self, key=key, src=src, ref=ref, width=width, height=height, tab_index=tab_index)

    def render(self):
        st.iframe(child_or_prop(self, "src"), **self.props.exclude("key", "children", "src", "ref"))


class pdf(Element):
    def __init__(self, data: Any = None, *, key: str, ref: Optional[Ref] = None, height: int = 500):
        Element.__init__(self, key=key, data=data, ref=ref, height=height)

    def render(self):
        st.pdf(child_or_prop(self, "data"), key=KEY("st_pdf"), **self.props.exclude("key", "children", "data", "ref"))


class exception(Element):
    def __init__(self, exception: Optional[BaseException] = None, width: WidthWithoutContent = "stretch", *, key: str, ref: Optional[Ref] = None):
        Element.__init__(self, key=key, exception=exception, ref=ref, width=width)

    def render(self):
        st.exception(child_or_prop(self, "exception"), **self.props.exclude("key", "children", "exception", "ref"))


class help(Element):
    def __init__(self, obj: Any = st, *, key: str, ref: Optional[Ref] = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, obj=obj, ref=ref, width=width)

    def render(self):
        st.help(child_or_prop(self, "obj"), **self.props.exclude("key", "children", "obj", "ref"))


class write_stream(Element):
    def __init__(self, stream: Any = None, *, key: str, ref: Optional[Ref] = None, cursor: Optional[str] = None):
        Element.__init__(self, key=key, stream=stream, ref=ref, cursor=cursor)

    def render(self):
        result = st.write_stream(child_or_prop(self, "stream"), **self.props.exclude("key", "children", "stream", "ref"))
        set_element_value(get_element_path(), result)
        return result
