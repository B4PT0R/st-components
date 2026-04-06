from typing import Any, Callable, Iterable, Literal, Optional, Sequence

from ...core import Element, Ref
from ...core.access import _get_widget_key
from ._common import (
    BindOption,
    FeedbackOptions,
    LabelVisibility,
    SelectWidgetFilterMode,
    SelectionMode,
    WidgetCallback,
    Width,
    WidthWithoutContent,
    label_or_prop,
    st,
    widget_callback,
    widget_props,
)


class radio(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        index: Optional[int] = 0,
        format_func: Callable[[Any], Any] = str,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        horizontal: bool = False,
        captions: Optional[Sequence[str]] = None,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, index=index, format_func=format_func, help=help, on_change=on_change, args=args, kwargs=kwargs, disabled=disabled, horizontal=horizontal, captions=captions, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.radio(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class selectbox(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        index: Optional[int] = 0,
        format_func: Callable[[Any], str] = str,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        placeholder: Optional[str] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        accept_new_options: bool = False,
        filter_mode: SelectWidgetFilterMode = "fuzzy",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, index=index, format_func=format_func, help=help, on_change=on_change, args=args, kwargs=kwargs, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, accept_new_options=accept_new_options, filter_mode=filter_mode, width=width, bind=bind)

    def render(self):
        st.selectbox(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class multiselect(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        default: Optional[Any] = None,
        format_func: Callable[[Any], str] = str,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        max_selections: Optional[int] = None,
        placeholder: Optional[str] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        accept_new_options: bool = False,
        filter_mode: SelectWidgetFilterMode = "fuzzy",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, default=default, format_func=format_func, help=help, on_change=on_change, args=args, kwargs=kwargs, max_selections=max_selections, placeholder=placeholder, disabled=disabled, label_visibility=label_visibility, accept_new_options=accept_new_options, filter_mode=filter_mode, width=width, bind=bind)

    def render(self):
        st.multiselect(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class slider(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        value: Optional[Any] = None,
        step: Optional[Any] = None,
        format: Optional[str] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, ref=ref, help=help, on_change=on_change, args=args, kwargs=kwargs, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.slider(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class select_slider(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        value: Optional[Any | Sequence[Any]] = None,
        format_func: Callable[[Any], Any] = str,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, value=value, format_func=format_func, ref=ref, help=help, on_change=on_change, args=args, kwargs=kwargs, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.select_slider(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class pills(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        *,
        key: str,
        ref: Optional[Ref] = None,
        selection_mode: Optional[SelectionMode] = "single",
        default: Optional[Sequence[Any] | Any] = None,
        required: bool = False,
        format_func: Optional[Callable[[Any], str]] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, selection_mode=selection_mode, default=default, required=required, format_func=format_func, help=help, on_change=on_change, args=args, kwargs=kwargs, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.pills(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class segmented_control(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        options: Optional[Sequence[Any]] = (),
        *,
        key: str,
        ref: Optional[Ref] = None,
        selection_mode: Optional[SelectionMode] = "single",
        default: Optional[Sequence[Any] | Any] = None,
        required: bool = False,
        format_func: Optional[Callable[[Any], str]] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, options=options, ref=ref, selection_mode=selection_mode, default=default, required=required, format_func=format_func, help=help, on_change=on_change, args=args, kwargs=kwargs, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.segmented_control(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class feedback(Element):
    def __init__(
        self,
        options: FeedbackOptions = "thumbs",
        *,
        key: str,
        ref: Optional[Ref] = None,
        default: Optional[int] = None,
        disabled: bool = False,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        width: Optional[Width] = "content",
    ):
        Element.__init__(self, key=key, options=options, ref=ref, default=default, disabled=disabled, on_change=on_change, args=args, kwargs=kwargs, width=width)

    def render(self):
        options = self.children[0] if self.children else self.props.get("options", "thumbs")
        st.feedback(options, key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self, "options"))
