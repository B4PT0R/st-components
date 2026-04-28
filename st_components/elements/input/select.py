from typing import Any, Callable, Iterable, Literal, Sequence

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import BindOption, FeedbackOptions, LabelVisibility, SelectWidgetFilterMode, SelectionMode, WidgetCallback, Width, WidthWithoutContent
from ..factory import widget_callback, widget_child, widget_props


def _indexed_default(props):
    """Return options[index] when the widget has no session_state value yet."""
    options = props.get("options") or []
    index = props.get("index", 0)
    return options[index] if options and index is not None and index < len(options) else None


class radio(Element):
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        index: int | None = 0,
        format_func: Callable[[Any], Any] = str,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        horizontal: bool = False,
        captions: Sequence[str] | None = None,
        label_visibility: LabelVisibility = "visible",
        width: Width | None = "content",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, index=index, format_func=format_func, help=help, on_change=on_change, disabled=disabled, horizontal=horizontal, captions=captions, label_visibility=label_visibility, width=width, bind=bind)

    def get_output(self, raw):
        return raw if raw is not None else _indexed_default(self.props)

    def render(self):
        st.radio(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class selectbox(Element):
    _slots = {"root": "", "select": '[data-baseweb="select"]', "label": "label"}
    _default_slot = "select"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        index: int | None = 0,
        format_func: Callable[[Any], str] = str,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        accept_new_options: bool = False,
        filter_mode: SelectWidgetFilterMode = "fuzzy",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, index=index, format_func=format_func, help=help, on_change=on_change, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, accept_new_options=accept_new_options, filter_mode=filter_mode, width=width, bind=bind)

    def get_output(self, raw):
        return raw if raw is not None else _indexed_default(self.props)

    def render(self):
        st.selectbox(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class multiselect(Element):
    _default_output_prop = "default"
    _slots = {"root": "", "select": '[data-baseweb="select"]', "label": "label"}
    _default_slot = "select"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        default: Any | None = None,
        format_func: Callable[[Any], str] = str,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        max_selections: int | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        accept_new_options: bool = False,
        filter_mode: SelectWidgetFilterMode = "fuzzy",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, default=default, format_func=format_func, help=help, on_change=on_change, max_selections=max_selections, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, accept_new_options=accept_new_options, filter_mode=filter_mode, width=width, bind=bind)

    def render(self):
        st.multiselect(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class slider(Element):
    _default_output_prop = "value"
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        min_value: Any | None = None,
        max_value: Any | None = None,
        value: Any | None = None,
        step: Any | None = None,
        format: str | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.slider(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class select_slider(Element):
    _default_output_prop = "value"
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        value: Any | Sequence[Any] | None = None,
        format_func: Callable[[Any], Any] = str,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, value=value, format_func=format_func, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.select_slider(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class pills(Element):
    _default_output_prop = "default"
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        *,
        key: str,
        ref: Ref | None = None,
        selection_mode: SelectionMode | None = "single",
        default: Sequence[Any] | Any | None = None,
        required: bool = False,
        format_func: Callable[[Any], str | None] = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Width | None = "content",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, selection_mode=selection_mode, default=default, required=required, format_func=format_func, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.pills(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class segmented_control(Element):
    _default_output_prop = "default"
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        options: Sequence[Any] | None = (),
        *,
        key: str,
        ref: Ref | None = None,
        selection_mode: SelectionMode | None = "single",
        default: Sequence[Any] | Any | None = None,
        required: bool = False,
        format_func: Callable[[Any], str | None] = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Width | None = "content",
        bind: BindOption | None = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, selection_mode=selection_mode, default=default, required=required, format_func=format_func, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.segmented_control(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class feedback(Element):
    _default_output_prop = "default"
    _slots = {"root": ""}
    _default_slot = "root"

    def __init__(
        self,
        options: FeedbackOptions = "thumbs",
        *,
        key: str,
        ref: Ref | None = None,
        default: int | None = None,
        disabled: bool = False,
        on_change: WidgetCallback | None = None,
        width: Width | None = "content",
    ):
        Element.__init__(self, key=key, options=options, ref=ref, default=default, disabled=disabled, on_change=on_change, width=width)

    def render(self):
        options = self.children[0] if self.children else self.props.get("options", "thumbs")
        st.feedback(options, key=widget_key(), on_change=widget_callback(), **widget_props("options", "on_change"))
