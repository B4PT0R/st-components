import inspect
from pathlib import Path

import toml

import streamlit as st

from . import _session as ss
from .base import Component, Element, render
from .provider import ContextProvider
from .context import set_context
from .models import AppConfig, Config, Props, Theme, ThemeSection
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
    """Return the current :class:`App` instance.

    Raises ``RuntimeError`` if no App has been created yet.  Useful inside
    components that need to access the app's theme, CSS, or shared state.
    """
    if _CURRENT_APP is None:
        raise RuntimeError("No current App instance is available.")
    return _CURRENT_APP


class AppProps(Props):
    key: str = "app"


class App(Component):
    __props_class__ = AppProps
    _THEME_STATE_KEY = ss.APP_THEME
    _CSS_STATE_KEY = ss.APP_CSS
    _CONFIG_STATE_KEY = ss.APP_CONFIG

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
        color_mode=None,
        css=None,
        config=None,
        query_params=None,
    ):
        normalized_children = [] if children is None else list(children)
        if len(normalized_children) > 1:
            raise TypeError("App expects at most one root child in children=.")
        super().__init__(key="app", children=normalized_children)

        # Constructor args are defaults — fiber overrides are the source of truth.
        # Read existing fiber overrides to avoid clobbering runtime changes.
        from .store import fibers as _fibers
        existing = _fibers().get("app")
        ov = (existing.overrides or {}).get("props", {}) if existing else {}

        self.pages = []
        self.page_title = ov.get("page_title", page_title)
        self.page_icon = ov.get("page_icon", page_icon)
        self.layout = ov.get("layout", layout)
        self.initial_sidebar_state = ov.get("initial_sidebar_state", initial_sidebar_state)
        self.menu_items = ov.get("menu_items", menu_items)

        theme = ov.get("theme", theme)
        css = ov.get("css", css)
        config = ov.get("config", config)
        if isinstance(theme, dict) and not isinstance(theme, Theme):
            theme = Theme(theme)
        if isinstance(config, dict) and not isinstance(config, Config):
            config = Config(config)

        # Priority: session state > constructor arg > config.toml > default
        loaded_mode = None
        self.theme = self._recall_or(theme, self._THEME_STATE_KEY)
        if self.theme is None:
            self.theme, loaded_mode = self._load_theme_from_config()
        self.css = self._recall_or(css, self._CSS_STATE_KEY)
        self.config = self._recall_or(config, self._CONFIG_STATE_KEY)
        # color_mode: session state > fiber override > constructor arg > config.toml > default
        self.color_mode = self._recall_or(
            ov.get("color_mode", color_mode or loaded_mode or "light"),
            ss.APP_COLOR_MODE,
        )
        # Persist resolved color_mode so it survives reruns even when
        # the theme is later stored in session state (which skips
        # _load_theme_from_config and therefore loaded_mode).
        self._sync_session(ss.APP_COLOR_MODE, self.color_mode)

        from .query_params import query_params as _qp
        self.params = _qp(query_params)
        self._active_router = None
        self._active_page = None
        self._active_router_wrappers = []
        global _CURRENT_APP
        _CURRENT_APP = self

    def _decorate_render(self):
        original_render = self.render

        def decorated():
            root = original_render()
            if root is None:
                raise RuntimeError(
                    "App.render() must return a root — "
                    "pass one via App()(root) or override render()."
                )
            return self._run_app(root)

        decorated._decorated = True
        self.render = decorated

    def _apply_overrides(self):
        """Apply fiber overrides to App's direct attributes (not just props)."""
        overrides = self.fiber.overrides if self.fiber else None
        if overrides is None:
            return
        props_ov = overrides.get("props")
        if not props_ov:
            return
        # App stores page config as direct attributes, not in self.props
        for attr in ("page_title", "page_icon", "layout", "initial_sidebar_state", "menu_items"):
            if attr in props_ov:
                setattr(self, attr, props_ov[attr])
        if "color_mode" in props_ov:
            self.color_mode = props_ov["color_mode"]
            self._sync_session(ss.APP_COLOR_MODE, self.color_mode)
        if "theme" in props_ov:
            self.set_theme(props_ov["theme"])
        if "css" in props_ov:
            self.set_css(props_ov["css"])
        if "config" in props_ov:
            self.set_config(props_ov["config"])
        children_ov = overrides.get("children")
        if children_ov is not None:
            from .base import _auto_key_children
            self.props.children = list(children_ov)
            _auto_key_children(self.props.children)

    @property
    def root(self):
        if not self.children:
            return None
        return self.children[0]

    def __call__(self, *children):
        if len(children) != 1:
            raise TypeError("App expects exactly one child root.")
        from .base import _ensure_key
        child = children[0]
        _ensure_key(child)
        self.props.children = [child]
        return self

    def create_shared_state(self, namespace, spec):
        """Declare a named shared state namespace (in-memory, session-scoped)."""
        declare_shared_state(namespace, spec)
        return self

    def create_local_store(self, namespace, schema=None):
        """Declare a named localStorage namespace (browser-persisted).

        Same pattern as ``create_shared_state`` but persisted in the
        browser's ``localStorage``::

            class UserPrefs(LocalStore):
                theme: str = "light"
                font_size: int = 14

            app.create_local_store("prefs", UserPrefs)

            # Later, anywhere:
            prefs = get_local_store("prefs")
            prefs.theme = "dark"
        """
        from .local_storage import local_storage
        local_storage(namespace, schema)
        return self

    @staticmethod
    def get_local_store(namespace):
        """Return an existing localStorage namespace by name.

        ::

            prefs = App.get_local_store("prefs")
            prefs.theme = "dark"
        """
        from .local_storage import get_local_store as _get
        return _get(namespace)

    @staticmethod
    def clear_local_store(namespace):
        """Delete a localStorage namespace from the browser.

        ::

            App.clear_local_store("prefs")
        """
        from .local_storage import clear_local_storage as _clear
        _clear(namespace)

    def render_page(self, root):
        if self._active_router is not None and self._active_page is not None:
            return self._render_routed_root(
                self._active_router,
                self._active_page,
                root,
                wrappers=self._active_router_wrappers,
            )
        return self._render_root(root)

    @staticmethod
    def _recall_or(value, session_key):
        """Return session_state value if set, else fall back to constructor arg."""
        recalled = ss.get(session_key)
        return recalled if recalled is not None else value

    @staticmethod
    def _sync_session(session_key, value):
        """Sync *value* into session_state (or remove the key when None)."""
        ss.put_or_delete(session_key, value)

    _UNSET = object()

    def set_params(
        self,
        *,
        page_title=_UNSET,
        page_icon=_UNSET,
        layout=_UNSET,
        initial_sidebar_state=_UNSET,
        menu_items=_UNSET,
        theme=_UNSET,
        color_mode=_UNSET,
        css=_UNSET,
        config=_UNSET,
    ):
        """Update any app-level setting — same signature as the constructor.

        Only the provided params are changed; the rest are left untouched.
        Page config changes (layout, title, etc.) are applied immediately
        via ``st.set_page_config``.

        ::

            app.set_params(layout="centered", theme=Theme(base="dark"))
            app.set_params(page_title="New title", css="body { font-size: 18px; }")
        """
        _U = App._UNSET
        page_config = {}
        if page_title is not _U:
            self.page_title = page_title
            page_config["page_title"] = page_title
        if page_icon is not _U:
            self.page_icon = page_icon
            page_config["page_icon"] = page_icon
        if layout is not _U:
            self.layout = layout
            page_config["layout"] = layout
        if initial_sidebar_state is not _U:
            self.initial_sidebar_state = initial_sidebar_state
            page_config["initial_sidebar_state"] = initial_sidebar_state
        if menu_items is not _U:
            self.menu_items = menu_items
            page_config["menu_items"] = menu_items
        if page_config:
            st.set_page_config(**page_config)
        if color_mode is not _U:
            self.color_mode = color_mode
            self._sync_session(ss.APP_COLOR_MODE, color_mode)
        if theme is not _U:
            self.set_theme(theme)
        if css is not _U:
            self.set_css(css)
        if config is not _U:
            self.set_config(config)

        # Persist all changes as fiber overrides so they survive the next
        # App() instantiation in the script (which would otherwise overwrite).
        all_props = {}
        needs_rerun = False
        for k, v in [("page_title", page_title), ("page_icon", page_icon),
                      ("layout", layout), ("initial_sidebar_state", initial_sidebar_state),
                      ("menu_items", menu_items), ("theme", theme), ("color_mode", color_mode),
                      ("css", css), ("config", config)]:
            if v is not _U:
                all_props[k] = v
                if k in ("theme", "color_mode", "layout", "css"):
                    needs_rerun = True
        if all_props and self.fiber:
            overrides = self.fiber.overrides or {}
            overrides["props"] = {**(overrides.get("props") or {}), **all_props}
            self.fiber.overrides = overrides

        # Apply runtime changes immediately (config options, CSS injection)
        # then request a soft rerun so the frontend picks them up
        # without interrupting the current render
        if needs_rerun:
            self._apply_styles()
            from .rerun import rerun as _rerun
            _rerun(scope="app")

        return self

    def set_theme(self, theme):
        if isinstance(theme, dict) and not isinstance(theme, Theme):
            theme = Theme(theme)
        if theme is not None and not isinstance(theme, Theme):
            raise TypeError(f"App.set_theme(...) expects a dict or Theme, got {type(theme)}")
        self.theme = theme
        self._sync_session(self._THEME_STATE_KEY, theme)
        return self

    def save_theme(self, theme=None):
        if theme is not None:
            self.set_theme(theme)
        self._persist_theme_config()
        return self

    def set_css(self, css):
        self.css = css
        self._sync_session(self._CSS_STATE_KEY, css)
        return self

    def set_config(self, config):
        if isinstance(config, dict) and not isinstance(config, Config):
            config = Config(config)
        if config is not None and not isinstance(config, Config):
            raise TypeError(f"App.set_config(...) expects a dict or Config, got {type(config)}")
        self.config = config
        self._sync_session(self._CONFIG_STATE_KEY, config)
        return self

    def save_config(self, config=None):
        if config is not None:
            self.set_config(config)
        self._persist_app_config()
        return self

    def _load_theme_from_config(self):
        """Load Theme and color_mode from config files.

        Prefers ``.streamlit/stc-config.toml`` (full AppConfig).
        Falls back to ``.streamlit/config.toml`` ``[theme]`` (Streamlit flat theme).

        Returns ``(theme, color_mode)`` or ``(None, None)``.
        """
        # Prefer stc-config.toml
        cfg = AppConfig.load_toml(self._stc_config_path())
        if cfg.get("theme"):
            return cfg.theme, cfg.get("color_mode")

        # Fall back to Streamlit's flat [theme] in config.toml
        config_path = self._config_toml_path()
        if not config_path.exists():
            return None, None
        try:
            data = toml.loads(config_path.read_text())
        except Exception:
            return None, None

        flat = data.get("theme")
        if not flat:
            return None, None

        mode = flat.pop("base", "light") or "light"
        theme = Theme()
        palette = theme.active_colors(mode)
        for k, v in flat.items():
            if k == "sidebar":
                theme.sidebar = ThemeSection(v) if isinstance(v, dict) else v
            elif k in palette:
                palette[k] = v
            elif k in theme:
                theme[k] = v
        return theme, mode

    def _config_toml_path(self):
        return Path.cwd() / ".streamlit" / "config.toml"

    def _stc_config_path(self):
        return Path.cwd() / ".streamlit" / "stc-config.toml"

    def _to_app_config(self):
        """Snapshot current App settings into an AppConfig."""
        cfg = AppConfig()
        theme = self._theme_dict()
        if theme:
            cfg.theme = theme
        mode = getattr(self, "color_mode", None)
        if mode:
            cfg.color_mode = mode
        for field in ("page_title", "page_icon", "layout", "initial_sidebar_state"):
            val = getattr(self, field, None)
            if val is not None:
                cfg[field] = val
        css = self.css
        if isinstance(css, Path):
            cfg.css = str(css)
        elif isinstance(css, str):
            # Check if it looks like a file path
            candidate = Path(css)
            if candidate.suffix == ".css":
                cfg.css = css
        config = self._config_dict()
        if config:
            cfg.streamlit_config = config
        return cfg

    def _save_stc_config(self):
        """Persist all App settings to stc-config.toml."""
        self._to_app_config().dump_toml(self._stc_config_path())

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

    @staticmethod
    def _write_toml(path, updates):
        """Merge *updates* into a TOML file, writing only if changed."""
        existing_text = path.read_text() if path.exists() else ""
        existing_config = toml.loads(existing_text) if existing_text.strip() else {}
        rendered_config = dict(existing_config)
        for key, value in updates.items():
            rendered_config[key] = dict(value) if isinstance(value, dict) else value
        rendered = toml.dumps(rendered_config)
        if rendered != existing_text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered)

    def _persist_toml_section(self, updates):
        """Merge *updates* into .streamlit/config.toml."""
        self._write_toml(self._config_toml_path(), updates)

    def _persist_theme_config(self):
        theme = self._theme_dict()
        if not theme:
            return
        mode = getattr(self, "color_mode", "light") or "light"
        # .streamlit/config.toml — flat theme for Streamlit runtime
        if hasattr(theme, "flat"):
            self._persist_toml_section({"theme": theme.flat(mode)})
        else:
            self._persist_toml_section({"theme": dict(theme)})
        # .streamlit/stc-config.toml — full AppConfig
        self._save_stc_config()

    def _persist_app_config(self):
        config = self._config_dict()
        if config:
            self._persist_toml_section(config)
        self._save_stc_config()

    @staticmethod
    def _set_streamlit_options(prefix, data):
        """Recursively apply config options via streamlit.config.set_option()."""
        try:
            from streamlit import config as streamlit_config
        except Exception:
            return
        for key, value in data.items():
            option_key = f"{prefix}.{key}"
            if isinstance(value, dict):
                App._set_streamlit_options(option_key, value)
            else:
                streamlit_config.set_option(option_key, value)

    def _apply_theme_runtime(self):
        theme = self._theme_dict()
        if not theme:
            return
        if hasattr(theme, "flat"):
            # Flat top-level only — no light/dark sub-sections
            mode = getattr(self, "color_mode", "light") or "light"
            self._set_streamlit_options("theme", theme.flat(mode))
        else:
            self._set_streamlit_options("theme", theme)

    def _apply_config_runtime(self):
        client = self._config_dict().get("client", {})
        if client:
            self._set_streamlit_options("client", client)

    @staticmethod
    def _read_css_source(source):
        """Resolve a single CSS source to a string."""
        if isinstance(source, Path):
            return source.read_text()
        if isinstance(source, str):
            candidate = Path(source)
            if candidate.suffix == ".css" and candidate.exists():
                return candidate.read_text()
            return source
        raise TypeError(f"Unsupported css source type: {type(source)}")

    def _css_blocks(self):
        if self.css is None:
            return []
        sources = [self.css] if isinstance(self.css, (str, Path)) else list(self.css)
        return [block for block in map(self._read_css_source, sources) if block.strip()]

    def _apply_styles(self):
        self._apply_config_runtime()
        self._apply_theme_runtime()

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

    def _merged_page_config(self, page=None):
        """Build the full page config dict, merging app defaults with page overrides."""
        config = self._app_page_config()
        if page is not None:
            config.update(page.page_config())
            if "page_title" not in config and page.props.nav_title is not None:
                config["page_title"] = page.props.nav_title
            if "page_icon" not in config and page.props.nav_icon is not None:
                config["page_icon"] = page.props.nav_icon
        return config

    def _apply_page_config(self, page=None):
        config = self._merged_page_config(page)
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
        self._apply_overrides()
        track_rendered_fiber(self._fiber_key)

    def _render_with_cycle(self, body):
        begin_render_cycle()
        try:
            self._prepare_app_fiber()
            with set_context(key=self.key, component=self):
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

        if callable(source) and not isinstance(source, (Component, Element)):
            source = source()
            if inspect.isclass(source) and issubclass(source, Component):
                raise TypeError(
                    "Page factories must return instantiated Components, not Component classes."
                )

        if source is None:
            return None
        if router is not None and page is not None:
            return self._render_routed_root(router, page, source, wrappers=wrappers)
        return self._render_root(source)

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

    @staticmethod
    def _unwrap_router(root):
        """Walk through ContextProvider wrappers to find a Router root."""
        wrappers = []
        node = root

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

    # ── Streamlit APIs ─────────────────────────────────────────────────────

    from .streamlit_api import (
        secrets, cache_data, cache_resource,
    )

    @property
    def user(self):
        """Current user info (Streamlit Cloud auth)."""
        from .streamlit_api import get_user
        return get_user()

    @staticmethod
    def login(provider="google", **kwargs):
        """Trigger Streamlit Cloud login."""
        from .streamlit_api import login as _login
        _login(provider=provider, **kwargs)

    @staticmethod
    def logout():
        """Trigger Streamlit Cloud logout."""
        from .streamlit_api import logout as _logout
        _logout()

    @staticmethod
    def connection(name, type=None, **kwargs):
        """Create or retrieve a Streamlit connection."""
        from .streamlit_api import connection as _conn
        return _conn(name, type=type, **kwargs)

    @staticmethod
    def stop():
        """Stop script execution immediately."""
        from .streamlit_api import stop as _stop
        _stop()

    @property
    def request_context(self):
        """Current HTTP request context (headers, cookies)."""
        from .streamlit_api import get_request_context
        return get_request_context()

    # ── Rerun control ──────────────────────────────────────────────────────

    @staticmethod
    def rerun(scope="app", wait=True):
        """Request a rerun with optional scope and delay.

        ::

            app.rerun()                # soft rerun ASAP
            app.rerun("fragment")      # fragment-only rerun
            app.rerun(wait=1.5)        # rerun after 1.5s
            app.rerun(wait=False)      # immediate hard rerun
        """
        from .rerun import rerun as _rerun
        _rerun(scope=scope, wait=wait)

    @staticmethod
    def wait(delay=True, scope="app"):
        """Request a minimum delay before the next rerun of *scope*.

        ::

            st.toast("Saved!")
            app.wait(1.5)                    # app scope
            app.wait(0.5, scope="fragment")  # fragment scope
        """
        from .rerun import wait as _wait
        _wait(delay=delay, scope=scope)

    # ── Render ───────────────────────────────────────────────────────────

    def _run_app(self, root):
        """Run all App infrastructure around the rendered root."""
        wrappers, router = self._unwrap_router(root)

        try:
            if router is None:
                self._apply_page_config()
                self._apply_styles()
                return self._render_root(root)

            navigation_pages, page_map = self._build_navigation_pages(router, wrappers=wrappers)
            current = st.navigation(
                navigation_pages,
                position=router.props.position,
                expanded=router.props.expanded,
            )
            current_page = page_map.get(id(current))

            self._apply_page_config(current_page)
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
        finally:
            from .local_storage import render_local_storage
            from .rerun import check_rerun
            render_local_storage()
            check_rerun()

    def render(self):
        """Return the root of the app tree.

        Override in subclasses to build the tree dynamically.
        Default returns the child passed via ``App()(root)``.
        """
        return self.root
