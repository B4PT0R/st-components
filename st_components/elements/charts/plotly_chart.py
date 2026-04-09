from typing import Any, Iterable, Optional

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import Height, PlotlySelectionMode, SelectionBehavior, Width
from ..factory import widget_child


class plotly_chart(Element):
    def __init__(self, figure_or_data: Any = None, use_container_width: Optional[bool] = None, *, key: str, ref: Optional[Ref] = None, width: Width = "stretch", height: Height = "content", theme: Optional[str] = "streamlit", on_select: SelectionBehavior = "ignore", selection_mode: PlotlySelectionMode | Iterable[PlotlySelectionMode] = ("points", "box", "lasso"), config: Optional[dict[str, Any]] = None, **kwargs: Any):
        Element.__init__(self, key=key, figure_or_data=figure_or_data, ref=ref, use_container_width=use_container_width, width=width, height=height, theme=theme, on_select=on_select, selection_mode=selection_mode, config=config, kwargs=kwargs)

    def render(self):
        figure_or_data = widget_child("figure_or_data")
        on_select = self.props.get("on_select", "ignore")
        streamlit_kwargs = dict(self.props.get("kwargs") or {})
        streamlit_kwargs.update(self.props.exclude("key", "children", "figure_or_data", "ref", "on_select", "kwargs"))
        st.plotly_chart(
            figure_or_data,
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **streamlit_kwargs,
        )
