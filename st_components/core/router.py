"""Router — multipage navigation component.

The Router is the sole direct child of App (optionally wrapped in
ContextProviders).  It holds Page children and delegates to
``st.navigation`` for URL-based page switching.

::

    App(
        Router(key="nav", position="sidebar")(
            Page(key="home", nav_title="Home", default=True)(HomePage(key="hp")),
            Page(key="settings", nav_title="Settings")(SettingsPage(key="sp")),
        )
    ).render()
"""
import inspect
from typing import Literal

from modict import modict

from .base import Anchor, Component, Element
from .errors import RouterError
from .models import Props
from .page import Page


class RouterProps(Props):
    key: str = "router"
    position: Literal["sidebar", "top", "hidden"] = "sidebar"
    expanded: bool = False
    chrome: type | None = None
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
            raise RouterError(
                f"Router does not accept global page config props ({names}). "
                f"Pass them to App(...) instead."
            )
        chrome = props.get("chrome")
        if chrome is not None:
            if not inspect.isclass(chrome) or not issubclass(chrome, Component) or issubclass(chrome, (Element, Page, Router)):
                raise RouterError(
                    f"Router(chrome=...) expects a Component subclass, got {chrome!r}. "
                    f"Define a class that places its page child via *self.children, e.g.:\n"
                    f"    class Chrome(Component):\n"
                    f"        def render(self):\n"
                    f"            return container(key='layout')(\n"
                    f"                Sidebar(key='sb'),\n"
                    f"                container(key='main')(*self.children),\n"
                    f"            )"
                )
        super().__init__(**props)

    def __call__(self, *children):
        for child in children:
            if not isinstance(child, Page):
                raise RouterError(
                    f"Router expects only Page children, got {type(child).__name__!r}. "
                    f"Wrap your component in a Page: Page(key='k')(MyComponent(key='c'))."
                )
        self.props.children = list(children)
        return self

    @property
    def pages(self):
        return self.children

    def render(self):
        raise RouterError(
            "Router must be the sole direct child of App "
            "(optionally wrapped in ContextProviders). "
            "It cannot be nested inside other components."
        )
