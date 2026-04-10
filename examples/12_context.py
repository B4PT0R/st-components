"""
08 - Context

Shows how to thread ambient values through the tree without prop-drilling.
Introduces: ContextData, create_context, Provider, use_context.
"""
import st_components as stc
from st_components.elements import (
    button, columns, container, divider, markdown, metric, selectbox,
)

from examples._source import source_view


# ---------------------------------------------------------------------------
# 1. Define a context
# ---------------------------------------------------------------------------

class ThemeData(stc.ContextData):
    mode: str = "light"
    accent: str = "blue"


ThemeContext = stc.create_context(ThemeData(), name="theme")


# ---------------------------------------------------------------------------
# 2. Components that consume the context — no prop-drilling needed
# ---------------------------------------------------------------------------

@stc.component
def ThemeBadge(props):
    """Reads the nearest ThemeContext value."""
    theme = stc.use_context(ThemeContext)
    return container(key="badge", border=True)(
        metric(key="mode", label="Mode", value=theme.mode),
        metric(key="accent", label="Accent", value=theme.accent),
    )


@stc.component
def DeepChild(props):
    """Several levels deep — still reads context without receiving it as a prop."""
    theme = stc.use_context(ThemeContext)
    return markdown(key="msg")(
        f"I'm deeply nested and I see **mode={theme.mode}**, **accent={theme.accent}** "
        f"— without any prop drilling."
    )


@stc.component
def MiddleLayer(props):
    """This component knows nothing about theming — it just renders its child."""
    return container(key="box", border=True)(
        markdown(key="h")("### Middle layer (no theme props)"),
        markdown(key="desc")("This component passes nothing to its child. Context goes around it."),
        DeepChild(key="deep"),
    )


# ---------------------------------------------------------------------------
# 3. Page with controls
# ---------------------------------------------------------------------------

class ContextDemo(stc.Component):
    class ContextDemoState(stc.State):
        mode: str = "light"
        accent: str = "blue"

    def render(self):
        mode_options = ["light", "dark", "high-contrast"]
        accent_options = ["blue", "green", "orange", "violet"]

        return container(key="page")(
            markdown(key="intro")(
                "## Context\n\n"
                "Context lets you pass values **through the tree** without threading them "
                "as props at every level. Any descendant can read the nearest provider's value.\n\n"
                "**What to try:** change the mode or accent below — every consumer updates, "
                "even the deeply nested one that never received these values as props."
            ),
            divider(key="d1"),
            markdown(key="h1")("### Provider controls"),
            columns(key="controls")(
                selectbox(key="mode", options=mode_options,
                          index=mode_options.index(self.state.mode),
                          on_change=self.sync_state("mode"))("Mode"),
                selectbox(key="accent", options=accent_options,
                          index=accent_options.index(self.state.accent),
                          on_change=self.sync_state("accent"))("Accent"),
            ),
            # The Provider wraps the subtree — all descendants see the new values
            ThemeContext.Provider(
                key="theme_provider",
                data=ThemeData(mode=self.state.mode, accent=self.state.accent),
            )(
                container(key="consumers")(
                    markdown(key="h2")("### Consumers"),
                    columns(key="badges")(
                        ThemeBadge(key="badge_1"),
                        ThemeBadge(key="badge_2"),
                    ),
                    MiddleLayer(key="middle"),
                ),
            ),
            source_view(__file__),
        )


stc.App(page_title="08 - Context")(ContextDemo()).render()
