import inspect
from pathlib import Path

import toml

import streamlit as st

from .base import Component, Element, render
from .context_api import ContextProvider
from .context import component_context, key_context, reset_context_runtime
from .models import Config, Props, Theme
from .page import Page
from .router import Router
from .store import (
    begin_render_cycle,
    declare_shared_state,
    end_render_cycle,
    register_component,
    track_rendered_fiber,
    unregister_component,
)


_CURRENT_APP = None


def get_app():
    if _CURRENT_APP is None:
        raise RuntimeError("No current App instance is available.")
    return _CURRENT_APP


class AppProps(Props):
    key: str = "app"


class App(Component):
    __props_class__ = AppProps
    _THEME_STATE_KEY = "__st_components_app_theme__"
    _CSS_STATE_KEY = "__st_components_app_css__"
    _CONFIG_STATE_KEY = "__st_components_app_config__"
    _PERSIST_THEME_KEY = "__st_components_persist_theme__"
    _PERSIST_CONFIG_KEY = "__st_components_persist_config__"

    def __init__(
        self,
        *,
        children=None,
        page_title=None,
        page_icon=None,
        layout=None,
        initial_sidebar_state=None,
        menu_items=None,
        theme=None,
        css=None,
        config=None,
        persist_theme=True,
        persist_config=True,
    ):
        normalized_children = [] if children is None else list(children)
        if len(normalized_children) > 1:
            raise TypeError("App expects at most one root child in children=.")
        super().__init__(key="app", children=normalized_children)
        self.pages = []
        self.page_title = page_title
        self.page_icon = page_icon
        self.layout = layout
        self.initial_sidebar_state = initial_sidebar_state
        self.menu_items = menu_items
        if isinstance(theme, dict) and not isinstance(theme, Theme):
            theme = Theme(theme)
        if isinstance(config, dict) and not isinstance(config, Config):
            config = Config(config)
        self.theme = self._initial_theme(theme)
        self.css = self._initial_css(css)
        self.config = self._initial_config(config)
        self.persist_theme = persist_theme
        self.persist_config = persist_config
        self._active_router = None
        self._active_page = None
        self._active_router_wrappers = []
        global _CURRENT_APP
        _CURRENT_APP = self

    def _decorate_render(self):
        pass

    @property
    def root(self):
        if not self.children:
            return None
        return self.children[0]

    def __call__(self, *children):
        if len(children) != 1:
            raise TypeError("App expects exactly one child root.")
        self.props.children = [children[0]]
        return self

    def create_shared_state(self, namespace, spec):
        declare_shared_state(namespace, spec)
        return self

    def render_page(self, root):
        if self._active_router is not None and self._active_page is not None:
            return self._render_routed_root(
                self._active_router,
                self._active_page,
                root,
                wrappers=self._active_router_wrappers,
            )
        return self._render_root(root)

    def _initial_theme(self, theme):
        if theme is None and self._THEME_STATE_KEY in st.session_state:
            return st.session_state[self._THEME_STATE_KEY]
        return theme

    def _initial_css(self, css):
        if css is None and self._CSS_STATE_KEY in st.session_state:
            return st.session_state[self._CSS_STATE_KEY]
        return css

    def _initial_config(self, config):
        if config is None and self._CONFIG_STATE_KEY in st.session_state:
            return st.session_state[self._CONFIG_STATE_KEY]
        return config

    def set_theme(self, theme):
        if isinstance(theme, dict) and not isinstance(theme, Theme):
            theme = Theme(theme)
        if theme is not None and not isinstance(theme, Theme):
            raise TypeError(f"App.set_theme(...) expects a dict or Theme, got {type(theme)}")
        self.theme = theme
        if theme is None:
            if self._THEME_STATE_KEY in st.session_state:
                del st.session_state[self._THEME_STATE_KEY]
        else:
            st.session_state[self._THEME_STATE_KEY] = theme
        return self

    def save_theme(self, theme=None):
        if theme is not None:
            self.set_theme(theme)
        st.session_state[self._PERSIST_THEME_KEY] = True
        self._persist_theme_config()
        return self

    def set_css(self, css):
        self.css = css
        if css is None:
            if self._CSS_STATE_KEY in st.session_state:
                del st.session_state[self._CSS_STATE_KEY]
        else:
            st.session_state[self._CSS_STATE_KEY] = css
        return self

    def set_config(self, config):
        if isinstance(config, dict) and not isinstance(config, Config):
            config = Config(config)
        if config is not None and not isinstance(config, Config):
            raise TypeError(f"App.set_config(...) expects a dict or Config, got {type(config)}")
        self.config = config
        if config is None:
            if self._CONFIG_STATE_KEY in st.session_state:
                del st.session_state[self._CONFIG_STATE_KEY]
        else:
            st.session_state[self._CONFIG_STATE_KEY] = config
        return self

    def save_config(self, config=None):
        if config is not None:
            self.set_config(config)
        st.session_state[self._PERSIST_CONFIG_KEY] = True
        self._persist_app_config()
        return self

    def _config_toml_path(self):
        return Path.cwd() / ".streamlit" / "config.toml"

    def _theme_dict(self):
        if self.theme is None:
            return {}
        if not isinstance(self.theme, Theme):
            raise TypeError(f"App(theme=...) expects a dict or Theme, got {type(self.theme)}")
        return self.theme

    def _config_dict(self):
        if self.config is None:
            return {}
        if not isinstance(self.config, Config):
            raise TypeError(f"App(config=...) expects a dict or Config, got {type(self.config)}")
        return self.config

    def _persist_theme_config(self):
        theme = self._theme_dict()
        if not theme:
            return

        config_path = self._config_toml_path()
        existing_text = config_path.read_text() if config_path.exists() else ""
        existing_config = toml.loads(existing_text) if existing_text.strip() else {}
        rendered_config = dict(existing_config)
        rendered_config["theme"] = dict(theme)
        rendered = toml.dumps(rendered_config)

        if rendered != existing_text:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(rendered)
        st.session_state[self._PERSIST_THEME_KEY] = False

    def _persist_app_config(self):
        config = self._config_dict()
        if not config:
            return

        config_path = self._config_toml_path()
        existing_text = config_path.read_text() if config_path.exists() else ""
        existing_config = toml.loads(existing_text) if existing_text.strip() else {}
        rendered_config = dict(existing_config)
        for key, value in config.items():
            rendered_config[key] = dict(value) if isinstance(value, dict) else value
        rendered = toml.dumps(rendered_config)

        if rendered != existing_text:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(rendered)
        st.session_state[self._PERSIST_CONFIG_KEY] = False

    def _apply_theme_runtime(self):
        theme = self._theme_dict()
        if not theme:
            return

        try:
            import importlib

            streamlit_config = importlib.import_module("streamlit.config")
        except Exception:
            return

        def apply(prefix, value):
            for key, item in value.items():
                option_key = f"{prefix}.{key}"
                if isinstance(item, dict):
                    apply(option_key, item)
                else:
                    streamlit_config.set_option(option_key, item)

        apply("theme", theme)

    def _apply_config_runtime(self):
        config = self._config_dict()
        if not config:
            return

        try:
            import importlib

            streamlit_config = importlib.import_module("streamlit.config")
        except Exception:
            return

        client = config.get("client", {})
        for key, value in client.items():
            streamlit_config.set_option(f"client.{key}", value)

    def _css_blocks(self):
        if self.css is None:
            return []
        if isinstance(self.css, (str, Path)):
            sources = [self.css]
        else:
            sources = list(self.css)

        blocks = []
        for source in sources:
            if isinstance(source, Path):
                blocks.append(source.read_text())
                continue
            if isinstance(source, str):
                candidate = Path(source)
                if candidate.suffix == ".css" and candidate.exists():
                    blocks.append(candidate.read_text())
                else:
                    blocks.append(source)
                continue
            raise TypeError(f"Unsupported css source type: {type(source)}")
        return [block for block in blocks if block.strip()]

    def _apply_styles(self):
        self._apply_config_runtime()
        self._apply_theme_runtime()
        if self.persist_theme or st.session_state.get(self._PERSIST_THEME_KEY, False):
            self._persist_theme_config()
        if self.persist_config or st.session_state.get(self._PERSIST_CONFIG_KEY, False):
            self._persist_app_config()

        css_blocks = self._css_blocks()
        if css_blocks:
            st.html("<style>\n" + "\n\n".join(css_blocks) + "\n</style>")

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

    def _prepare_app_fiber(self):
        self._fiber_key = self.key
        if not self.is_mounted:
            self.mount()
        if self.fiber.component_id != self._component_id:
            unregister_component(self.fiber.component_id)
            self.fiber.component_id = self._component_id
        register_component(self._component_id, self)
        track_rendered_fiber(self._fiber_key)

    def _render_with_cycle(self, body):
        reset_context_runtime()
        begin_render_cycle()
        try:
            self._prepare_app_fiber()
            with key_context(self.key), component_context(self):
                return body()
        finally:
            end_render_cycle()

    def _render_root(self, root):
        return self._render_with_cycle(lambda: render(root))

    def _render_routed_root(self, router, page, root, *, wrappers=None):
        def build_router_page_tree():
            return router._render_component_body(
                lambda: page._render_component_body(lambda: root)
            )

        def body():
            current = build_router_page_tree
            for wrapper in reversed(wrappers or []):
                current = (
                    lambda current=current, wrapper=wrapper: wrapper._render_component_body(current)
                )
            return render(current())

        return self._render_with_cycle(body)

    def _run_inline_page_source(self, source, *, router=None, page=None, wrappers=None):
        if inspect.isclass(source) and issubclass(source, Component):
            raise TypeError(
                "Page inline sources must be instantiated Components, not Component classes."
            )

        if isinstance(source, (Component, Element)) or not callable(source):
            if router is not None and page is not None:
                return self._render_routed_root(router, page, source, wrappers=wrappers)
            return self._render_root(source)

        result = source()
        if inspect.isclass(result) and issubclass(result, Component):
            raise TypeError(
                "Page factories must return instantiated Components, not Component classes."
            )
        if result is not None:
            if router is not None and page is not None:
                return self._render_routed_root(router, page, result, wrappers=wrappers)
            return self._render_root(result)
        return None

    def _build_streamlit_page(self, router, page, *, wrappers=None):
        source = page.source
        page_kwargs = page.navigation_props()

        if isinstance(source, (str, Path)):
            streamlit_source = source
        else:
            def streamlit_source():
                return self._run_inline_page_source(source, router=router, page=page, wrappers=wrappers)

        streamlit_page = st.Page(streamlit_source, **page_kwargs)
        return streamlit_page, page

    def _build_navigation_pages(self, router, *, wrappers=None):
        sections = {}
        pages = []
        page_map = {}

        for page in router.pages:
            streamlit_page, original_page = self._build_streamlit_page(router, page, wrappers=wrappers)
            page_map[id(streamlit_page)] = original_page

            section = original_page.section
            if section is None:
                pages.append(streamlit_page)
            else:
                sections.setdefault(section, []).append(streamlit_page)

        if sections:
            if pages:
                sections = {"": pages, **sections}
            return sections, page_map
        return pages, page_map

    def _unwrap_router_root(self):
        wrappers = []
        node = self.root

        while isinstance(node, ContextProvider):
            if len(node.children) != 1:
                raise RuntimeError(
                    "Providers above Router must wrap exactly one child root."
                )
            wrappers.append(node)
            node = node.children[0]

        if isinstance(node, Router):
            return wrappers, node
        return None, None

    def render(self):
        if self.root is None:
            raise RuntimeError("App.render() requires a root.")

        wrappers, router = self._unwrap_router_root()

        if router is None:
            self._apply_page_config()
            self._apply_styles()
            return self._render_root(self.root)

        navigation_pages, page_map = self._build_navigation_pages(router, wrappers=wrappers)
        current = st.navigation(
            navigation_pages,
            position=router.props.position,
            expanded=router.props.expanded,
        )
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
        self._apply_styles()

        previous_router = self._active_router
        previous_page = self._active_page
        previous_wrappers = self._active_router_wrappers
        self._active_router = router
        self._active_page = current_page
        self._active_router_wrappers = wrappers or []
        try:
            return current.run()
        finally:
            self._active_router = previous_router
            self._active_page = previous_page
            self._active_router_wrappers = previous_wrappers
