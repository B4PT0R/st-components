"""
17 - Full Data App

A realistic multipage data-science app demonstrating best practices:
- Multipage routing (Router / Page)
- Shared state across pages
- Context for ambient config
- Typed Props & State
- Component composition and reuse
- Lifecycle hooks (component_did_mount)
- Functional components with use_memo
- Separation of computation from rendering

Run:
    streamlit run examples/17_full_data_app/app.py
"""
import st_components as stc
from st_components.builtins import Page, Router

from shared import AppChrome, AppSettings, DisplayConfig, DisplayContext

# ── App setup ────────────────────────────────────────────────────────────────

app = stc.App(
    DisplayContext.Provider(key="display", data=DisplayConfig(show_stats=True, chart_height=300))(
        Router(position="top", chrome=AppChrome)(
            Page(key="signal", nav_title="Signal", nav_icon=":material/show_chart:", default=True)(
                "pages/signal_page.py"
            ),
            Page(key="distribution", nav_title="Distribution", nav_icon=":material/bar_chart:")(
                "pages/distribution_page.py"
            ),
            Page(key="regression", nav_title="Regression", nav_icon=":material/trending_up:")(
                "pages/regression_page.py"
            ),
        )
    ),
    page_title="Data Explorer",
    page_icon=":material/analytics:",
    layout="wide",
)
app.create_shared_state("settings", AppSettings())
app.render()
