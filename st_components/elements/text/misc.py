
import streamlit as st

from ...core import Element, Ref
from ..prop_types import BadgeColor, SpaceSize, Width, WidthWithoutContent
from ..factory import widget_child


class divider(Element):
    _slots = {"root": "", "rule": "hr"}
    _default_slot = "rule"

    def __init__(self, *, key: str, ref: Ref | None = None, width: WidthWithoutContent = "stretch"):
        Element.__init__(self, key=key, ref=ref, width=width)

    def render(self):
        st.divider(**self._st_props())


class badge(Element):
    _slots = {"root": "", "badge": "span"}
    _default_slot = "badge"

    def __init__(self, label: str = "", *, key: str, ref: Ref | None = None, icon: str | None = None, color: BadgeColor = "blue", width: Width = "content", help: str | None = None):
        Element.__init__(self, key=key, body=label, ref=ref, icon=icon, color=color, width=width, help=help)

    def render(self):
        st.badge(widget_child("body", ""), **self._st_props("body"))


class space(Element):
    def __init__(self, size: SpaceSize = "small", *, key: str, ref: Ref | None = None):
        Element.__init__(self, key=key, ref=ref, size=size)

    def render(self):
        st.space(self.props.get("size", "small"))
