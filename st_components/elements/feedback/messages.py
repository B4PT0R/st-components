from typing import Any, Literal, Optional

import streamlit as st

from ...core import Element, Ref
from ..prop_types import WidthWithoutContent


def body_or_prop(element):
    return element.children[0] if element.children else element.props.get("body", "")


class success(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, icon: Optional[str] = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, width=width)

    def render(self):
        st.success(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class info(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, icon: Optional[str] = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, width=width)

    def render(self):
        st.info(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class warning(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, icon: Optional[str] = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, width=width)

    def render(self):
        st.warning(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class error(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, icon: Optional[str] = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, width=width)

    def render(self):
        st.error(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))


class toast(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Optional[Ref] = None, icon: Optional[str] = None, duration: Literal["short", "long", "infinite"] | int = "short"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, duration=duration)

    def render(self):
        st.toast(body_or_prop(self), **self.props.exclude("key", "children", "body", "ref"))
