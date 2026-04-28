from pathlib import Path

import streamlit as st
from modict import modict

from ..core import Component, Props, Ref, State, Theme, get_app
from ..core.models import ThemeSection
from ..elements import (
    button,
    color_picker,
    columns,
    container,
    dialog,
    markdown,
    number_input,
    selectbox,
    subheader,
    text_area,
    toggle,
)


_MODE_OPTIONS = ["light", "dark"]
_FONT_OPTIONS = ["sans-serif", "serif", "monospace"]
_RADIUS_OPTIONS = ["none", "small", "medium", "large", "full"]

# Color fields that live in the mode palette
_PALETTE_FIELDS = (
    "primaryColor",
    "backgroundColor",
    "secondaryBackgroundColor",
    "textColor",
    "borderColor",
    "codeBackgroundColor",
)

# Shared fields that live on Theme (mode-independent)
_SHARED_FIELDS = ("font", "baseFontSize", "baseRadius", "buttonRadius", "showWidgetBorder")

# All color fields shown in the editor (palette + sidebar)
_ALL_COLOR_FIELDS = (*_PALETTE_FIELDS, "sidebarBackgroundColor")  # codeBackgroundColor already in _PALETTE_FIELDS


class ThemeEditorRefs(modict):
    mode: Ref = modict.factory(Ref)
    font: Ref = modict.factory(Ref)
    baseFontSize: Ref = modict.factory(Ref)
    primaryColor: Ref = modict.factory(Ref)
    backgroundColor: Ref = modict.factory(Ref)
    secondaryBackgroundColor: Ref = modict.factory(Ref)
    textColor: Ref = modict.factory(Ref)
    borderColor: Ref = modict.factory(Ref)
    codeBackgroundColor: Ref = modict.factory(Ref)
    sidebarBackgroundColor: Ref = modict.factory(Ref)
    baseRadius: Ref = modict.factory(Ref)
    buttonRadius: Ref = modict.factory(Ref)
    showWidgetBorder: Ref = modict.factory(Ref)


class ThemeEditorValues(modict):
    """Flat editor state — combines the active palette colors + shared settings."""
    mode: str = "light"
    font: str = "sans-serif"
    baseFontSize: int = 16
    primaryColor: str = "#ff4b4b"
    backgroundColor: str = "#ffffff"
    secondaryBackgroundColor: str = "#f0f2f6"
    textColor: str = "#31333F"
    borderColor: str = "#e6eaf1"
    codeBackgroundColor: str = "#f0f2f6"
    sidebarBackgroundColor: str = "#f0f2f6"
    baseRadius: str = "medium"
    buttonRadius: str = "medium"
    showWidgetBorder: bool = True


class ThemeEditorFlags(modict):
    initialized: bool = False
    save_requested: bool = False


def _option_index(options, value):
    try:
        return list(options).index(value)
    except ValueError:
        return 0


def _sidebar_bg(theme, mode):
    """Resolve sidebar backgroundColor: mode sidebar → global sidebar → palette fallback."""
    mode_sb = theme.active_sidebar(mode)
    if mode_sb and "backgroundColor" in mode_sb:
        return mode_sb.backgroundColor
    global_sb = theme.get("sidebar")
    if global_sb and "backgroundColor" in global_sb:
        return global_sb.backgroundColor
    return theme.active_colors(mode).get("secondaryBackgroundColor", "#f0f2f6")


def _read_values(theme, mode):
    """Read flat editor values from a Theme + active mode."""
    if theme is None:
        theme = Theme()
    palette = theme.active_colors(mode)
    values = ThemeEditorValues(mode=mode)
    for field in _PALETTE_FIELDS:
        if field in palette:
            values[field] = palette[field]
    values.sidebarBackgroundColor = _sidebar_bg(theme, mode)
    for field in _SHARED_FIELDS:
        if field in theme:
            values[field] = theme[field]
    return values


def _write_values(values, existing_theme):
    """Write flat editor values back into a deep-copied Theme."""
    theme = Theme.loads(existing_theme.dumps())
    mode = values.mode
    palette = theme.active_colors(mode)

    for field in _PALETTE_FIELDS:
        if field in values:
            palette[field] = values[field]

    # Sidebar background → mode-specific sidebar section
    sidebar_bg = values.get("sidebarBackgroundColor")
    if sidebar_bg:
        sidebar_attr = "dark_sidebar" if mode == "dark" else "light_sidebar"
        existing = theme.get(sidebar_attr)
        if existing is None:
            theme[sidebar_attr] = ThemeSection(backgroundColor=sidebar_bg)
        else:
            existing.backgroundColor = sidebar_bg

    # Shared fields — only write if already on theme or changed from defaults
    defaults = ThemeEditorValues()
    for field in _SHARED_FIELDS:
        val = values.get(field)
        if val is not None and (field in theme or val != defaults.get(field)):
            theme[field] = val

    return theme


