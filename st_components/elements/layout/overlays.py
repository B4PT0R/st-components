from typing import Any, Callable, Literal, Optional

import streamlit as st

from ...core import Element, Ref, get_key_stack, path_context, render
from .._types import DialogWidth, DismissBehavior, Width, WidthWithoutContent


class dialog(Element):
    def __init__(
        self,
        title: str = "",
        *,
        key: str,
        ref: Optional[Ref] = None,
        width: DialogWidth = "small",
        dismissible: bool = True,
        icon: Optional[str] = None,
        on_dismiss: DismissBehavior = "ignore",
    ):
        Element.__init__(self, key=key, title=title, ref=ref, width=width, dismissible=dismissible, icon=icon, on_dismiss=on_dismiss)

    def render(self):
        title = self.props.get("title", "")
        on_dismiss = self.props.get("on_dismiss", "ignore")
        context_keys = get_key_stack()

        def dismiss_callback():
            if callable(on_dismiss):
                return on_dismiss()
            return on_dismiss

        @st.dialog(
            title,
            **self.props.exclude("key", "children", "title", "ref", "on_dismiss"),
            on_dismiss=dismiss_callback if callable(on_dismiss) else on_dismiss,
        )
        def body():
            with path_context(context_keys):
                for child in self.children:
                    render(child)

        return body()


class chat_message(Element):
    def __init__(
        self,
        name: Literal["user", "assistant", "ai", "human"] | str = "assistant",
        *,
        key: str,
        ref: Optional[Ref] = None,
        avatar: Optional[str] = None,
        width: Width = "stretch",
    ):
        Element.__init__(self, key=key, name=name, ref=ref, avatar=avatar, width=width)

    def render(self):
        with st.chat_message(self.props.get("name", "assistant"), **self.props.exclude("key", "children", "name", "ref")):
            for child in self.children:
                render(child)


class status(Element):
    def __init__(
        self,
        label: str = "",
        *,
        key: str,
        ref: Optional[Ref] = None,
        expanded: bool = False,
        state: Literal["running", "complete", "error"] = "running",
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, label=label, ref=ref, expanded=expanded, state=state, width=width)

    def render(self):
        with st.status(self.props.get("label", ""), **self.props.exclude("key", "children", "label", "ref")):
            for child in self.children:
                render(child)
