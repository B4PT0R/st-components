from typing import Any, Iterable, Literal, Optional

from ...core import Element, Ref
from ...core.access import widget_key
from ..factory import widget_callback
import streamlit as st
from ..factory import widget_child, widget_props
from ..prop_types import Width


class data_editor(Element):
    def __init__(
        self,
        data: Optional[Any] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        width: Optional[Width] = "stretch",
        height: Optional[int | str] = "auto",
        use_container_width: Optional[bool] = None,
        hide_index: Optional[bool] = None,
        column_order: Optional[Iterable[str]] = None,
        column_config: Optional[Any] = None,
        num_rows: Literal["fixed", "dynamic", "add", "delete"] = "fixed",
        disabled: bool | Iterable[str | int] = False,
        on_change: Optional[Any] = None,
        row_height: Optional[int] = None,
        placeholder: Optional[str] = None,
    ):
        Element.__init__(self, key=key, data=data, ref=ref, width=width, height=height, use_container_width=use_container_width, hide_index=hide_index, column_order=column_order, column_config=column_config, num_rows=num_rows, disabled=disabled, on_change=on_change, row_height=row_height, placeholder=placeholder)

    @staticmethod
    def _resolve_output(data, editing_state):
        from modict import MISSING
        if editing_state is None or editing_state is MISSING:
            return data
        try:
            import pyarrow as pa
            from streamlit import dataframe_util
            from streamlit.elements.widgets.data_editor import (
                DataEditorSerde,
                _apply_dataframe_edits,
                determine_dataframe_schema,
            )
        except Exception:
            return data
        data_format = dataframe_util.determine_data_format(data)
        data_df = dataframe_util.convert_anything_to_pandas_df(data, ensure_copy=True)
        arrow_table = pa.Table.from_pandas(data_df)
        dataframe_schema = determine_dataframe_schema(data_df, arrow_table.schema)
        if isinstance(editing_state, str):
            editing_state = DataEditorSerde().deserialize(editing_state)
        _apply_dataframe_edits(data_df, editing_state, dataframe_schema)
        return dataframe_util.convert_pandas_df_to_data_format(data_df, data_format)

    def get_output(self, raw):
        return self._resolve_output(widget_child("data"), raw)

    def render(self):
        data = widget_child("data")
        st.data_editor(
            data,
            key=widget_key(),
            on_change=widget_callback(),
            **widget_props("data", "on_change"),
        )
