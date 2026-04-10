"""
Regression Playground page.

Demonstrates:
- use_memo with all inputs as deps
- set_state for batch reset
"""
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parents[1]
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import st_components as stc
from st_components.elements import (
    button, columns, container, divider, line_chart, markdown, slider,
)
from examples._source import source_view
from shared import AppSidebar, DisplayContext
from components import Section, StatsRow


def _compute_regression(true_slope, noise, seed, n_samples):
    """Pure computation — no side effects."""
    rng = np.random.default_rng(seed=seed)
    x = np.linspace(-3, 3, n_samples)
    y_clean = true_slope * x + 0.5
    y_noisy = y_clean + rng.normal(0, max(noise, 0.01), n_samples)

    coeffs = np.polyfit(x, y_noisy, deg=1)
    slope, intercept = float(coeffs[0]), float(coeffs[1])
    y_fit = slope * x + intercept

    ss_res = np.sum((y_noisy - y_fit) ** 2)
    ss_tot = np.sum((y_noisy - np.mean(y_noisy)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return {
        "fitted_slope": round(slope, 3),
        "fitted_intercept": round(intercept, 3),
        "r2": round(float(r2), 4),
        "y_noisy": y_noisy.tolist(),
        "y_fit": y_fit.tolist(),
    }


class RegressionPlayground(stc.Component):
    class RegrState(stc.State):
        true_slope: float = 1.5
        noise: float = 0.5

    def reset(self):
        self.set_state(true_slope=1.5, noise=0.5)

    def render(self):
        settings = stc.get_shared_state("settings")
        display = stc.use_context(DisplayContext)

        computed = stc.use_memo(
            lambda: _compute_regression(
                self.state.true_slope, self.state.noise,
                settings.seed, settings.n_samples,
            ),
            deps=[self.state.true_slope, self.state.noise,
                  settings.seed, settings.n_samples],
        )

        slope_error = round(abs(computed["fitted_slope"] - self.state.true_slope), 3)

        return container(key="page")(
            AppSidebar(key="sidebar"),
            Section(key="header", title="Regression Playground",
                    description="Set the true slope and noise — or change seed/samples in the sidebar."),
            columns(key="controls")(
                slider(key="slope", min_value=-4.0, max_value=4.0, step=0.25,
                       value=self.state.true_slope,
                       on_change=self.sync_state("true_slope"))("True slope"),
                slider(key="noise", min_value=0.0, max_value=3.0, step=0.1,
                       value=self.state.noise,
                       on_change=self.sync_state("noise"))("Noise (σ)"),
            ),
            StatsRow(key="stats", stats=[
                {"label": "True slope", "value": self.state.true_slope},
                {"label": "Fitted slope", "value": computed["fitted_slope"]},
                {"label": "Slope error", "value": slope_error},
                {"label": "R²", "value": computed["r2"]},
                {"label": "Samples", "value": settings.n_samples},
            ]) if display.show_stats else None,
            line_chart(key="chart", data={
                "observed": computed["y_noisy"],
                "fit": computed["y_fit"],
            }, height=display.chart_height),
            button(key="reset", on_click=self.reset)("Reset to defaults"),
            source_view(__file__),
        )


stc.get_app().render_page(RegressionPlayground(key="root"))
