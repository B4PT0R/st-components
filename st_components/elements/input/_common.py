from datetime import datetime
from typing import Any

import streamlit as st

from ...core import callback_context, get_element_path, set_element_value
from ...core.access import get_element_value
from ...core.access import _get_widget_key
from .._types import (
    BindOption,
    ButtonType,
    FeedbackOptions,
    IconPosition,
    LabelVisibility,
    SelectWidgetFilterMode,
    SelectionMode,
    WidgetCallback,
    Width,
    WidthWithoutContent,
)


def label_or_prop(element):
    return element.children[0] if element.children else element.props.get("label", "")


def data_or_prop(element):
    return element.children[0] if element.children else element.props.get("data")


def widget_callback(element, callback_name="on_change", *, pass_value=False):
    callback = element.props.get(callback_name)
    if callback is None:
        return None

    args = tuple(element.props.get("args") or ())
    kwargs = dict(element.props.get("kwargs") or {})
    element_path = get_element_path()
    widget_key = _get_widget_key(element_path)

    def wrapped():
        with callback_context(element_path=element_path, widget_key=widget_key):
            if callback_name in {"on_change", "on_submit"} or pass_value:
                return callback(get_element_value(), *args, **kwargs)
            return callback(*args, **kwargs)

    return wrapped


def widget_props(element, *excluded):
    return element.props.exclude(
        "key",
        "children",
        "label",
        "ref",
        "on_change",
        "args",
        "kwargs",
        *excluded,
    )


def resolve_data_editor_value(data, editing_state):
    if editing_state is None:
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


__all__ = [
    "BindOption",
    "ButtonType",
    "FeedbackOptions",
    "IconPosition",
    "LabelVisibility",
    "SelectWidgetFilterMode",
    "SelectionMode",
    "WidgetCallback",
    "Width",
    "WidthWithoutContent",
    "data_or_prop",
    "datetime",
    "label_or_prop",
    "resolve_data_editor_value",
    "set_element_value",
    "st",
    "widget_callback",
    "widget_props",
]
