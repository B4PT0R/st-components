from typing import Any, Literal, Sequence

from ...core import Element, Ref
from ...core.access import widget_key
import streamlit as st
from ..prop_types import LabelVisibility, WidgetCallback, WidthWithoutContent
from ..factory import widget_callback, widget_child, widget_props


class file_uploader(Element):
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        type: str | Sequence[str] | None = None,
        accept_multiple_files: bool | Literal["directory"] = False,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        max_upload_size: int | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
    ):
        Element.__init__(self, key=key, label=label, type=type, accept_multiple_files=accept_multiple_files, ref=ref, help=help, on_change=on_change, max_upload_size=max_upload_size, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.file_uploader(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class camera_input(Element):
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        *,
        key: str,
        ref: Ref | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.camera_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class audio_input(Element):
    _slots = {"root": "", "label": "label"}
    _default_slot = "root"

    def __init__(
        self,
        label: str | None = None,
        *,
        sample_rate: int | None = 16000,
        key: str,
        ref: Ref | None = None,
        help: str | None = None,
        on_change: WidgetCallback | None = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: WidthWithoutContent | None = "stretch",
    ):
        Element.__init__(self, key=key, label=label, sample_rate=sample_rate, ref=ref, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width)

    def render(self):
        st.audio_input(widget_child("label", ""), key=widget_key(), on_change=widget_callback(), **widget_props("label", "on_change"))


class chat_input(Element):
    _slots = {"root": "", "input": "textarea"}
    _default_slot = "input"

    def __init__(
        self,
        placeholder: str = "Your message",
        *,
        key: str,
        ref: Ref | None = None,
        max_chars: int | None = None,
        max_upload_size: int | None = None,
        accept_file: bool | Literal["multiple", "directory"] = False,
        file_type: str | Sequence[str] | None = None,
        accept_audio: bool = False,
        audio_sample_rate: int | None = 16000,
        disabled: bool = False,
        on_submit: WidgetCallback | None = None,
        width: WidthWithoutContent | None = "stretch",
        height: str | int | None = "content",
    ):
        Element.__init__(self, key=key, placeholder=placeholder, ref=ref, max_chars=max_chars, max_upload_size=max_upload_size, accept_file=accept_file, file_type=file_type, accept_audio=accept_audio, audio_sample_rate=audio_sample_rate, disabled=disabled, on_submit=on_submit, width=width, height=height)

    def render(self):
        placeholder = self.children[0] if self.children else self.props.get("placeholder", "Your message")
        st.chat_input(placeholder, key=widget_key(), on_submit=widget_callback("on_submit"), **widget_props("placeholder", "on_submit"))
