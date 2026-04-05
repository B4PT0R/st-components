from typing import Any, Literal, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import IconPosition, Width
from .._utils import child_or_prop


class page_link(Element):
    def __init__(
        self,
        page: Any = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        label: Optional[str] = None,
        icon: Optional[str] = None,
        icon_position: IconPosition = "left",
        help: Optional[str] = None,
        disabled: bool = False,
        use_container_width: Optional[bool] = None,
        width: Width = "content",
        query_params: Optional[Any] = None,
    ):
        Element.__init__(self, key=key, page=page, ref=ref, label=label, icon=icon, icon_position=icon_position, help=help, disabled=disabled, use_container_width=use_container_width, width=width, query_params=query_params)

    def render(self):
        st.page_link(child_or_prop(self, "page"), **self.props.exclude("key", "children", "page", "ref"))


class logo(Element):
    def __init__(self, image: Any = None, *, key: str, ref: Optional[Ref] = None, size: Literal["small", "medium", "large"] = "medium", link: Optional[str] = None, icon_image: Optional[Any] = None):
        Element.__init__(self, key=key, image=image, ref=ref, size=size, link=link, icon_image=icon_image)

    def render(self):
        st.logo(child_or_prop(self, "image"), **self.props.exclude("key", "children", "image", "ref"))