class ThemeEditor(Component):
    class ThemeEditorProps(Props):
        pass

    class ThemeEditorState(State):
        editor: ThemeEditorValues = modict.factory(ThemeEditorValues)
        flags: ThemeEditorFlags = modict.factory(ThemeEditorFlags)
        refs: ThemeEditorRefs = modict.factory(ThemeEditorRefs)

    def __init__(self, **props):
        super().__init__(**props)
        self._refs = self.state.refs

    def _theme(self):
        return get_app().theme or Theme()

    def _mode(self):
        return getattr(get_app(), "color_mode", "light") or "light"

    def _load_editor(self, theme, css_text=""):
        """Load editor state from a Theme — used at init, reset, and mode switch."""
        self.state.editor = _read_values(theme, self._mode())

    def _refresh_refs(self, *fields):
        """Reset widget values so they re-read the new value prop."""
        for field in fields:
            ref = self._refs[field]
            try:
                ref.reset_widget()
            except (RuntimeError, AttributeError):
                ref.reset()

    def _sync_mode(self, mode):
        """Switch color mode: save current edits, load the other palette."""
        # _bind_editor already set editor.mode = mode — restore old mode to save edits
        self.state.editor.mode = self._mode()
        theme = _write_values(self.state.editor, self._theme())
        get_app().set_theme(theme)

        # Load the new mode's values from the updated theme
        self.state.editor = _read_values(theme, mode)
        self._refresh_refs(*_ALL_COLOR_FIELDS, "mode")

    def _bind_editor(self, field, after=None):
        def sync(value):
            self.state.editor.update(**{field: value})
            if after is not None:
                after(value)
        return sync

    def _save(self):
        self.state.flags.update(save_requested=True)

    def _reset(self):
        self._load_editor(Theme())
        self._refresh_refs(*self._refs.keys())

    def _palette_picker(self, *, ui_key, field, label, values):
        return color_picker(
            key=ui_key,
            ref=self._refs[field],
            value=values[field],
            on_change=self._bind_editor(field),
        )(label)

    def _foundation_panel(self, values):
        return container(key="foundation", border=True, height="stretch")(
            subheader(key="title")("Foundation"),
            markdown(key="body")("Color mode, font family and root text size."),
            selectbox(
                key="mode",
                ref=self._refs["mode"],
                options=_MODE_OPTIONS,
                index=_option_index(_MODE_OPTIONS, values["mode"]),
                on_change=self._bind_editor("mode", after=self._sync_mode),
            )("Color mode"),
            selectbox(
                key="font",
                ref=self._refs["font"],
                options=_FONT_OPTIONS,
                index=_option_index(_FONT_OPTIONS, values.get("font", "sans-serif")),
                on_change=self._bind_editor("font"),
            )("Font"),
            number_input(
                key="font_size",
                ref=self._refs["baseFontSize"],
                min_value=12,
                max_value=24,
                step=1,
                value=values["baseFontSize"],
                on_change=self._bind_editor("baseFontSize"),
            )("Base font size"),
        )

    def _colors_panel(self, values):
        return container(key="colors", border=True)(
            subheader(key="title")("Colors"),
            markdown(key="body")(f"Palette for **{values['mode']}** mode."),
            container(
                key="palette",
                horizontal=True,
                horizontal_alignment="distribute",
                gap="small",
                width="stretch",
            )(
                self._palette_picker(ui_key="primary", field="primaryColor", label="Primary", values=values),
                self._palette_picker(ui_key="background", field="backgroundColor", label="Background", values=values),
                self._palette_picker(ui_key="surface", field="secondaryBackgroundColor", label="Surface", values=values),
                self._palette_picker(ui_key="text", field="textColor", label="Text", values=values),
                self._palette_picker(ui_key="border", field="borderColor", label="Border", values=values),
                self._palette_picker(ui_key="code_bg", field="codeBackgroundColor", label="Code bg", values=values),
                self._palette_picker(ui_key="sidebar_bg", field="sidebarBackgroundColor", label="Sidebar", values=values),
            ),
        )

    def _shape_panel(self, values):
        return container(key="shape", border=True, height="stretch")(
            subheader(key="title")("Shape"),
            markdown(key="body")("Corner radii and widget framing."),
            selectbox(
                key="base_radius",
                ref=self._refs["baseRadius"],
                options=_RADIUS_OPTIONS,
                index=_option_index(_RADIUS_OPTIONS, values["baseRadius"]),
                on_change=self._bind_editor("baseRadius"),
            )("Base radius"),
            selectbox(
                key="button_radius",
                ref=self._refs["buttonRadius"],
                options=_RADIUS_OPTIONS,
                index=_option_index(_RADIUS_OPTIONS, values["buttonRadius"]),
                on_change=self._bind_editor("buttonRadius"),
            )("Button radius"),
            toggle(key="widget_border", ref=self._refs["showWidgetBorder"], value=values["showWidgetBorder"], on_change=self._bind_editor("showWidgetBorder"))("Show widget borders"),
        )

    def _actions_bar(self):
        return container(
            key="actions",
            horizontal=True,
            horizontal_alignment="distribute",
            gap="small",
            width="stretch",
        )(
            button(key="save", on_click=self._save, type="primary")("Save"),
            button(key="reset", on_click=self._reset, type="secondary")("Reset"),
        )

    def _layout(self, values):
        return container(
            key="editor_layout",
            gap="small",
        )(
            columns(key="top_grid", gap="small")(
                self._foundation_panel(values),
                self._shape_panel(values),
            ),
            self._colors_panel(values),
            self._actions_bar(),
        )

    def render(self):
        theme = self._theme()
        mode = self._mode()
        if not self.state.flags.initialized:
            self._load_editor(theme)
            self.state.flags.initialized = True

        next_theme = _write_values(self.state.editor, theme)
        next_mode = self.state.editor.mode
        theme_changed = next_theme != theme
        mode_changed = next_mode != mode

        if theme_changed or mode_changed or self.state.flags.save_requested:
            if theme_changed:
                get_app().set_theme(next_theme)
            if mode_changed:
                get_app().set_params(color_mode=next_mode)
            if self.state.flags.save_requested:
                get_app().save_theme()
                self.state.flags.save_requested = False
            get_app().rerun(wait=False)

        return self._layout(self.state.editor)


