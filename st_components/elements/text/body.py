from typing import Any, Literal, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import TextAlignment, Width
from ._common import body_or_prop


class caption(Element):
    def __init__(self, body: Any = "", unsafe_allow_html: bool = False, *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, unsafe_allow_html=unsafe_allow_html, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.caption(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class text(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, width: Width = "content", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.text(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class markdown(Element):
    def __init__(self, body: Any = "", unsafe_allow_html: bool = False, *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, width: Width | Literal["auto"] = "auto", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, unsafe_allow_html=unsafe_allow_html, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.markdown(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class code(Element):
    def __init__(self, body: Any = "", language: Optional[str] = "python", *, key: str, ref: Optional[Ref] = None, line_numbers: bool = False, wrap_lines: bool = False, height: Optional[str | int] = "content", width: Width = "stretch"):
        Element.__init__(self, key=key, body=body, language=language, ref=ref, line_numbers=line_numbers, wrap_lines=wrap_lines, height=height, width=width)

    def render(self):
        st.code(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class latex(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, width: Width = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, help=help, width=width)

    def render(self):
        st.latex(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))
