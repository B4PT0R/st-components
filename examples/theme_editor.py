from st_components import App, Component, State
from st_components.builtins import ThemeEditorButton
from st_components.elements import (
    caption,
    columns,
    container,
    markdown,
    metric,
    number_input,
    text_area,
    text_input,
    title,
    toggle,
)


class SettingsCard(Component):

    class SettingsCardState(State):
        project: str = "Atlas redesign"
        owner: str = "Baptiste"
        focus: int = 72
        notes: str = "Use the theme editor to tune colors, typography, spacing and radii."
        alerts: bool = True

    def render(self):
        return container(key="card", border=True)(
            markdown(key="title")("### Settings"),
            text_input(key="project", value=self.state.project, on_change=self.sync_state("project"))("Project"),
            text_input(key="owner", value=self.state.owner, on_change=self.sync_state("owner"))("Owner"),
            number_input(key="focus", min_value=0, max_value=100, step=1, value=self.state.focus, on_change=self.sync_state("focus"))("Focus"),
            toggle(key="alerts", value=self.state.alerts, on_change=self.sync_state("alerts"))("Alerts"),
            text_area(key="notes", value=self.state.notes, height=140, on_change=self.sync_state("notes"))("Notes"),
        )


class PreviewCard(Component):

    def render(self):
        return container(key="card", border=True)(
            markdown(key="title")("### Preview"),
            markdown(key="body")(
                "This page intentionally stays small. It gives enough surface to judge "
                "**colors**, **typography**, **widget borders**, **button radius** and "
                "**general spacing** without burying the example in layout code."
            ),
            columns(key="metrics")(
                metric(key="status", label="Status", value="Live"),
                metric(key="surface", label="Surface", value="Card"),
                metric(key="mode", label="Theme", value="Editable"),
            ),
        )


class ThemeEditorDemo(Component):

    def render(self):
        return container(key="page")(
            title(key="title")("Theme editor builtin"),
            caption(key="caption")(
                "Use the prewired button below to edit the current app theme live."
            ),
            ThemeEditorButton(key="open", type="primary", title="Theme editor")("Open theme editor"),
            columns(key="content")(
                SettingsCard(key="settings"),
                PreviewCard(key="preview"),
            ),
        )


App(
    page_title="Theme editor",
    layout="wide",
)(ThemeEditorDemo(key="app")).render()
