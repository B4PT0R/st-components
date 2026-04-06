from typing import Optional

from ...core import Element, Ref
from ...core.access import _get_widget_key
from ._common import BindOption, LabelVisibility, WidgetCallback, Width, label_or_prop, st, widget_callback, widget_props


class checkbox(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, value=value, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.checkbox(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))


class toggle(Element):
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        *,
        key: str,
        ref: Optional[Ref] = None,
        disabled: bool = False,
        label_visibility: LabelVisibility = "visible",
        width: Optional[Width] = "content",
        bind: Optional[BindOption] = None,
    ):
        Element.__init__(self, key=key, label=label, ref=ref, value=value, help=help, on_change=on_change, disabled=disabled, label_visibility=label_visibility, width=width, bind=bind)

    def render(self):
        st.toggle(label_or_prop(self), key=_get_widget_key(), on_change=widget_callback(self), **widget_props(self))
