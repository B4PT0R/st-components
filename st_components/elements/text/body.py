from typing import Any, Literal

import streamlit as st

from ...core import Element, Ref
from ..prop_types import TextAlignment, Width
from ..factory import widget_child


class caption(Element):
    _slots = {"root": "", "body": '[data-testid="stMarkdownContainer"]', "text": "p"}
    _default_slot = "text"

    def __init__(self, body: Any = "", unsafe_allow_html: bool = False, *, key: str, ref: Ref | None = None, help: str | None = None, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, unsafe_allow_html=unsafe_allow_html, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.caption(widget_child("body", ""), **self._st_props("body"))


class text(Element):
    _slots = {"root": "", "text": "pre"}
    _default_slot = "text"

    def __init__(self, body: Any = "", *, key: str, ref: Ref | None = None, help: str | None = None, width: Width = "content", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.text(widget_child("body", ""), **self._st_props("body"))


class markdown(Element):
    # Streamlit renders st.markdown as:
    #   .st-key-<scope> > … wrappers … > .stMarkdown > [data-testid="stMarkdownContainer"] > <p>
    # `body` targets the tight wrapper around the rendered content (the most
    # stable hook short of the bare <p>).  Useful when you want a background
    # that hugs the text instead of the full row.
    _slots = {"root": "", "body": '[data-testid="stMarkdownContainer"]', "text": "p"}
    _default_slot = "text"

    def __init__(self, body: Any = "", unsafe_allow_html: bool = False, *, key: str, ref: Ref | None = None, help: str | None = None, width: Width | Literal["auto"] = "auto", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, unsafe_allow_html=unsafe_allow_html, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.markdown(widget_child("body", ""), **self._st_props("body"))


class code(Element):
    _slots = {"root": "", "code": "code", "pre": "pre"}
    _default_slot = "code"

    def __init__(self, body: Any = "", language: str | None = "python", *, key: str, ref: Ref | None = None, line_numbers: bool = False, wrap_lines: bool = False, height: str | int | None = "content", width: Width = "stretch"):
        Element.__init__(self, key=key, body=body, language=language, ref=ref, line_numbers=line_numbers, wrap_lines=wrap_lines, height=height, width=width)

    def render(self):
        st.code(widget_child("body", ""), **self._st_props("body"))


class latex(Element):
    _slots = {"root": "", "body": '[data-testid="stMarkdownContainer"]', "text": "p"}
    _default_slot = "text"

    def __init__(self, body: Any = "", *, key: str, ref: Ref | None = None, help: str | None = None, width: Width = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, help=help, width=width)

    def render(self):
        st.latex(widget_child("body", ""), **self._st_props("body"))
