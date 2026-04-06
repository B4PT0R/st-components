from typing import Any, Iterable, Literal, Optional

from ...core import Element, Ref, callback_context, get_element_path, set_element_value
from ...core.access import _get_widget_key
from ._common import data_or_prop, st, widget_props
from .._types import Width


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
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        row_height: Optional[int] = None,
        placeholder: Optional[str] = None,
    ):
        Element.__init__(self, key=key, data=data, ref=ref, width=width, height=height, use_container_width=use_container_width, hide_index=hide_index, column_order=column_order, column_config=column_config, num_rows=num_rows, disabled=disabled, on_change=on_change, args=args, kwargs=kwargs, row_height=row_height, placeholder=placeholder)

    def render(self):
        data = data_or_prop(self)
        element_path = get_element_path()
        widget_key = _get_widget_key(element_path)
        callback = self.props.get("on_change")
        args = tuple(self.props.get("args") or ())
        kwargs = dict(self.props.get("kwargs") or {})

        def wrapped_callback():
            from . import _resolve_data_editor_value

            value = _resolve_data_editor_value(data, st.session_state.get(widget_key))
            set_element_value(element_path, value)
            if callback is None:
                return None
            with callback_context(element_path=element_path, widget_key=widget_key):
                return callback(value, *args, **kwargs)

        value = st.data_editor(data, key=widget_key, on_change=wrapped_callback if callback is not None else None, **widget_props(self, "data"))
        set_element_value(element_path, value)
