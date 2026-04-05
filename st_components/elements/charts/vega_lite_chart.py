from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref, get_element_path
from ...core.access import _get_widget_key
from .._types import Height, SelectionBehavior, Width
from .._utils import child_or_prop, selection_prop, store_element_value


class vega_lite_chart(Element):
    def __init__(self, data: Any = None, spec: Optional[Any] = None, *, key: str, ref: Optional[Ref] = None, width: Optional[Width] = None, height: Height = "content", use_container_width: Optional[bool] = None, theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: Optional[str | Iterable[str]] = None, **kwargs: Any):
        Element.__init__(self, key=key, data=data, spec=spec, ref=ref, width=width, height=height, use_container_width=use_container_width, theme=theme, on_select=on_select, selection_mode=selection_mode, kwargs=kwargs)

    def render(self):
        data = child_or_prop(self, "data")
        element_path = get_element_path()
        streamlit_kwargs = dict(self.props.get("kwargs") or {})
        streamlit_kwargs.update(self.props.exclude("key", "children", "data", "ref", "on_select", "kwargs"))
        value = st.vega_lite_chart(
            data,
            key=_get_widget_key(element_path),
            on_select=selection_prop(self),
            **streamlit_kwargs,
        )
        store_element_value(element_path, value)
        return value
