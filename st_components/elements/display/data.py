from typing import Any, Iterable, Literal

import streamlit as st

from ...core import Element, Ref
from ...core.access import callback, widget_key
from ..prop_types import DataSelectionMode, DeltaArrow, Height, LabelVisibility, Width, WidthWithoutContent
from ..factory import widget_child


class dataframe(Element):
    _slots = {"root": ""}
    _default_slot = "root"

    def __init__(
        self,
        data: Any = None,
        width: Width = "stretch",
        height: int | str = "auto",
        *,
        key: str,
        ref: Ref | None = None,
        use_container_width: bool | None = None,
        hide_index: bool | None = None,
        column_order: Iterable[str] | None = None,
        column_config: Any | None = None,
        on_select: Literal["ignore", "rerun"] | Any = "ignore",
        selection_mode: DataSelectionMode | Iterable[DataSelectionMode] = "multi-row",
        selection_default: Any | None = None,
        row_height: int | None = None,
        placeholder: str | None = None,
    ):
        Element.__init__(self, key=key, ref=ref, data=data, width=width, height=height, use_container_width=use_container_width, hide_index=hide_index, column_order=column_order, column_config=column_config, on_select=on_select, selection_mode=selection_mode, selection_default=selection_default, row_height=row_height, placeholder=placeholder)

    def render(self):
        on_select = self.props.get("on_select", "ignore")
        st.dataframe(
            widget_child("data"),
            key=widget_key(),
            on_select=callback(on_select) if callable(on_select) else on_select,
            **self._st_props("data", "on_select"),
        )


class table(Element):
    _slots = {"root": "", "table": "table"}
    _default_slot = "root"

    def __init__(
        self,
        data: Any = None,
        *,
        key: str,
        ref: Ref | None = None,
        border: bool | Literal["horizontal"] = True,
        width: Width = "stretch",
        height: Height = "content",
        hide_index: bool | None = None,
        hide_header: bool | None = None,
    ):
        Element.__init__(self, key=key, ref=ref, data=data, border=border, width=width, height=height, hide_index=hide_index, hide_header=hide_header)

    def render(self):
        st.table(widget_child("data"), **self._st_props("data"))


class metric(Element):
    _slots = {
        "root": "",
        "label": '[data-testid="stMetricLabel"]',
        "value": '[data-testid="stMetricValue"]',
        "delta": '[data-testid="stMetricDelta"]',
    }
    _default_slot = "root"

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        delta: Any = None,
        delta_color: Literal["normal", "inverse", "off"] = "normal",
        *,
        key: str,
        ref: Ref | None = None,
        help: str | None = None,
        label_visibility: LabelVisibility = "visible",
        border: bool = False,
        width: Width = "stretch",
        height: Height = "content",
        chart_data: Iterable[Any] | None = None,
        chart_type: Literal["line", "bar", "area"] = "line",
        delta_arrow: DeltaArrow = "auto",
        format: str | None = None,
        delta_description: str | None = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, value=value, delta=delta, delta_color=delta_color, help=help, label_visibility=label_visibility, border=border, width=width, height=height, chart_data=chart_data, chart_type=chart_type, delta_arrow=delta_arrow, format=format, delta_description=delta_description)

    def render(self):
        st.metric(widget_child("label", ""), **self._st_props("label"))
