"""
Distribution Analyzer page.

Demonstrates:
- use_memo with shared state deps for reactive computation
- Altair chart integration
"""
import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd

PARENT = Path(__file__).resolve().parents[1]
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import st_components as stc
from st_components.elements import (
    altair_chart, caption, columns, container, divider, markdown, selectbox, slider,
)
from examples._source import source_view
from shared import DisplayContext
from components import Section, StatsRow

DISTRIBUTIONS = ["Normal", "Exponential", "Uniform", "Bimodal"]


def _compute_distribution(dist, loc, scale, seed, n_samples):
    """Pure computation — no side effects."""
    rng = np.random.default_rng(seed=seed)
    generators = {
        "Normal": lambda: rng.normal(loc, max(scale, 0.01), n_samples),
        "Exponential": lambda: rng.exponential(max(scale, 0.01), n_samples) + loc,
        "Uniform": lambda: rng.uniform(loc - scale, loc + scale, n_samples),
        "Bimodal": lambda: np.concatenate([
            rng.normal(loc - scale, max(scale * 0.4, 0.01), n_samples // 2),
            rng.normal(loc + scale, max(scale * 0.4, 0.01), n_samples - n_samples // 2),
        ]),
    }
    samples = generators.get(dist, generators["Normal"])()
    samples = samples[(samples >= -10) & (samples <= 10)]
    counts, edges = np.histogram(samples, bins=30, range=(-10, 10))
    m, s = float(np.mean(samples)), float(np.std(samples))
    skew = float(np.mean(((samples - m) / s) ** 3)) if s > 0 else 0.0

    return {
        "mean": round(m, 3), "std": round(s, 3), "skewness": round(skew, 3),
        "p5": round(float(np.percentile(samples, 5)), 3),
        "p95": round(float(np.percentile(samples, 95)), 3),
        "bin_starts": edges[:-1].tolist(),
        "bin_ends": edges[1:].tolist(),
        "counts": counts.tolist(),
    }


class DistributionAnalyzer(stc.Component):
    class DistState(stc.State):
        dist: str = "Normal"
        loc: float = 0.0
        scale: float = 1.0

    def render(self):
        settings = stc.get_shared_state("settings")
        display = stc.use_context(DisplayContext)

        computed = stc.use_memo(
            lambda: _compute_distribution(
                self.state.dist, self.state.loc, self.state.scale,
                settings.seed, settings.n_samples,
            ),
            deps=[self.state.dist, self.state.loc, self.state.scale,
                  settings.seed, settings.n_samples],
        )

        hist_df = pd.DataFrame({
            "start": computed["bin_starts"],
            "end": computed["bin_ends"],
            "count": computed["counts"],
        })
        chart = (
            alt.Chart(hist_df)
            .mark_bar(stroke="white", strokeWidth=0.5)
            .encode(
                x=alt.X("start:Q", scale=alt.Scale(domain=[-10, 10]), title="value"),
                x2="end:Q",
                y=alt.Y("count:Q", title="count"),
            )
            .properties(height=display.chart_height)
        )

        return container(key="page")(
            Section(key="header", title="Distribution Analyzer",
                    description="Pick a distribution and adjust parameters — or change seed/samples in the sidebar."),
            columns(key="controls")(
                selectbox(key="dist", options=DISTRIBUTIONS,
                          index=DISTRIBUTIONS.index(self.state.dist),
                          on_change=self.sync_state("dist"))("Distribution"),
                slider(key="loc", min_value=-5.0, max_value=5.0, step=0.5,
                       value=self.state.loc, on_change=self.sync_state("loc"))("Center (μ)"),
                slider(key="scale", min_value=0.1, max_value=5.0, step=0.1,
                       value=self.state.scale, on_change=self.sync_state("scale"))("Spread (σ)"),
            ),
            StatsRow(key="stats", stats=[
                {"label": "Mean", "value": computed["mean"]},
                {"label": "Std", "value": computed["std"]},
                {"label": "Skew", "value": computed["skewness"]},
                {"label": "P5", "value": computed["p5"]},
                {"label": "P95", "value": computed["p95"]},
            ]) if display.show_stats else None,
            altair_chart(key="hist", width="stretch")(chart),
            source_view(__file__),
        )


stc.get_app().render_page(DistributionAnalyzer(key="root"))
