from typing import Any, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import Anchor, Divider, TextAlignment, Width
from ._common import body_or_prop


class title(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, width=width, text_alignment=text_alignment)

    def render(self):
        st.title(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class header(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.header(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class subheader(Element):
    def __init__(self, body: Any = "", anchor: Anchor = None, *, key: str, ref: Optional[Ref] = None, help: Optional[str] = None, divider: Divider = False, width: Width = "stretch", text_alignment: TextAlignment = "left"):
        Element.__init__(self, key=key, body=body, anchor=anchor, ref=ref, help=help, divider=divider, width=width, text_alignment=text_alignment)

    def render(self):
        st.subheader(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))
