from pathlib import Path

import streamlit as st
from modict import modict

from ..core import Component, Props, Ref, State, Theme, get_app
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


_BASE_OPTIONS = ["light", "dark"]
_FONT_OPTIONS = ["sans-serif", "serif", "monospace"]
_RADIUS_OPTIONS = ["none", "small", "medium", "large", "full"]
_PALETTE_FIELDS = (
    "primaryColor",
    "backgroundColor",
    "secondaryBackgroundColor",
    "textColor",
    "borderColor",
    "sidebarBackgroundColor",
)


class ThemeEditorRefs(modict):
    base: Ref = modict.factory(Ref)
    font: Ref = modict.factory(Ref)
    baseFontSize: Ref = modict.factory(Ref)
    primaryColor: Ref = modict.factory(Ref)
    backgroundColor: Ref = modict.factory(Ref)
    secondaryBackgroundColor: Ref = modict.factory(Ref)
    textColor: Ref = modict.factory(Ref)
    borderColor: Ref = modict.factory(Ref)
    baseRadius: Ref = modict.factory(Ref)
    buttonRadius: Ref = modict.factory(Ref)
    showWidgetBorder: Ref = modict.factory(Ref)
    sidebarBackgroundColor: Ref = modict.factory(Ref)
    css: Ref = modict.factory(Ref)


class ThemePalette(modict):
    primaryColor: str
    backgroundColor: str
    secondaryBackgroundColor: str
    textColor: str
    borderColor: str
    sidebarBackgroundColor: str


_PALETTES = {
    "light": ThemePalette(
        primaryColor="#0f766e",
        backgroundColor="#f8fafc",
        secondaryBackgroundColor="#e2e8f0",
        textColor="#0f172a",
        borderColor="#cbd5e1",
        sidebarBackgroundColor="#e2e8f0",
    ),
    "dark": ThemePalette(
        primaryColor="#2dd4bf",
        backgroundColor="#0f172a",
        secondaryBackgroundColor="#1e293b",
        textColor="#e2e8f0",
        borderColor="#334155",
        sidebarBackgroundColor="#111827",
    ),
}


def _palette(base):
    return _PALETTES[base if base in _PALETTES else "light"]


def _default_theme(base="light"):
    colors = _palette(base)
    values = colors.exclude("sidebarBackgroundColor")
    return Theme(
        base=base,
        font="sans-serif",
        **values,
        baseFontSize=16,
        baseRadius="medium",
        buttonRadius="medium",
        showWidgetBorder=True,
        sidebar={"backgroundColor": colors.sidebarBackgroundColor},
    )


class ThemeEditorValues(modict):
    base: str = "light"
    font: str = "sans-serif"
    baseFontSize: int = 16
    primaryColor: str = "#0f766e"
    backgroundColor: str = "#f8fafc"
    secondaryBackgroundColor: str = "#e2e8f0"
    textColor: str = "#0f172a"
    borderColor: str = "#cbd5e1"
    baseRadius: str = "medium"
    buttonRadius: str = "medium"
    sidebarBackgroundColor: str = "#e2e8f0"
    showWidgetBorder: bool = True
    css: str = ""


class ThemeEditorFlags(modict):
    initialized: bool = False
    show_css: bool = False
    save_requested: bool = False


def _option_index(options, value):
    values = list(options)
    return values.index(value)


def _theme_option(key):
    value = st.get_option(key)
    if type(value).__module__.startswith("unittest.mock"):
        return None
    return value


def _runtime_theme():
    base = _theme_option("theme.base")
    if base not in _BASE_OPTIONS:
        base = "light"
    theme = Theme(base=base)

    for field in ThemeEditorValues().exclude("css").keys():
        if field == "sidebarBackgroundColor":
            continue
        value = _theme_option(f"theme.{field}")
        if value is None:
            continue
        try:
            theme[field] = value
        except TypeError:
            continue

    sidebar_background = _theme_option("theme.sidebar.backgroundColor")
    if isinstance(sidebar_background, str):
        theme.sidebar = {"backgroundColor": sidebar_background}

    return theme