class ThemeEditorDialog(Component):

    class ThemeEditorDialogProps(Props):
        open: bool = False
        title: str = "Theme editor"
        width: str = "large"

    def render(self):
        if not self.props.open:
            return None
        dialog_props = self.props.exclude("key", "children", "open")
        return dialog(key="dialog", **dialog_props)(
            ThemeEditor(key="editor")
        )


class ThemeEditorButton(Component):

    class ThemeEditorButtonProps(Props):
        label: str = "Edit theme"
        title: str = "Theme editor"
        width: str = "large"
        type: str = "secondary"
        help: str | None = None
        icon: str | None = None
        use_container_width: bool | None = None
        disabled: bool = False
        shortcut: str | None = None

    class ThemeEditorButtonState(State):
        open: bool = False

    def _open(self):
        self.state.open = True

    def _close(self):
        self.state.open = False
        on_dismiss = self.props.get("on_dismiss")
        if callable(on_dismiss):
            on_dismiss()

    def render(self):
        label = self.children[0] if self.children else self.props.label
        trigger = button(
            key="trigger",
            on_click=self._open,
            type=self.props.type,
            help=self.props.help,
            icon=self.props.icon,
            use_container_width=self.props.use_container_width,
            disabled=self.props.disabled,
            shortcut=self.props.shortcut,
        )(label)
        if not self.state.open:
            return trigger
        return (
            trigger,
            ThemeEditorDialog(
                key="dialog",
                open=True,
                title=self.props.title,
                width=self.props.width,
                on_dismiss=self._close,
            ),
        )


# ── CSS Editor ──────────────────────────────────────────────────────────────


_CSS_PLACEHOLDER = """\
/* Streamlit exposes theme values as CSS variables.
   Use var(--st-*) to stay in sync with the active theme. */

.stApp {
    /* Core colors */
    /* var(--st-primary-color)                */
    /* var(--st-background-color)             */
    /* var(--st-secondary-background-color)   */
    /* var(--st-text-color)                   */
    /* var(--st-border-color)                 */
    /* var(--st-link-color)                   */

    /* Semantic colors (red/orange/yellow/green/blue/violet/gray) */
    /* var(--st-green-color)                  */
    /* var(--st-green-background-color)       */
    /* var(--st-green-text-color)             */

    /* Typography */
    /* var(--st-font)                         */
    /* var(--st-heading-font)                 */
    /* var(--st-code-font)                    */
    /* var(--st-base-font-size)               */

    /* Shape */
    /* var(--st-base-radius)                  */
    /* var(--st-button-radius)                */
}
"""


