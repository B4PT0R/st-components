from typing import Any, Literal

import streamlit as st

from ...core import Element, Ref
from ..prop_types import WidthWithoutContent
from ..factory import widget_child


def _message_element(st_func):
    """Generate a simple feedback Element that delegates to *st_func*."""
    class cls(Element):
        def __init__(self, body: Any = "", *, key: str, ref: Ref | None = None, icon: str | None = None, width: WidthWithoutContent = "stretch"):
            Element.__init__(self, key=key, body=body, ref=ref, icon=icon, width=width)

        def render(self):
            st_func(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))

    cls.__name__ = cls.__qualname__ = getattr(st_func, "__name__", "message")
    return cls


success = _message_element(st.success)
info = _message_element(st.info)
warning = _message_element(st.warning)
error = _message_element(st.error)


class toast(Element):
    def __init__(self, body: Any = "", *, key: str, ref: Ref | None = None, icon: str | None = None, duration: Literal["short", "long", "infinite"] | int = "short"):
        Element.__init__(self, key=key, body=body, ref=ref, icon=icon, duration=duration)

    def render(self):
        st.toast(widget_child("body", ""), **self.props.exclude("key", "children", "body", "ref"))
