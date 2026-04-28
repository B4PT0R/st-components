"""
Shared state, context, and reusable components for the data app.

Demonstrates:
- Typed shared state (cross-page persistence)
- Context (ambient config without prop-drilling)
- Reusable sidebar component
"""
import st_components as stc
from st_components.elements import (
    caption, columns, container, divider, markdown, metric, sidebar, slider, toggle,
)


# ── Shared state (persists across pages) ─────────────────────────────────────

class AppSettings(stc.State):
    """Global settings shared by all pages via App.create_shared_state()."""
    seed: int = 42
    n_samples: int = 500
    dark_mode: bool = False
    wide_layout: bool = True


# ── Context (ambient config) ─────────────────────────────────────────────────

class DisplayConfig(stc.ContextData):
    """Display preferences threaded through the tree without prop-drilling."""
    show_stats: bool = True
    chart_height: int = 300


DisplayContext = stc.create_context(DisplayConfig(), name="display")


# ── Reusable sidebar ─────────────────────────────────────────────────────────


class AppSidebar(stc.Component):
    """Sidebar with shared controls — same instance on every page."""

    def on_dark_mode(self, value):
        settings = stc.get_shared_state("settings")
        settings.dark_mode = value
        stc.get_app().set_params(color_mode="dark" if value else "light")

    def on_wide_layout(self, value):
        settings = stc.get_shared_state("settings")
        settings.wide_layout = value
        stc.get_app().set_params(layout="wide" if value else "centered")

    def render(self):
        settings = stc.get_shared_state("settings")
        return sidebar(key="sidebar")(
            markdown(key="title")("### Data Explorer"),
            caption(key="sub")("st-components full app demo"),
            divider(key="d1"),
            markdown(key="h_data")("**Data settings**"),
            slider(key="seed", min_value=0, max_value=100, value=settings.seed,
                   on_change=lambda v: settings.update(seed=v))("Random seed"),
            slider(key="n_samples", min_value=50, max_value=2000, step=50,
                   value=settings.n_samples,
                   on_change=lambda v: settings.update(n_samples=int(v)))("Sample size"),
            divider(key="d2"),
            markdown(key="h_display")("**Display**"),
            toggle(key="dark", value=settings.dark_mode,
                   on_change=self.on_dark_mode)("Dark mode"),
            toggle(key="wide", value=settings.wide_layout,
                   on_change=self.on_wide_layout)("Wide layout"),
            divider(key="d3"),
            container(key="info", border=True)(
                metric(key="m_seed", label="Seed", value=settings.seed),
                metric(key="m_n", label="Samples", value=settings.n_samples),
            ),
        )


# ── Page chrome (sidebar + main + footer wrapped around every page) ─────────

class AppFooter(stc.Component):
    """Footer rendered around every page via AppChrome."""

    def render(self):
        return container(key="footer")(
            divider(key="rule"),
            columns(key="cols")(
                container(key="brand")(
                    markdown(key="title")("**Data Explorer**"),
                    caption(key="tagline")(
                        "st-components full data-app demo."
                    ),
                ),
                container(key="resources")(
                    markdown(key="title")("**Resources**"),
                    markdown(key="docs")(
                        "[Documentation](https://github.com/B4PT0R/st-components#readme)"
                    ),
                    markdown(key="examples")(
                        "[All examples](https://github.com/B4PT0R/st-components/tree/main/examples)"
                    ),
                ),
                container(key="about")(
                    markdown(key="title")("**About**"),
                    caption(key="data")(
                        "Synthetic data computed in-process via numpy."
                    ),
                    caption(key="license")("Released under the MIT License."),
                ),
            ),
            divider(key="bottom_rule"),
            caption(key="copyright")(
                "© 2026 · footer rendered once by `AppChrome`, shown around every page."
            ),
        )


class AppChrome(stc.Component):
    """Page chrome — Router instantiates this around every page source.

    Lives at fiber path ``app.router.chrome``, page-independent: chrome
    state survives navigation between pages naturally. The active page
    renders inside `*self.children` (path:
    ``app.router.chrome.<page>.<source>``). Sidebar and footer are
    declared here once instead of being repeated by each page.
    """

    def render(self):
        return container(key="layout")(
            AppSidebar(key="sidebar"),
            container(key="main")(*self.children),
            AppFooter(key="footer"),
        )
