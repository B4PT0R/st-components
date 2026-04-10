"""
10 - Theming

Shows how to use the built-in ThemeEditorButton to customize the app's
look and feel at runtime: colors, typography, radii, CSS overrides.
Introduces: ThemeEditorButton, App(theme=..., css=..., config=...).
"""
import st_components as stc
from st_components.builtins import CSSEditorButton, ThemeEditorButton
from st_components.elements import (
    audio_input, button, caption, checkbox, color_picker, columns, container,
    date_input, divider, file_uploader, header, markdown, metric, multiselect,
    number_input, selectbox, sidebar, slider, text_area, text_input, toggle,
)

from examples._source import source_view


class DummySidebar(stc.Component):
    """Dummy sidebar — just enough widgets to preview sidebar colors live."""

    class S(stc.State):
        value: int = 50

    def render(self):
        return sidebar(key="sidebar")(
            header(key="h")("Sidebar"),
            caption(key="sub")("Preview sidebar background, text, and widget colors."),
            divider(key="d"),
            text_input(key="sample", value="Sample text")("Text input"),
            slider(key="slider", min_value=0, max_value=100,
                   value=self.state.value,
                   on_change=self.sync_state("value"))("Slider"),
            toggle(key="toggle", value=True)("Toggle"),
            metric(key="metric", label="Value", value=self.state.value),
        )


class DummyCard(stc.Component):
    """Dummy card — enough surface to judge colors, typography, borders, spacing."""

    def render(self):
        return container(key="card", border=True)(
            markdown(key="h")("### Sample widgets"),
            caption(key="desc")(
                "Dummy content — just enough variety to preview every aspect of the theme."
            ),
            columns(key="buttons")(
                button(key="primary", type="primary")("Primary"),
                button(key="secondary", type="secondary")("Secondary"),
                button(key="tertiary", type="tertiary")("Tertiary"),
            ),
            columns(key="row1")(
                text_input(key="text", value="Hello")("Text input"),
                number_input(key="number", value=42)("Number"),
                date_input(key="date")("Date"),
            ),
            columns(key="row2")(
                selectbox(key="select", options=["Alpha", "Beta", "Gamma"])("Selectbox"),
                multiselect(key="multi", options=["Red", "Green", "Blue"], default=["Red"])("Multiselect"),
                color_picker(key="color", value="#0f766e")("Color"),
            ),
            columns(key="row3")(
                slider(key="slider", min_value=0, max_value=100, value=50)("Slider"),
                toggle(key="toggle", value=True)("Toggle"),
                checkbox(key="check", value=True)("Checkbox"),
            ),
            text_area(key="area", value="Some longer text…", height=80)("Text area"),
            file_uploader(key="file")("File uploader"),
            audio_input(key="audio")("Audio input"),
            metric(key="metric", label="Sample metric", value=99, delta=7),
        )


class ThemingDemo(stc.Component):
    def render(self):
        return container(key="page")(
            DummySidebar(key="side"),
            markdown(key="intro")(
                "## Theming\n\n"
                "Open the **Theme editor** to customize colors, typography, and shape. "
                "Open the **CSS editor** to add custom overrides using Streamlit's "
                "`var(--st-*)` CSS variables.\n\n"
                "**Try this:** open the CSS editor and paste:\n"
                "```css\n"
                ".stApp {\n"
                "    --st-base-radius: 0px;\n"
                "    letter-spacing: 0.02em;\n"
                "}\n"
                ".stVerticalBlock { gap: 0.5rem !important; }\n"
                "```\n"
                "Click **Apply** — notice the tighter spacing and sharp corners.\n\n"
                "> Click **Save** to persist theme to `stc-config.toml` or CSS to "
                "`.streamlit/styles.css`."
            ),
            columns(key="editor_buttons", gap="small")(
                ThemeEditorButton(key="theme_btn", type="primary", title="Theme Editor")(
                    "Open theme editor"
                ),
                CSSEditorButton(key="css_btn", icon=":material/code:")(
                    "Open CSS editor"
                ),
            ),
            divider(key="d"),
            DummyCard(key="card"),
            source_view(__file__),
        )


stc.App(
    page_title="10 - Theming",
    layout="wide",
)(ThemingDemo()).render()
