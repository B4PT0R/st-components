from typing import Literal

from modict import modict

from .base import Anchor, Component
from .models import Props
from .page import Page


class RouterProps(Props):
    key: str = "router"
    position: Literal["sidebar", "top", "hidden"] = "sidebar"
    expanded: bool = False
    children: list[Page] = modict.factory(list)


class Router(Component):
    class Props(RouterProps):
        pass

    def __init__(self, **props):
        unsupported = {
            field: props[field]
            for field in (
                "page_title",
                "page_icon",
                "layout",
                "initial_sidebar_state",
                "menu_items",
            )
            if field in props
        }
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise TypeError(
                f"Router does not accept global page config props ({names}). "
                "Pass them to App(...) instead."
            )
        super().__init__(**props)

    def __call__(self, *children):
        for child in children:
            if not isinstance(child, Page):
                raise TypeError(
                    f"Router expects only Page children, got {type(child)}"
                )
        self.props.children = list(children)
        return self

    @property
    def pages(self):
        return self.children

    def render(self):
        return Anchor(key=self.key)(*self.children)
