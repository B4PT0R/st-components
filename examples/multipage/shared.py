from st_components import Component, State, get_shared_state
from st_components.elements import button, caption, container, markdown, sidebar, text_input


class WorkspaceState(State):
    visits: int = 0
    current_message: str = "Hello from shared state"
    team: str = "Core"
    focus: int = 7


class WorkspaceSidebar(Component):

    def sync_team(self, value):
        workspace = get_shared_state("workspace")
        workspace.team = value

    def sync_focus(self, value):
        workspace = get_shared_state("workspace")
        try:
            workspace.focus = int(value)
        except (TypeError, ValueError):
            pass

    def sync_message(self, value):
        workspace = get_shared_state("workspace")
        workspace.current_message = value

    def increment_visits(self):
        workspace = get_shared_state("workspace")
        workspace.visits += 1

    def render(self):
        workspace = get_shared_state("workspace")
        return sidebar(key="sidebar")(
            container(key="workspace")(
                markdown(key="title")("### Workspace sidebar"),
                caption(key="caption")(
                    "This sidebar component is instantiated in each page and synchronized through shared state."
                ),
                text_input(
                    key="team",
                    value=workspace.team,
                    on_change=self.sync_team,
                )("Shared team"),
                text_input(
                    key="focus",
                    value=str(workspace.focus),
                    on_change=self.sync_focus,
                )("Shared focus"),
                text_input(
                    key="message",
                    value=workspace.current_message,
                    on_change=self.sync_message,
                )("Shared message"),
                button(key="visits", on_click=self.increment_visits, type="primary")(
                    f"Increment shared visits ({workspace.visits})"
                ),
            )
        )
