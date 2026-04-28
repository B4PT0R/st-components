from st_components import App, Component, get_shared_state, use_context
from st_components.builtins import Page, Router
from st_components.elements import (
    caption,
    code,
    columns,
    container,
    info,
    json,
    markdown,
    metric,
    page_link,
    text_input,
    title,
)

from examples._source import source_view
from shared import AppChrome, AppModeContext, AppModeData, WorkspaceState


class OverviewPage(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(note="Inline pages can live next to the entrypoint.")

    def render(self):
        workspace = get_shared_state("workspace")
        app_mode = use_context(AppModeContext)
        snapshot = {
            "page_type": "inline component page",
            "note": self.state.note,
            "app_mode": dict(app_mode),
            "shared_state": dict(workspace),
        }

        return container(key="page")(
            title(key="title")("st-components multipage example"),
            caption(key="caption")(
                "This page is declared inline in the entrypoint with Page(...)(OverviewPage(key=\"root\"))."
            ),
            info(key="info")(
                "Use the top navigation to switch between this inline page and the file-backed report page. "
                "The sidebar comes from the Router's `chrome=AppChrome` wrapper — declared once, "
                "applied around every page. The pages themselves no longer need to instantiate it."
            ),
            columns(key="metrics")(
                metric(key="team", label="Shared team", value=workspace.team),
                metric(key="focus", label="Shared focus", value=workspace.focus),
                metric(key="visits", label="Shared visits", value=workspace.visits),
                metric(key="mode", label="Page source", value="inline"),
                metric(key="app_mode", label="Context mode", value=app_mode.mode),
            ),
            text_input(
                key="note",
                value=self.state.note,
                on_change=self.sync_state("note"),
            )("Inline page note"),
            markdown(key="body")(
                "The sidebar lives in `AppChrome`, the Router's chrome wrapper. "
                "Chrome's `render()` places the active page via `*self.children` — so each page "
                "is rendered inside the chrome's layout (path: `app.router.chrome.<page>.<source>`).\n\n"
                "Chrome's own fiber lives at `app.router.chrome` — page-independent — so chrome "
                "state would survive navigation naturally. The sidebar still uses "
                "`get_shared_state(\"workspace\")` here because the values are also consumed by "
                "page bodies (cross-cutting state), but a sidebar-only widget could use plain "
                "`self.state` and persist across pages without `shared_state`."
            ),
            page_link(
                key="report_link",
                page="pages/report_page.py",
                label="Open the file-backed report page",
                icon=":material/open_in_new:",
            ),
            json(key="snapshot")(snapshot),
            code(key="code", language="python")(
                "class AppChrome(Component):\n"
                "    def render(self):\n"
                "        return container(key=\"layout\")(\n"
                "            WorkspaceSidebar(key=\"workspace_sidebar\"),\n"
                "            container(key=\"main\")(*self.children),  # ← active page renders here\n"
                "        )\n\n"
                "app = App(\n"
                "    page_title=\"st-components multipage example\",\n"
                "    layout=\"wide\",\n"
                ")(\n"
                "    AppModeContext.Provider(key=\"app_mode_scope\", data=AppModeData(mode=\"multipage-demo\"))(\n"
                "        Router(position=\"top\", chrome=AppChrome)(\n"
                "            Page(key=\"overview\", nav_title=\"Overview\", default=True)(\n"
                "                OverviewPage(key=\"root\")\n"
                "            ),\n"
                "            Page(key=\"report\", nav_title=\"Report\")(\n"
                "                \"pages/report_page.py\"\n"
                "            ),\n"
                "        )\n"
                "    )\n"
                ")\n"
                "app.create_shared_state(\"workspace\", WorkspaceState())\n"
                "app.render()"
            ),
            source_view(__file__),
        )

app = App(
    AppModeContext.Provider(key="app_mode_scope", data=AppModeData(mode="multipage-demo"))(
        Router(position="top", chrome=AppChrome)(
            Page(key="overview", nav_title="Overview", nav_icon=":material/home:", default=True)(
                OverviewPage(key="root")
            ),
            Page(key="report", nav_title="Report", nav_icon=":material/description:")(
                "pages/report_page.py"
            ),
        )
    ),
    page_title="st-components multipage example",
    page_icon=":material/dashboard:",
    layout="wide",
)
app.create_shared_state("workspace", WorkspaceState())
app.render()