def _active_theme(theme=None):
    effective = _runtime_theme()
    if theme:
        effective.update(theme.exclude("sidebar"))
        if theme.get("sidebar", {}).get("backgroundColor") is not None:
            effective.sidebar = {"backgroundColor": theme.sidebar.backgroundColor}
    return effective


def _editor_values(theme, css_text=""):
    theme = _active_theme(theme)
    base = theme.get("base", "light")
    defaults = _default_theme(base)
    values = ThemeEditorValues(defaults.exclude("sidebar"))
    values.update(theme.exclude("sidebar"))
    values.update(
        sidebarBackgroundColor=theme.get("sidebar", defaults.get("sidebar", {})).get("backgroundColor"),
        css=css_text,
    )
    return values


def _editor_to_theme(values):
    values = dict(values.exclude("css"))
    sidebar_background = values.pop("sidebarBackgroundColor")
    return Theme(**values, sidebar={"backgroundColor": sidebar_background})


def _apply_editor_palette(values):
    colors = _palette(values.base)
    values.update(colors)


class ThemeEditor(Component):
    class ThemeEditorProps(Props):
        show_css: bool = False

    class ThemeEditorState(State):
        editor: ThemeEditorValues = modict.factory(ThemeEditorValues)
        flags: ThemeEditorFlags = modict.factory(ThemeEditorFlags)
        refs: ThemeEditorRefs = modict.factory(ThemeEditorRefs)

    def __init__(self, **props):
        super().__init__(**props)
        self._refs = self.state.refs

    def _theme(self):
        return _active_theme(get_app().theme)

    def _css_text(self):
        css = get_app().css
        if css is None:
            return ""
        if isinstance(css, Path):
            return css.read_text()
        if isinstance(css, str):
            return css
        blocks = []
        for item in css:
            if isinstance(item, Path):
                blocks.append(item.read_text())
            else:
                blocks.append(str(item))
        return "\n\n".join(blocks)

    def _load_state(self, theme, css_text):
        self.state.update(editor=_editor_values(theme, css_text))
        self.state.flags.update(
            initialized=True,
            show_css=self.props.show_css,
        )
        return self.state

    def _current_values(self):
        return self.state.editor

    def _theme_from_values(self, values=None):
        return _editor_to_theme(values or self._current_values())

    def _refresh_refs(self, *fields):
        for field in fields:
            self._refs[field].refresh()

    def _sync_palette(self, base):
        self.state.editor.update(base=base)
        _apply_editor_palette(self.state.editor)
        self._refresh_refs(*_PALETTE_FIELDS)

    def _bind_editor(self, field, after=None):
        def sync(value):
            self.state.editor.update(**{field: value})
            if after is not None:
                after(value)

        return sync

    def _bind_flag(self, field):
        def sync(value):
            self.state.flags.update(**{field: value})

        return sync

    def _save(self):
        self.state.flags.update(save_requested=True)

    def _reset(self):
        theme = _default_theme()
        css_text = ""
        self._load_state(theme, css_text)
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
            markdown(key="body")("Base theme, font family and root text size."),
            selectbox(
                key="base",
                ref=self._refs["base"],
                options=_BASE_OPTIONS,
                index=_option_index(_BASE_OPTIONS, values["base"]),
                on_change=self._bind_editor("base", after=self._sync_palette),
            )("Base"),
            selectbox(
                key="font",
                ref=self._refs["font"],
                options=_FONT_OPTIONS,
                index=_option_index(_FONT_OPTIONS, values["font"]),
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
            markdown(key="body")("Primary, surfaces, text, borders and sidebar background."),
            container(
                key="palette",
                horizontal=True,
                horizontal_alignment="distribute",
                gap="small",
                width="stretch",
            )(
                self._palette_picker(ui_key="primary", field="primaryColor", label="Primary color", values=values),
                self._palette_picker(ui_key="background", field="backgroundColor", label="Background color", values=values),
                self._palette_picker(ui_key="surface", field="secondaryBackgroundColor", label="Surface color", values=values),
                self._palette_picker(ui_key="text", field="textColor", label="Text color", values=values),
                self._palette_picker(ui_key="border", field="borderColor", label="Border color", values=values),
                self._palette_picker(ui_key="sidebar_bg", field="sidebarBackgroundColor", label="Sidebar background", values=values),
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

    def _css_panel(self, values):
        if not self.state.flags.show_css:
            return None
        return container(key="css_panel", border=True, height="stretch")(
            subheader(key="title")("CSS"),
            markdown(key="body")("Optional overrides applied after the Streamlit theme."),
            text_area(key="css", ref=self._refs["css"], value=values["css"], height=160, on_change=self._bind_editor("css"))("CSS"),
        )

    def _actions_bar(self):
        return container(
            key="actions",
            horizontal=True,
            horizontal_alignment="distribute",
            gap="small",
            width="stretch",
        )(
            container(
                key="actions_left",
                horizontal=True,
                horizontal_alignment="left",
                gap="small",
            )(
                button(key="save", on_click=self._save, type="primary")("Save"),
                button(key="reset", on_click=self._reset, type="secondary")("Reset"),
            ),
            container(
                key="actions_right",
                horizontal_alignment="right",
                vertical_alignment="center",
                height="stretch",
                gap="small",
            )(
                toggle(key="show_css", value=self.state.flags.show_css, on_change=self._bind_flag("show_css"))("Show CSS"),
            )
        )

    def _layout(self, values):
        return container(
            key="editor_layout",
            gap="small",
        )(
            columns(key="top_grid", gap="small")(
                *[self._foundation_panel(values),
                self._shape_panel(values),
                self._css_panel(values)]
            ),
            self._colors_panel(values),
            self._actions_bar(),
        )

    def render(self):
        theme = self._theme()
        current_css = self._css_text()
        if not self.state.flags.initialized:
            self._load_state(theme, current_css)

        next_theme = self._theme_from_values()
        next_css = self.state.editor.css if self.state.flags.show_css else ""
        theme_changed = next_theme != theme
        css_changed = next_css != current_css

        if theme_changed or css_changed or self.state.flags.save_requested:
            if theme_changed:
                get_app().set_theme(next_theme)
            if css_changed:
                get_app().set_css(next_css)
            if self.state.flags.save_requested:
                get_app().save_theme()
                self.state.flags.update(save_requested=False)
            st.rerun(scope="app")

        return self._layout(self._current_values())


class ThemeEditorDialog(Component):

    class ThemeEditorDialogProps(Props):
        open: bool = False
        title: str = "Theme editor"
        show_css: bool = False
        width: str = "large"

    def render(self):
        if not self.props.open:
            return None

        dialog_props = self.props.exclude("key", "children", "open", "show_css")
        return dialog(key="dialog", **dialog_props)(
            ThemeEditor(key="editor", show_css=self.props.show_css)
        )


class ThemeEditorButton(Component):

    class ThemeEditorButtonProps(Props):
        label: str = "Edit theme"
        title: str = "Theme editor"
        show_css: bool = False
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
        return (
            button(
                key="trigger",
                on_click=self._open,
                type=self.props.type,
                help=self.props.help,
                icon=self.props.icon,
                use_container_width=self.props.use_container_width,
                disabled=self.props.disabled,
                shortcut=self.props.shortcut,
            )(label),
            ThemeEditorDialog(
                key="dialog",
                open=self.state.open,
                title=self.props.title,
                show_css=self.props.show_css,
                width=self.props.width,
                on_dismiss=self._close,
            ),
        )
