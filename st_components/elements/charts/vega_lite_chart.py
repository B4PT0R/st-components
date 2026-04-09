from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import Height, SelectionBehavior, Width
from ..factory import widget_child


class vega_lite_chart(Element):
    def __init__(self, data: Any = None, spec: Optional[Any] = None, *, key: str, ref: Optional[Ref] = None, width: Optional[Width] = None, height: Height = "content", use_container_width: Optional[bool] = None, theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: Optional[str | Iterable[str]] = None, **kwargs: Any):
        Element.__init__(self, key=key, data=data, spec=spec, ref=ref, width=width, height=height, use_container_width=use_container_width, theme=theme, on_select=on_select, selection_mode=selection_mode, kwargs=kwargs)

    def render(self):
        data = widget_child("data")
        streamlit_kwargs = dict(self.props.get("kwargs") or {})
        streamlit_kwargs.update(self.props.exclude("key", "children", "data", "ref", "on_select", "kwargs"))
        on_select = self.props.get("on_select", "ignore")
        st.vega_lite_chart(
            data,
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **streamlit_kwargs,
        )
