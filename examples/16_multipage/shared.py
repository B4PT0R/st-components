from st_components import Component, ContextData, State, create_context, get_shared_state, use_context
from st_components.elements import button, caption, columns, container, divider, markdown, sidebar, text_input


class WorkspaceState(State):
    visits: int = 0
    current_message: str = "Hello from shared state"
    team: str = "Core"
    focus: int = 7


class AppModeData(ContextData):
    mode: str = "unset"


AppModeContext = create_context(AppModeData(mode="unset"), name="app_mode")


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
        app_mode = use_context(AppModeContext)
        return sidebar(key="sidebar")(
            container(key="workspace")(
                markdown(key="title")("### Workspace sidebar"),
                caption(key="caption")(
                    "This sidebar lives in the Router's chrome wrapper — it renders once around every page."
                ),
                caption(key="mode")(
                    f"Ambient context mode: `{app_mode.mode}`"
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


class AppFooter(Component):
    """Site-wide footer — the same kind of footer you'd find on most websites:
    a divider, a few columns of links/info, and a copyright line at the bottom.

    Kept as its own component so the chrome stays small and the footer can be
    edited (or reused elsewhere) without touching the layout code.
    """

    def render(self):
        return container(key="footer")(
            divider(key="rule"),
            columns(key="cols")(
                container(key="about")(
                    markdown(key="title")("**st-components**"),
                    caption(key="tagline")(
                        "React-style stateful components for Streamlit."
                    ),
                    caption(key="version")("v0.4.1 · MIT License"),
                ),
                container(key="product")(
                    markdown(key="title")("**Product**"),
                    markdown(key="docs")(
                        "[Documentation](https://github.com/B4PT0R/st-components#readme)"
                    ),
                    markdown(key="api")(
                        "[API reference](https://github.com/B4PT0R/st-components/blob/main/API_REFERENCE.md)"
                    ),
                    markdown(key="examples")(
                        "[Examples](https://github.com/B4PT0R/st-components/tree/main/examples)"
                    ),
                ),
                container(key="community")(
                    markdown(key="title")("**Community**"),
                    markdown(key="github")(
                        "[GitHub](https://github.com/B4PT0R/st-components)"
                    ),
                    markdown(key="issues")(
                        "[Report an issue](https://github.com/B4PT0R/st-components/issues)"
                    ),
                    markdown(key="streamlit")(
                        "[Streamlit](https://streamlit.io)"
                    ),
                ),
                container(key="legal")(
                    markdown(key="title")("**Legal**"),
                    caption(key="license")("Released under the MIT License."),
                    caption(key="trademark")(
                        "Streamlit® is a registered trademark of Snowflake Inc."
                    ),
                ),
            ),
            divider(key="bottom_rule"),
            caption(key="copyright")(
                "© 2026 st-components · rendered once by `AppChrome`, shown around every page."
            ),
        )


class AppChrome(Component):
    """Per-page chrome — the Router instantiates this around every page source.

    The active page renders inside *self.children. Anything declared here
    (sidebar, footer, …) shows up around every page without each page having
    to re-declare it.
    """

    def render(self):
        return container(key="layout")(
            WorkspaceSidebar(key="sidebar"),
            container(key="main")(*self.children),
            AppFooter(key="footer"),
        )
