from typing import Any

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Anchor, Divider, TextAlignment, Width
from ..factory import widget_child


class title(Element):
    _slots = {"root": "", "heading": "h1"}
    _default_slot = "heading"

    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.title(widget_child("body", ""), **self._st_props("body"))


class header(Element):
    _slots = {"root": "", "heading": "h2"}
    _default_slot = "heading"

    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.header(widget_child("body", ""), **self._st_props("body"))


class subheader(Element):
    _slots = {"root": "", "heading": "h3"}
    _default_slot = "heading"

    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.subheader(widget_child("body", ""), **self._st_props("body"))
