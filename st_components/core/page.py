"""Page — represents a single route in a multipage app.

Each Page wraps exactly one source (Component, callable, or file path)
and provides navigation metadata (title, icon, URL path, section).

::

    Page(key="home", nav_title="Home", default=True)(
        HomePage(key="hp")
    )
"""
import inspect
from pathlib import Path
from typing import Literal

from modict import modict

from .base import Anchor, Component, Element
from .errors import PageError


class PageProps(modict):
    key: str | None = None
    nav_title: str | None = None
    nav_icon: str | None = None
    page_title: str | None = None
    page_icon: str | None = None
    layout: Literal["centered", "wide"] | None = None
    initial_sidebar_state: Literal["auto", "expanded", "collapsed"] | None = None
    menu_items: dict | None = None
    url_path: str | None = None
    default: bool = False
    visibility: Literal["visible", "hidden"] = "visible"
    section: str | None = None
    children: list = modict.factory(list)


class Page(Component):
    __props_class__ = PageProps

    def __init__(self, **props):
        super().__init__(**props)

    def __call__(self, *children):
        if len(children) != 1:
            raise PageError(
                f"Page expects exactly one child source, got {len(children)}. "
                f"Wrap multiple children in a container or layout component."
            )
        self.props.children = list(children)
        return self

    @property
    def source(self):
        if len(self.children) != 1:
            raise PageError(
                f"Page (key={self.props.get('key')!r}) must define exactly one child source "
                f"before it can be added to an App. Call Page(key='k')(source_component)."
            )
        return self.children[0]

    @property
    def key(self):
        return self.props.get("key") or self.namespace()

    @property
    def section(self):
        return self.props.get("section")

    def navigation_props(self):
        nav = {
            **{k: v for k, v in [("title", self.props.nav_title), ("icon", self.props.nav_icon)] if v is not None},
            **{f: self.props.get(f) for f in ("url_path", "default", "visibility") if self.props.get(f) is not None},
        }
        return nav

    def page_config(self):
        return {
            **{k: v for k, v in [("page_title", self.props.page_title), ("page_icon", self.props.page_icon)] if v is not None},
            **{f: self.props.get(f) for f in ("layout", "initial_sidebar_state", "menu_items") if self.props.get(f) is not None},
        }

    def namespace(self):
        """Derive a stable namespace from the page's key, URL path, or source identity."""
        if self.props.get("key"):
            return self.props.key
        if self.props.default:
            return "__default__"
        if self.props.url_path:
            return self.props.url_path

        source = self.source
        if isinstance(source, (str, Path)):
            return Path(source).stem
        if inspect.isclass(source):
            return source.__name__
        if callable(source):
            return getattr(source, "__name__", source.__class__.__name__)
        if isinstance(source, (Component, Element)):
            return getattr(source, "key", None) or source.__class__.__name__
        return source.__class__.__name__

    def render(self):
        return Anchor(key=self.key)()
