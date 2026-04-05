import inspect
from pathlib import Path

import toml

import streamlit as st

from .base import Component, Element, render
from .context import page_namespace, reset_context_runtime
from .models import Config, Theme
from .page import Page
from .router import Router
from .store import begin_render_cycle, declare_shared_state, end_render_cycle


_CURRENT_APP = None


def get_app():
    if _CURRENT_APP is None:
        raise RuntimeError("No current App instance is available.")
    return _CURRENT_APP


class App:
    _THEME_STATE_KEY = "__st_components_app_theme__"
    _CSS_STATE_KEY = "__st_components_app_css__"
    _CONFIG_STATE_KEY = "__st_components_app_config__"
    _PERSIST_THEME_KEY = "__st_components_persist_theme__"
    _PERSIST_CONFIG_KEY = "__st_components_persist_config__"

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
        theme=None,
        css=None,
        config=None,
        persist_theme=True,
        persist_config=True,
    ):
        self.root = root
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
        global _CURRENT_APP
        _CURRENT_APP = self

    def __call__(self, *children):
        if len(children) != 1:
            raise TypeError("App expects exactly one child root.")
        self.root = children[0]
        return self

    def shared_state(self, namespace, spec):
        declare_shared_state(namespace, spec)
        return self

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
            self._apply_styles()
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
        self._apply_styles()

        with page_namespace(namespace):
            return current.run()
