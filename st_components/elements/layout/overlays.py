from typing import Any, Callable, Literal

import streamlit as st

from ...core import Element, Ref, get_key_stack, render, set_context
from ..factory import render_handle
from ..prop_types import DialogWidth, DismissBehavior, Width, WidthWithoutContent


class dialog(Element):
    def __init__(
        self,
        title: str = "",
        *,
        key: str | None = None,
        ref: Ref | None = None,
        width: DialogWidth = "small",
        dismissible: bool = True,
        icon: str | None = None,
        on_dismiss: DismissBehavior = "ignore",
    ):
        Element.__init__(self, key=key, title=title, ref=ref, width=width, dismissible=dismissible, icon=icon, on_dismiss=on_dismiss)

    def render(self):
        title = self.props.get("title", "")
        on_dismiss = self.props.get("on_dismiss", "ignore")
        context_keys = get_key_stack()
        dismiss_callback = (lambda: on_dismiss()) if callable(on_dismiss) else None

        @st.dialog(
            title,
            **self.props.exclude("key", "children", "title", "ref", "on_dismiss"),
            on_dismiss=dismiss_callback if callable(on_dismiss) else on_dismiss,
        )
        def body():
            with set_context(keys=context_keys):
                for child in self.children:
                    render(child)

        body()


class chat_message(Element):
    def __init__(
        self,
        name: Literal["user", "assistant", "ai", "human"] | str = "assistant",
        *,
        key: str | None = None,
        ref: Ref | None = None,
        avatar: str | None = None,
        width: Width = "stretch",
    ):
        Element.__init__(self, key=key, name=name, ref=ref, avatar=avatar, width=width)

    def render(self):
        handle = st.chat_message(self.props.get("name", "assistant"), **self.props.exclude("key", "children", "name", "ref"))
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)


class status(Element):
    def __init__(
        self,
        label: str = "",
        *,
        key: str | None = None,
        ref: Ref | None = None,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, expanded=expanded, state=state, width=width)

    def render(self):
        handle = st.status(self.props.get("label", ""), **self.props.exclude("key", "children", "label", "ref"))
        self.state.handle = handle
        with render_handle(handle, self._fiber_key):
            for child in self.children:
                render(child)
