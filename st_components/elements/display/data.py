from typing import Any, Iterable, Literal, Optional

import streamlit as st

from ...core import Element, Ref, get_element_path
from ...core.access import _get_widget_key
from .._types import DataSelectionMode, DeltaArrow, Height, LabelVisibility, Width, WidthWithoutContent
from .._utils import child_or_prop, selection_prop, store_element_value


class dataframe(Element):
    def __init__(
        self,
        data: Any = None,
        width: Width = "stretch",
        height: int | str = "auto",
        *,
        key: str,
        ref: Optional[Ref] = None,
        use_container_width: Optional[bool] = None,
        hide_index: Optional[bool] = None,
        column_order: Optional[Iterable[str]] = None,
        column_config: Optional[Any] = None,
        on_select: Literal["ignore", "rerun"] | Any = "ignore",
        selection_mode: DataSelectionMode | Iterable[DataSelectionMode] = "multi-row",
        selection_default: Optional[Any] = None,
        row_height: Optional[int] = None,
        placeholder: Optional[str] = None,
    ):
        Element.__init__(self, key=key, ref=ref, data=data, width=width, height=height, use_container_width=use_container_width, hide_index=hide_index, column_order=column_order, column_config=column_config, on_select=on_select, selection_mode=selection_mode, selection_default=selection_default, row_height=row_height, placeholder=placeholder)

    def render(self):
        element_path = get_element_path()
        value = st.dataframe(
            child_or_prop(self, "data"),
            key=_get_widget_key(element_path),
            on_select=selection_prop(self),
            **self.props.exclude("key", "children", "data", "ref", "on_select"),
        )
        store_element_value(element_path, value)


class table(Element):
    def __init__(
        self,
        data: Any = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        border: bool | Literal["horizontal"] = True,
        width: Width = "stretch",
        height: Height = "content",
        hide_index: Optional[bool] = None,
        hide_header: Optional[bool] = None,
    ):
        Element.__init__(self, key=key, ref=ref, data=data, border=border, width=width, height=height, hide_index=hide_index, hide_header=hide_header)

    def render(self):
        st.table(child_or_prop(self, "data"), **self.props.exclude("key", "children", "data", "ref"))


class metric(Element):
    def __init__(
        self,
        label: str = "",
        value: Any = None,
        delta: Any = None,
        delta_color: Literal["normal", "inverse", "off"] = "normal",
        *,
        key: str,
        ref: Optional[Ref] = None,
        help: Optional[str] = None,
        label_visibility: LabelVisibility = "visible",
        border: bool = False,
        width: Width = "stretch",
        height: Height = "content",
        chart_data: Optional[Iterable[Any]] = None,
        chart_type: Literal["line", "bar", "area"] = "line",
        delta_arrow: DeltaArrow = "auto",
        format: Optional[str] = None,
        delta_description: Optional[str] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, value=value, delta=delta, delta_color=delta_color, help=help, label_visibility=label_visibility, border=border, width=width, height=height, chart_data=chart_data, chart_type=chart_type, delta_arrow=delta_arrow, format=format, delta_description=delta_description)

    def render(self):
        st.metric(child_or_prop(self, "label", ""), **self.props.exclude("key", "children", "label", "ref"))
