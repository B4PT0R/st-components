from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref, get_element_path
from ...core.access import _get_widget_key
from .._types import Height, PlotlySelectionMode, SelectionBehavior, Width
from .._utils import child_or_prop, selection_prop, store_element_value


class plotly_chart(Element):
    def __init__(self, figure_or_data: Any = None, use_container_width: Optional[bool] = None, *, key: str, ref: Optional[Ref] = None, width: Width = "stretch", height: Height = "content", theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: PlotlySelectionMode | Iterable[PlotlySelectionMode] = ("points", "box", "lasso"), config: Optional[dict[str, Any]] = None, **kwargs: Any):
        Element.__init__(self, key=key, figure_or_data=figure_or_data, ref=ref, use_container_width=use_container_width, width=width, height=height, theme=theme, on_select=on_select, selection_mode=selection_mode, config=config, kwargs=kwargs)

    def render(self):
        figure_or_data = child_or_prop(self, "figure_or_data")
        element_path = get_element_path()
        streamlit_kwargs = dict(self.props.get("kwargs") or {})
        streamlit_kwargs.update(self.props.exclude("key", "children", "figure_or_data", "ref", "on_select", "kwargs"))
        value = st.plotly_chart(
            figure_or_data,
            key=_get_widget_key(element_path),
            on_select=selection_prop(self),
            **streamlit_kwargs,
        )
        store_element_value(element_path, value)