class CSSEditor(Component):
    """Inline CSS editor that reads/writes the app's CSS source."""

    class CSSEditorProps(Props):
        height: int = 300

    class CSSEditorState(State):
        text: str = ""
        initialized: bool = False
        apply_requested: bool = False
        save_requested: bool = False
        ref: Ref = modict.factory(Ref)

    def _css_text(self):
        css = get_app().css
        if css is None:
            return ""
        if isinstance(css, Path):
            return css.read_text(encoding="utf-8")
        if isinstance(css, str):
            return css
        return "\n\n".join(
            item.read_text(encoding="utf-8") if isinstance(item, Path) else str(item)
            for item in css
        )

    def _on_change(self, value):
        self.state.text = value

    def _apply(self):
        self.state.apply_requested = True

    def _save(self):
        self.state.save_requested = True

    def render(self):
        if not self.state.initialized:
            self.state.text = self._css_text()
            self.state.initialized = True

        # Handle deferred actions outside callbacks to avoid
        # fragment rerun warnings from st.dialog.
        if self.state.apply_requested or self.state.save_requested:
            if self.state.save_requested:
                css = get_app().css
                if isinstance(css, Path):
                    css.write_text(self.state.text, encoding="utf-8")
                elif isinstance(css, str):
                    candidate = Path(css)
                    if candidate.suffix == ".css" and candidate.parent.exists():
                        candidate.write_text(self.state.text, encoding="utf-8")
            get_app().set_css(self.state.text)
            self.state.apply_requested = False
            self.state.save_requested = False
            get_app().rerun(wait=False)

        current_css = self._css_text()
        changed = self.state.text != current_css

        _DOCS_URL = "https://docs.streamlit.io/develop/concepts/custom-components/components-v2/theming"
        return container(key="css_editor_layout", gap="small")(
            markdown(key="docs_link")(
                f"Use `var(--st-*)` CSS variables to match the active theme. "
                f"[See Streamlit theming docs]({_DOCS_URL})."
            ),
            text_area(
                key="css",
                ref=self.state.ref,
                value=self.state.text,
                height=self.props.height,
                placeholder=_CSS_PLACEHOLDER,
                on_change=self._on_change,
            )("CSS"),
            container(
                key="actions",
                horizontal=True,
                gap="small",
            )(
                button(key="apply", on_click=self._apply, type="primary", disabled=not changed)("Apply"),
                button(key="save", on_click=self._save, type="secondary", disabled=not changed)("Save to file"),
            ),
        )


class CSSEditorDialog(Component):

    class CSSEditorDialogProps(Props):
        open: bool = False
        title: str = "CSS editor"
        width: str = "large"
        height: int = 300

    def render(self):
        if not self.props.open:
            return None
        return dialog(key="dialog", title=self.props.title, width=self.props.width)(
            CSSEditor(key="editor", height=self.props.height)
        )


class CSSEditorButton(Component):

    class CSSEditorButtonProps(Props):
        label: str = "Edit CSS"
        title: str = "CSS editor"
        width: str = "large"
        height: int = 300
        type: str = "secondary"
        help: str | None = None
        icon: str | None = None
        use_container_width: bool | None = None
        disabled: bool = False

    class CSSEditorButtonState(State):
        open: bool = False

    def _open(self):
        self.state.open = True

    def _close(self):
        self.state.open = False
        on_dismiss = self.props.get("on_dismiss")
        if callable(on_dismiss):
            on_dismiss()

    def render(self):
        label = self.children[0] if self.children else self.props.label
        trigger = button(
            key="trigger",
            on_click=self._open,
            type=self.props.type,
            help=self.props.help,
            icon=self.props.icon,
            use_container_width=self.props.use_container_width,
            disabled=self.props.disabled,
        )(label)
        if not self.state.open:
            return trigger
        return (
            trigger,
            CSSEditorDialog(
                key="dialog",
                open=True,
                title=self.props.title,
                width=self.props.width,
                height=self.props.height,
                on_dismiss=self._close,
            ),
        )
