import inspect
from pathlib import Path
from typing import Literal

from modict import modict

from .base import Component, Element, Fragment


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
            raise TypeError("Page expects exactly one child source.")
        self.props.children = list(children)
        return self

    @property
    def source(self):
        if len(self.children) != 1:
            raise RuntimeError("Page must define exactly one child source before it can be added to an App.")
        return self.children[0]

    @property
    def key(self):
        return self.props.get("key") or self.namespace()

    @property
    def section(self):
        return self.props.get("section")

    def navigation_props(self):
        navigation = {}
        if self.props.nav_title is not None:
            navigation["title"] = self.props.nav_title
        if self.props.nav_icon is not None:
            navigation["icon"] = self.props.nav_icon
        for field in ("url_path", "default", "visibility"):
            value = self.props.get(field)
            if value is not None:
                navigation[field] = value
        return navigation

    def page_config(self):
        config = {}
        if self.props.page_title is not None:
            config["page_title"] = self.props.page_title
        if self.props.page_icon is not None:
            config["page_icon"] = self.props.page_icon

        for field in ("layout", "initial_sidebar_state", "menu_items"):
            value = self.props.get(field)
            if value is not None:
                config[field] = value
        return config

    def namespace(self):
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
        return Fragment(key=self.key)()
