import inspect
from pathlib import Path

import streamlit as st

from .base import Component, Element, render
from .context import page_namespace, reset_context_runtime
from .page import Page
from .router import Router
from .store import begin_render_cycle, declare_shared_state, end_render_cycle


class App:

    @classmethod
    def render_page(cls, root):
        return cls(root=root).render()

    def __init__(
        self,
        root=None,
        *,
        page_title=None,
        page_icon=None,
        layout=None,
        initial_sidebar_state=None,
        menu_items=None,
    ):
        self.root = root
        self.pages = []
        self.page_title = page_title
        self.page_icon = page_icon
        self.layout = layout
        self.initial_sidebar_state = initial_sidebar_state
        self.menu_items = menu_items

    def __call__(self, *children):
        if len(children) != 1:
            raise TypeError("App expects exactly one child root.")
        self.root = children[0]
        return self

    def shared_state(self, namespace, spec):
        declare_shared_state(namespace, spec)
        return self

    def _app_page_config(self):
        config = {}
        for field in ("page_title", "page_icon", "layout", "initial_sidebar_state", "menu_items"):
            value = getattr(self, field)
            if value is not None:
                config[field] = value
        return config

    def _apply_page_config(self, page=None):
        config = self._app_page_config()
        if page is not None:
            config.update(page.page_config())
            if "page_title" not in config and page.props.nav_title is not None:
                config["page_title"] = page.props.nav_title
            if "page_icon" not in config and page.props.nav_icon is not None:
                config["page_icon"] = page.props.nav_icon
        if config:
            st.set_page_config(**config)

    def _render_root(self, root):
        reset_context_runtime()
        begin_render_cycle()
        try:
            return render(root)
        finally:
            end_render_cycle()

    def _run_inline_page_source(self, source):
        if inspect.isclass(source) and issubclass(source, Component):
            raise TypeError(
                "Page inline sources must be instantiated Components, not Component classes."
            )

        if isinstance(source, (Component, Element)) or not callable(source):
            return self._render_root(source)

        result = source()
        if inspect.isclass(result) and issubclass(result, Component):
            raise TypeError(
                "Page factories must return instantiated Components, not Component classes."
            )
        if result is not None:
            return self._render_root(result)
        return None

    def _build_streamlit_page(self, page):
        source = page.source
        page_kwargs = page.navigation_props()

        if isinstance(source, (str, Path)):
            streamlit_source = source
        else:
            def streamlit_source():
                return self._run_inline_page_source(source)

        streamlit_page = st.Page(streamlit_source, **page_kwargs)
        return streamlit_page, page.namespace(), page

    def _build_navigation_pages(self, router):
        sections = {}
        pages = []
        namespaces = {}
        page_map = {}

        for page in router.pages:
            streamlit_page, namespace, original_page = self._build_streamlit_page(page)
            namespaces[id(streamlit_page)] = namespace
            page_map[id(streamlit_page)] = original_page

            section = original_page.section
            if section is None:
                pages.append(streamlit_page)
            else:
                sections.setdefault(section, []).append(streamlit_page)

        if sections:
            if pages:
                sections = {"": pages, **sections}
            return sections, namespaces, page_map
        return pages, namespaces, page_map

    def render(self, *, position="sidebar", expanded=False):
        if self.root is None:
            raise RuntimeError("App.render() requires a root.")

        if not isinstance(self.root, Router):
            self._apply_page_config()
            return self._render_root(self.root)

        router = self.root
        navigation_pages, namespaces, page_map = self._build_navigation_pages(router)
        current = st.navigation(
            navigation_pages,
            position=router.props.position if router.props.position is not None else position,
            expanded=router.props.expanded if router.props.expanded is not None else expanded,
        )
        namespace = namespaces.get(id(current))
        current_page = page_map.get(id(current))

        config = self._app_page_config()
        if current_page is not None:
            config.update(current_page.page_config())
            if "page_title" not in config and current_page.props.nav_title is not None:
                config["page_title"] = current_page.props.nav_title
            if "page_icon" not in config and current_page.props.nav_icon is not None:
                config["page_icon"] = current_page.props.nav_icon
        if config:
            st.set_page_config(**config)

        with page_namespace(namespace):
            return current.run()
