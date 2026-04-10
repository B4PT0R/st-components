"""Data models backing the component engine.

Public (user-facing):
    Props, State, ContextData — base classes users subclass.
    Theme, ThemeSection, Config — app configuration.
    AppConfig — persistable stc-config.toml representation.

Internal (engine):
    HookSlot, Fiber, ElementFiber, ElementState — fiber/hook storage.
    Fibers, SharedStates — typed session_state containers.
    StreamlitTheme, StreamlitModeSection — Streamlit-side theme mapping.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal

import toml
from modict import modict


class Props(modict):
    """Immutable input data for a Component, passed at instantiation.

    ``key`` identifies the component among its siblings.  It can be omitted —
    an auto-key based on ``{classname}_{child_index}`` is assigned when the
    component is attached to a parent.  Explicit keys always take priority.

    Subclass to add typed fields with defaults::

        class CardProps(Props):
            title: str = "Untitled"
            bordered: bool = True
    """
    key: str | None = None
    children: list = modict.factory(list)

    @modict.validator("children")
    def _filter_none_children(self, value):
        return [c for c in value if c is not None]


class State(modict):
    """Mutable component state, persisted across Streamlit reruns.

    Subclass to declare typed fields with defaults::

        class CounterState(State):
            count: int = 0
            label: str = "clicks"
    """


class ContextData(modict):
    """Data carried by a context provider.  Subclass for typed fields::

        class ThemeData(ContextData):
            mode: str = "light"
            accent: str = "blue"
    """


class HookSlot(modict):
    """Single hook instance stored in a fiber's hooks list.

    Fields: kind (memo/ref/effect/state/id), value, deps, cleanup callback.
    """
    _config = modict.config(require_all="never")

    kind: str = modict.field(required="always")
    initialized: bool = False
    value: Any = None
    deps: Any = None
    cleanup: Any = None


class Fiber(modict):
    """Persistent state holder for a Component across Streamlit reruns.

    Stored in ``session_state`` keyed by the component's tree path.
    The Python Component instance is ephemeral (recreated each rerun);
    the Fiber is the source of truth for state, hooks, and overrides.
    """
    state: State = modict.factory(State)
    component_id: str | None = None
    previous_state: State | None = None
    keep_alive: bool = False
    overrides: dict | None = None
    hooks: list[HookSlot] = modict.factory(list)


class ElementState(State):
    """Frozen state for Elements — only writable during render via ``_writable()``.

    ``output`` holds the widget's current value; ``handle`` the Streamlit
    container object (for layout elements like ``st.container``).
    """

    _config = modict.config(frozen=True)

    output: Any = None
    handle: Any = None

    @contextmanager
    def _writable(self):
        """Temporarily lift the frozen constraint for the render phase."""
        saved_frozen = self._config.frozen
        self._config.frozen = False
        try:
            yield self
        finally:
            self._config.frozen = saved_frozen


class ElementFiber(Fiber):
    """Fiber subclass for Elements — adds ``path`` and ``widget_key``."""
    path: str = modict.field(required="always")
    widget_key: str | None = None
    state: State = modict.factory(ElementState)


class Fibers(modict[str, Fiber]):
    """Session-scoped container mapping tree paths to Fiber instances."""


class SharedStates(modict[str, State]):
    """Session-scoped container mapping namespace names to shared State instances."""



# --- Config & Theme models ---
# Base classes that auto-prune None or empty values after init.

class _PruneNone(modict):
    """Base for config/theme models: removes None-valued keys after init."""
    _config = modict.config(require_all="never")

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class _PruneEmpty(modict):
    """Base for container models: removes None, empty dict, and empty list values after init."""
    _config = modict.config(require_all="never")

    @modict.model_validator(mode="after")
    def _prune_empty_fields(self):
        for key in list(self.keys()):
            value = self[key]
            if value is None or value == {} or value == []:
                del self[key]


class ClientConfig(_PruneNone):
    showErrorDetails: Literal["full", "stacktrace", "type", "none"] | bool | None = None
    showErrorLinks: Literal["auto"] | bool | None = None
    showSidebarNavigation: bool | None = None
    toolbarMode: Literal["auto", "developer", "viewer", "minimal"] | None = None


class RunnerConfig(_PruneNone):
    fastReruns: bool | None = None
    enforceSerializableSessionState: bool | None = None
    enumCoercion: Literal["off", "nameOnly", "nameAndValue"] | None = None


class BrowserConfig(_PruneNone):
    gatherUsageStats: bool | None = None


class ServerConfig(_PruneNone):
    runOnSave: bool | None = None


class Config(_PruneEmpty):
    client: ClientConfig | None = None
    runner: RunnerConfig | None = None
    browser: BrowserConfig | None = None
    server: ServerConfig | None = None


class ThemeSection(_PruneNone):
    """Overridable theme fields.

    Used for ``[theme]`` base, ``[theme.light]``/``[theme.dark]`` mode overrides,
    ``[theme.sidebar]`` / ``[theme.light.sidebar]`` / ``[theme.dark.sidebar]``.
    All fields are optional — only set values are emitted.
    """
    # Core colors
    primaryColor: str | None = None
    backgroundColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    borderColor: str | None = None

    # Link & code
    linkColor: str | None = None
    linkUnderline: bool | None = None
    codeTextColor: str | None = None
    codeBackgroundColor: str | None = None

    # Semantic palette — base, background, and text variants
    redColor: str | None = None
    redBackgroundColor: str | None = None
    redTextColor: str | None = None
    orangeColor: str | None = None
    orangeBackgroundColor: str | None = None
    orangeTextColor: str | None = None
    yellowColor: str | None = None
    yellowBackgroundColor: str | None = None
    yellowTextColor: str | None = None
    blueColor: str | None = None
    blueBackgroundColor: str | None = None
    blueTextColor: str | None = None
    greenColor: str | None = None
    greenBackgroundColor: str | None = None
    greenTextColor: str | None = None
    violetColor: str | None = None
    violetBackgroundColor: str | None = None
    violetTextColor: str | None = None
    grayColor: str | None = None
    grayBackgroundColor: str | None = None
    grayTextColor: str | None = None

    # Dataframe
    dataframeBorderColor: str | None = None
    dataframeHeaderBackgroundColor: str | None = None

    # Shape (can be overridden per section)
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None

    # Font (can be overridden per section)
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    headingFontSizes: list[str] | None = None
    headingFontWeights: list[int] | int | None = None
    codeFontSize: str | int | float | None = None
    codeFontWeight: int | None = None

    # Charts (mode-specific defaults differ)
    chartCategoricalColors: list[str] | None = None
    chartSequentialColors: list[str] | None = None
    chartDivergingColors: list[str] | None = None


class ThemeFontFace(_PruneNone):
    family: str | None = None
    url: str | None = None
    weight: str | int | None = None
    style: str | None = None
    unicodeRange: str | None = None


# ── Native Streamlit color presets ──────────────────────────────────────────
# Source: streamlit/frontend/lib/src/theme/primitives/colors.ts
# Only values that DIFFER between modes need explicit presets.
# Fields left as None let Streamlit derive them from the core colors.

_LIGHT_COLORS = ThemeSection(
    # Core
    primaryColor="#ff4b4b",
    backgroundColor="#ffffff",
    secondaryBackgroundColor="#f0f2f6",
    textColor="#31333F",
    borderColor="#e6eaf1",
    # Semantic — only values that differ between modes
    redColor="#ff4b4b",
    orangeColor="#ffa421",
    yellowColor="#faca2b",
    greenColor="#21c354",
    blueColor="#1c83e1",
    grayColor="#a3a8b8",
    redTextColor="#bd4043",
    orangeTextColor="#e2660c",
    yellowTextColor="#926c05",
    greenTextColor="#158237",
    blueTextColor="#0054a3",
    violetTextColor="#583f84",
    # Charts — light: light→dark gradient (dark values stand out on white)
    chartCategoricalColors=[
        "#0068c9", "#83c9ff", "#ff2b2b", "#ffabab", "#29b09d",
        "#7defa1", "#ff8700", "#ffd16a", "#6d3fc0", "#d5dae5",
    ],
    chartSequentialColors=[
        "#e4f5ff", "#c7ebff", "#a6dcff", "#83c9ff", "#60b4ff",
        "#3d9df3", "#1c83e1", "#0068c9", "#0054a3", "#004280",
    ],
    chartDivergingColors=[
        "#7d353b", "#bd4043", "#ff4b4b", "#ff8c8c", "#ffc7c7",
        "#a6dcff", "#60b4ff", "#1c83e1", "#0054a3", "#004280",
    ],
)

_DARK_COLORS = ThemeSection(
    # Core
    primaryColor="#ff4b4b",
    backgroundColor="#0e1117",
    secondaryBackgroundColor="#262730",
    textColor="#fafafa",
    borderColor="#555867",
    # Semantic — only values that differ between modes
    redColor="#ff2b2b",
    orangeColor="#ff8700",
    yellowColor="#ffe312",
    greenColor="#09ab3b",
    blueColor="#0068c9",
    grayColor="#555867",
    redTextColor="#ff6c6c",
    orangeTextColor="#ffbd45",
    yellowTextColor="#ffffc2",
    greenTextColor="#5ce488",
    blueTextColor="#3d9df3",
    violetTextColor="#b27eff",
    # Charts — dark: reversed gradient (light values stand out on dark bg)
    chartCategoricalColors=[
        "#83c9ff", "#0068c9", "#ffabab", "#ff2b2b", "#7defa1",
        "#29b09d", "#ffd16a", "#ff8700", "#6d3fc0", "#d5dae5",
    ],
    chartSequentialColors=[
        "#004280", "#0054a3", "#0068c9", "#1c83e1", "#3d9df3",
        "#60b4ff", "#83c9ff", "#a6dcff", "#c7ebff", "#e4f5ff",
    ],
    chartDivergingColors=[
        "#7d353b", "#bd4043", "#ff4b4b", "#ff8c8c", "#ffc7c7",
        "#a6dcff", "#60b4ff", "#1c83e1", "#0054a3", "#004280",
    ],
)

# Fields only valid at theme.* level (not in theme.light.*/theme.dark.*)
_TOP_LEVEL_ONLY = frozenset({
    "base", "baseFontSize", "baseFontWeight", "fontFaces",
    "chartCategoricalColors", "chartSequentialColors", "chartDivergingColors",
    "metricValueFontSize", "metricValueFontWeight", "showSidebarBorder",
})


class Theme(_PruneEmpty):
    """App theme mirroring Streamlit's config.toml ``[theme]`` structure.

    Maps 1:1 to the TOML sections::

        [theme]           → Theme top-level fields (base, shared settings, fallback colors)
        [theme.light]     → Theme.light   (mode overrides)
        [theme.dark]      → Theme.dark    (mode overrides)
        [theme.sidebar]   → Theme.sidebar (global sidebar overrides)
        [theme.light.sidebar]  → Theme.light_sidebar  (sidebar in light mode)
        [theme.dark.sidebar]   → Theme.dark_sidebar   (sidebar in dark mode)

    Usage::

        theme = Theme()
        theme.light.primaryColor = "#ff0000"
        theme.dark.backgroundColor = "#111111"
        theme.light_sidebar.backgroundColor = "#eee"

        app = App(theme=theme, color_mode="dark")
    """
    # ── [theme] top-level only ──────────────────────────────────────────
    baseFontSize: str | int | float | None = None
    baseFontWeight: int | None = None
    metricValueFontSize: str | int | float | None = None
    metricValueFontWeight: int | None = None
    showSidebarBorder: bool | None = None
    chartCategoricalColors: list[str] | None = None
    chartSequentialColors: list[str] | None = None
    chartDivergingColors: list[str] | None = None
    fontFaces: list[ThemeFontFace] | None = None

    # ── [theme] fallback (also overridable in light/dark) ───────────────
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    headingFontSizes: list[str] | None = None
    headingFontWeights: list[int] | int | None = None
    codeFontSize: str | int | float | None = None
    codeFontWeight: int | None = None
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None

    # ── [theme.light] / [theme.dark] ───────────────────────────────────
    light: ThemeSection = modict.factory(lambda: ThemeSection(_LIGHT_COLORS))
    dark: ThemeSection = modict.factory(lambda: ThemeSection(_DARK_COLORS))

    # ── [theme.sidebar] ────────────────────────────────────────────────
    sidebar: ThemeSection | None = None

    # ── [theme.light.sidebar] / [theme.dark.sidebar] ──────────────────
    light_sidebar: ThemeSection | None = None
    dark_sidebar: ThemeSection | None = None

    def active_colors(self, mode="light"):
        """Return the mode palette (``light`` or ``dark``)."""
        return self.dark if mode == "dark" else self.light

    def active_sidebar(self, mode="light"):
        """Return the sidebar section for the given mode."""
        return self.get("dark_sidebar") if mode == "dark" else self.get("light_sidebar")

    def flat(self, mode="light"):
        """Flat dict for ``config.set_option`` at runtime.

        Merges: base → active mode colors → shared settings → sidebar.
        No ``light``/``dark`` sub-sections.
        """
        _INTERNAL = ("light", "dark", "sidebar", "fontFaces",
                     "light_sidebar", "dark_sidebar")

        active = dict(self.active_colors(mode))
        # Remove sidebar from palette dict (it's a ThemeSection, not a flat key)
        active.pop("sidebar", None)
        shared = {k: v for k, v in self.items()
                  if k not in _INTERNAL and v is not None}
        result = {"base": mode, **active, **shared}

        # Merge sidebar: global → mode-specific
        sidebar_result = {}
        global_sidebar = self.get("sidebar")
        if global_sidebar:
            sidebar_result.update(global_sidebar)
        mode_sidebar = self.active_sidebar(mode)
        if mode_sidebar:
            sidebar_result.update(mode_sidebar)
        if sidebar_result:
            result["sidebar"] = sidebar_result

        return result

    def to_streamlit(self, mode="light"):
        """Convert to a ``StreamlitTheme`` for config.toml / ``set_option``.

        Returns a fully typed ``StreamlitTheme`` with all sub-sections.
        """
        data = self.flat(mode)

        # [theme.light] / [theme.dark] — filter out top-level-only fields
        light_data = {k: v for k, v in self.light.items()
                      if k not in _TOP_LEVEL_ONLY}
        dark_data = {k: v for k, v in self.dark.items()
                     if k not in _TOP_LEVEL_ONLY}

        # [theme.light.sidebar] / [theme.dark.sidebar]
        ls = self.get("light_sidebar")
        ds = self.get("dark_sidebar")
        if ls:
            light_data["sidebar"] = dict(ls)
        if ds:
            dark_data["sidebar"] = dict(ds)

        data["light"] = light_data
        data["dark"] = dark_data

        return StreamlitTheme(data)

    def dumps(self):
        """Serialize to a plain dict suitable for TOML persistence.

        Nested ThemeSections are flattened to plain dicts.
        """
        result = {}
        for k, v in self.items():
            if isinstance(v, modict):
                result[k] = dict(v)
            elif isinstance(v, list):
                result[k] = [dict(i) if isinstance(i, modict) else i for i in v]
            else:
                result[k] = v
        return result

    @classmethod
    def loads(cls, data):
        """Deserialize from a plain dict (e.g. read from TOML).

        Modict coercion converts nested dicts back to ThemeSections.
        """
        if not data:
            return cls()
        return cls(data)


# ── Streamlit-side theme structure ──────────────────────────────────────────

class StreamlitSidebarSection(_PruneNone):
    """``[theme.sidebar]`` / ``[theme.light.sidebar]`` / ``[theme.dark.sidebar]``."""
    backgroundColor: str | None = None
    primaryColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    borderColor: str | None = None


class StreamlitModeSection(_PruneEmpty):
    """``[theme.light]`` or ``[theme.dark]`` — overrides for one mode."""
    _config = modict.config(require_all="never")

    primaryColor: str | None = None
    backgroundColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    borderColor: str | None = None
    linkColor: str | None = None
    linkUnderline: bool | None = None
    codeTextColor: str | None = None
    codeBackgroundColor: str | None = None
    redColor: str | None = None
    redBackgroundColor: str | None = None
    redTextColor: str | None = None
    orangeColor: str | None = None
    orangeBackgroundColor: str | None = None
    orangeTextColor: str | None = None
    yellowColor: str | None = None
    yellowBackgroundColor: str | None = None
    yellowTextColor: str | None = None
    blueColor: str | None = None
    blueBackgroundColor: str | None = None
    blueTextColor: str | None = None
    greenColor: str | None = None
    greenBackgroundColor: str | None = None
    greenTextColor: str | None = None
    violetColor: str | None = None
    violetBackgroundColor: str | None = None
    violetTextColor: str | None = None
    grayColor: str | None = None
    grayBackgroundColor: str | None = None
    grayTextColor: str | None = None
    dataframeBorderColor: str | None = None
    dataframeHeaderBackgroundColor: str | None = None
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    headingFontSizes: list[str] | None = None
    headingFontWeights: list[int] | int | None = None
    codeFontSize: str | int | float | None = None
    codeFontWeight: int | None = None
    sidebar: StreamlitSidebarSection | None = None


class StreamlitTheme(_PruneEmpty):
    """Typed representation of Streamlit's ``[theme]`` config.toml structure.

    Maps 1:1 to the TOML sections that ``config.set_option`` accepts::

        [theme]               → top-level fields
        [theme.light]         → StreamlitTheme.light
        [theme.dark]          → StreamlitTheme.dark
        [theme.sidebar]       → StreamlitTheme.sidebar
        [theme.light.sidebar] → StreamlitTheme.light.sidebar
        [theme.dark.sidebar]  → StreamlitTheme.dark.sidebar
    """
    # ── top-level only ──────────────────────────────────────────────────
    base: str | None = None
    baseFontSize: str | int | float | None = None
    baseFontWeight: int | None = None
    metricValueFontSize: str | int | float | None = None
    metricValueFontWeight: int | None = None
    showSidebarBorder: bool | None = None
    chartCategoricalColors: list[str] | None = None
    chartSequentialColors: list[str] | None = None
    chartDivergingColors: list[str] | None = None
    fontFaces: list[ThemeFontFace] | None = None

    # ── top-level fallback (also valid in light/dark) ───────────────────
    primaryColor: str | None = None
    backgroundColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    borderColor: str | None = None
    linkColor: str | None = None
    linkUnderline: bool | None = None
    codeTextColor: str | None = None
    codeBackgroundColor: str | None = None
    redColor: str | None = None
    redBackgroundColor: str | None = None
    redTextColor: str | None = None
    orangeColor: str | None = None
    orangeBackgroundColor: str | None = None
    orangeTextColor: str | None = None
    yellowColor: str | None = None
    yellowBackgroundColor: str | None = None
    yellowTextColor: str | None = None
    blueColor: str | None = None
    blueBackgroundColor: str | None = None
    blueTextColor: str | None = None
    greenColor: str | None = None
    greenBackgroundColor: str | None = None
    greenTextColor: str | None = None
    violetColor: str | None = None
    violetBackgroundColor: str | None = None
    violetTextColor: str | None = None
    grayColor: str | None = None
    grayBackgroundColor: str | None = None
    grayTextColor: str | None = None
    dataframeBorderColor: str | None = None
    dataframeHeaderBackgroundColor: str | None = None
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    headingFontSizes: list[str] | None = None
    headingFontWeights: list[int] | int | None = None
    codeFontSize: str | int | float | None = None
    codeFontWeight: int | None = None

    # ── sub-sections ────────────────────────────────────────────────────
    light: StreamlitModeSection | None = None
    dark: StreamlitModeSection | None = None
    sidebar: StreamlitSidebarSection | None = None

    def to_theme(self):
        """Convert to the st-components ``Theme`` model.

        Distributes top-level color fallbacks + mode overrides into
        ``Theme.light`` / ``Theme.dark`` palettes, and sidebar sections
        into ``Theme.light_sidebar`` / ``Theme.dark_sidebar``.
        """
        theme = Theme()

        # Collect top-level color/overridable fields (fallback)
        fallback = {k: v for k, v in self.items()
                    if k not in ("light", "dark", "sidebar", "fontFaces", "base")
                    and k not in _TOP_LEVEL_ONLY and v is not None}

        # Build each mode palette: preset defaults ← fallback ← mode overrides
        for mode_name in ("light", "dark"):
            palette = theme.active_colors(mode_name)
            # Apply top-level fallbacks
            for k, v in fallback.items():
                palette[k] = v
            # Apply mode-specific overrides
            mode_section = self.get(mode_name)
            if mode_section:
                sidebar_data = mode_section.get("sidebar")
                for k, v in mode_section.items():
                    if k != "sidebar":
                        palette[k] = v
                if sidebar_data:
                    theme[f"{mode_name}_sidebar"] = ThemeSection(sidebar_data)

        # Top-level-only shared settings
        for field in _TOP_LEVEL_ONLY:
            if field in ("base",):
                continue
            val = self.get(field)
            if val is not None:
                theme[field] = val

        # Top-level overridable settings that go on Theme (not in palettes)
        for field in ("font", "headingFont", "codeFont", "baseFontSize", "baseFontWeight",
                      "headingFontSizes", "headingFontWeights", "codeFontSize", "codeFontWeight",
                      "metricValueFontSize", "metricValueFontWeight",
                      "showWidgetBorder", "showSidebarBorder", "baseRadius", "buttonRadius"):
            val = self.get(field)
            if val is not None:
                theme[field] = val

        # Global sidebar
        global_sidebar = self.get("sidebar")
        if global_sidebar:
            theme.sidebar = ThemeSection(global_sidebar)

        # fontFaces
        ff = self.get("fontFaces")
        if ff:
            theme.fontFaces = ff

        return theme


# ── App-level config (persisted to stc-config.toml) ────────────────────────

class AppConfig(_PruneEmpty):
    """All persistable App settings, stored in ``.streamlit/stc-config.toml``.

    ::

        cfg = AppConfig.load_toml()       # read from stc-config.toml
        cfg.color_mode = "dark"
        cfg.dump_toml()                    # write back
    """
    # Theme
    theme: Theme | None = None
    color_mode: str | None = None

    # Page config
    page_title: str | None = None
    page_icon: str | None = None
    layout: str | None = None
    initial_sidebar_state: str | None = None

    # CSS file path (relative to cwd, created empty if absent)
    css: str = ".streamlit/styles.css"

    # Streamlit config overrides ([server], [client], etc.)
    streamlit_config: Config | None = None

    _STC_PATH = Path(".streamlit") / "stc-config.toml"

    def dump_toml(self, path=None):
        """Persist to stc-config.toml."""
        path = Path(path) if path else Path.cwd() / self._STC_PATH
        data = {}
        theme = self.get("theme")
        if theme:
            theme_data = theme.dumps() if hasattr(theme, "dumps") else dict(theme)
            mode = self.get("color_mode")
            if mode:
                theme_data["color_mode"] = mode
            data["theme"] = theme_data
        # Page config
        page = {}
        for field in ("page_title", "page_icon", "layout", "initial_sidebar_state"):
            val = self.get(field)
            if val is not None:
                page[field] = val
        if page:
            data["page"] = page
        # CSS file path — ensure the file exists
        css = self.get("css")
        if css:
            css_path = Path.cwd() / css
            css_path.parent.mkdir(parents=True, exist_ok=True)
            if not css_path.exists():
                css_path.write_text("")
            data["css"] = {"path": str(css)}
        # Streamlit config
        st_config = self.get("streamlit_config")
        if st_config:
            data["streamlit_config"] = dict(st_config)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(toml.dumps(data))

    @classmethod
    def load_toml(cls, path=None):
        """Load from stc-config.toml."""
        path = Path(path) if path else Path.cwd() / cls._STC_PATH
        if not path.exists():
            return cls()
        try:
            data = toml.loads(path.read_text())
        except Exception:
            return cls()

        result = cls()

        # Theme + color_mode
        theme_data = data.get("theme")
        if theme_data:
            mode = theme_data.pop("color_mode", None)
            result.theme = Theme.loads(theme_data)
            if mode:
                result.color_mode = mode

        # Page config
        page = data.get("page") or {}
        for field in ("page_title", "page_icon", "layout", "initial_sidebar_state"):
            val = page.get(field)
            if val is not None:
                result[field] = val

        # CSS file path — ensure the file exists
        css_section = data.get("css")
        if css_section:
            css_path_str = css_section.get("path")
            if css_path_str:
                result.css = css_path_str
                css_file = Path.cwd() / css_path_str
                css_file.parent.mkdir(parents=True, exist_ok=True)
                if not css_file.exists():
                    css_file.write_text("")

        # Streamlit config
        config_data = data.get("streamlit_config")
        if config_data:
            result.streamlit_config = Config(config_data)

        return result
