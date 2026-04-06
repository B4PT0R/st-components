from typing import Any, Literal, Optional, Sequence

from ...core import Element, Ref
from ...core.access import _get_widget_key
from ._common import LabelVisibility, WidgetCallback, WidthWithoutContent, label_or_prop, st, widget_callback, widget_props


class file_uploader(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        type: Optional[str | Sequence[str]] = None,
        accept_multiple_files: bool | Literal["directory"] = False,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        max_upload_size: Optional[int] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
    ):
        Element.__init__(self, key=key, label=label, type=type, accept_multiple_files=accept_multiple_files, ref=ref, help=help, on_change=on_change, max_upload_size=max_upload_size, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.file_uploader(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class camera_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.camera_input(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class audio_input(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        *,
        sample_rate: Optional[int] = 16000,
        key: str,
        ref: Optional[Ref] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[WidthWithoutContent] = "stretch",
    ):
        Element.__init__(self, key=key, label=label, sample_rate=sample_rate, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.audio_input(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class chat_input(Element):
    def __init__(
        self,
        placeholder: str = "Your message",
        *,
        key: str,
        ref: Optional[Ref] = None,
        max_chars: Optional[int] = None,
        max_upload_size: Optional[int] = None,
        accept_file: bool | Literal["multiple", "directory"] = False,
        file_type: Optional[str | Sequence[str]] = None,
        accept_audio: bool = False,
        audio_sample_rate: Optional[int] = 16000,
        disabled: bool = False,
        on_submit: Optional[WidgetCallback] = None,
        width: Optional[WidthWithoutContent] = "stretch",
        height: Optional[str | int] = "content",
    ):
        Element.__init__(self, key=key, placeholder=placeholder, ref=ref, max_chars=max_chars, max_upload_size=max_upload_size, accept_file=accept_file, file_type=file_type, accept_audio=accept_audio, audio_sample_rate=audio_sample_rate, disabled=disabled, on_submit=on_submit, width=width, height=height)

    def render(self):
        placeholder = self.children[0] if self.children else self.props.get("placeholder", "Your message")
        st.chat_input(placeholder, key=_get_widget_key(), on_submit=widget_callback(self, "on_submit"), **widget_props(self, "placeholder", "on_submit"))
