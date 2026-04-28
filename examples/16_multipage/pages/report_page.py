import sys
from pathlib import Path

from st_components import Component, get_app, get_shared_state, use_context
from st_components.elements import (
    caption,
    code,
    columns,
    container,
    info,
    json,
    markdown,
    metric,
    text_area,
    title,
)
from examples._source import source_view

MULTIPAGE_DIR = Path(__file__).resolve().parents[1]
if str(MULTIPAGE_DIR) not in sys.path:
    sys.path.insert(0, str(MULTIPAGE_DIR))

from shared import AppModeContext


class ReportPage(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(
            notes="This file is executed by Streamlit through st.Page(...).",
        )

    def render(self):
        workspace = get_shared_state("workspace")
        app_mode = use_context(AppModeContext)
        snapshot = {
            "page_type": "file-backed page",
            "notes": self.state.notes,
            "app_mode": dict(app_mode),
            "shared_state": dict(workspace),
        }

        return container(key="page")(
            title(key="title")("Report page"),
            caption(key="caption")(
                "This page lives in examples/16_multipage/pages/report_page.py and ends with get_app().render_page(...)."
            ),
            info(key="info")(
                "This file-backed page renders inside the same `AppChrome` as the overview page — "
                "the Router applies its chrome to file-backed pages too (via `get_app().render_page(...)`)."
            ),
            columns(key="metrics")(
                metric(key="team", label="Shared team", value=workspace.team),
                metric(key="focus", label="Shared focus", value=workspace.focus),
                metric(key="visits", label="Shared visits", value=workspace.visits),
                metric(key="mode", label="Page source", value="file"),
                metric(key="app_mode", label="Context mode", value=app_mode.mode),
            ),
            text_area(
                key="note",
                value=self.state.notes,
                height=140,
                on_change=self.sync_state("notes"),
            )("File page notes"),
            markdown(key="body")(
                "This file is a regular Streamlit page source — but its content still lives "
                "inside the Router's chrome. Path: `app.router.report.chrome.root...`.\n\n"
                "No special router API is needed here: `get_app().render_page(ReportPage(...))` "
                "goes through the same routed-render pipeline as inline pages, so the chrome "
                "(sidebar, layout) wraps this page automatically. Shared state and context "
                "carry over too."
            ),
            json(key="snapshot")(snapshot),
            code(key="code", language="python")(
                "from st_components import Component, get_app\n\n"
                "class ReportPage(Component):\n"
                "    def render(self):\n"
                "        return ...  # no need to declare the sidebar here — chrome handles it\n\n"
                "get_app().render_page(ReportPage(key=\"root\"))"
            ),
            source_view(__file__),
        )


get_app().render_page(ReportPage(key="root"))
