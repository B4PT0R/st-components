from typing import Any

import streamlit as st

from ...core import Element, Ref
from ..prop_types import Anchor, Divider, TextAlignment, Width
from ..factory import widget_child


class title(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.title(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))


class header(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.header(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))


class subheader(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Ref | None = None, help: str | None = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.subheader(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))
