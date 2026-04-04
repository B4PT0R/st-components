from st_components import App, Component, Page, Router, get_element_value, get_shared_state
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

from multipage_shared import WorkspaceSidebar, WorkspaceState


class OverviewPage(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(note="Inline pages can live next to the entrypoint.")

    def sync_note(self):
        self.state.note = get_element_value()

    def render(self):
        workspace = get_shared_state("workspace")
        snapshot = {
            "page_type": "inline component page",
            "note": self.state.note,
            "shared_state": dict(workspace),
        }

        return container(key="page")(
            WorkspaceSidebar(key="workspace_sidebar"),
            title(key="title")("st-components multipage example"),
            caption(key="caption")(
                "This page is declared inline in the entrypoint with Page(...)(OverviewPage(key=\"root\"))."
            ),
            info(key="info")(
                "Use the top navigation to switch between this inline page and the file-backed report page. "
                "Both pages instantiate the same sidebar component and keep it synchronized through shared state."
            ),
            columns(key="metrics")(
                metric(key="team", label="Shared team", value=workspace.team),
                metric(key="focus", label="Shared focus", value=workspace.focus),
                metric(key="visits", label="Shared visits", value=workspace.visits),
                metric(key="mode", label="Page source", value="inline"),
            ),
            text_input(
                key="note",
                value=self.state.note,
                on_change=self.sync_note,
            )("Inline page note"),
            markdown(key="body")(
                "The sidebar is declared as a reusable component and instantiated by each page. "
                "Its inputs read and write `get_shared_state(\"workspace\")`, so the visible controls stay aligned across navigation."
            ),
            page_link(
                key="report_link",
                page="multipage_pages/report_page.py",
                label="Open the file-backed report page",
                icon=":material/open_in_new:",
            ),
            json(key="snapshot")(snapshot),
            code(key="code", language="python")(
                "app = App(\n"
                "    page_title=\"st-components multipage example\",\n"
                "    page_icon=\":material/dashboard:\",\n"
                "    layout=\"wide\",\n"
                ")(\n"
                "    Router(\n"
                "        position=\"top\",\n"
                "    )(\n"
                "        Page(key=\"overview\", nav_title=\"Overview\", nav_icon=\":material/home:\", default=True)(\n"
                "            OverviewPage(key=\"root\")\n"
                "        ),\n"
                "        Page(key=\"report\", nav_title=\"Report\", nav_icon=\":material/description:\")(\n"
                "            \"multipage_pages/report_page.py\"\n"
                "        ),\n"
                "    )\n"
                ")\n"
                "app.shared_state(\"workspace\", WorkspaceState())\n"
                "app.render()"
            ),
        )

app = App(
    page_title="st-components multipage example",
    page_icon=":material/dashboard:",
    layout="wide",
)(
    Router(position="top")(
        Page(key="overview", nav_title="Overview", nav_icon=":material/home:", default=True)(
            OverviewPage(key="root")
        ),
        Page(key="report", nav_title="Report", nav_icon=":material/description:")(
            "multipage_pages/report_page.py"
        ),
    )
)
app.shared_state("workspace", WorkspaceState())
app.render()
