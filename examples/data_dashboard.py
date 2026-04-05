"""
Data science dashboard — shows how Python computation lives naturally in
component methods and callbacks, keeping Streamlit's render layer thin.

Run:
    streamlit run examples/data_dashboard.py
"""
import altair as alt
import numpy as np
import pandas as pd

from st_components import App, Component, State, get_element_value
from st_components.elements import (
    altair_chart, button, caption, columns, container, divider,
    line_chart, markdown, metric, sidebar,
    slider, subheader, tabs, text, title, selectbox,
)


# ---------------------------------------------------------------------------
# 1. Signal Explorer
#    Sliders drive frequency / noise.  Computation (FFT + rolling mean)
#    lives entirely in _recompute(), called from callbacks.
# ---------------------------------------------------------------------------

class SignalExplorer(Component):
    class SignalState(State):
        freq: float = 2.0
        noise: float = 0.3
        n_samples: int = 300
        # stored as lists so they survive rerun serialisation
        t: list = []
        signal: list = []
        smooth: list = []
        dominant_freq: float = 0.0
        snr_db: float = 0.0

    def component_did_mount(self):
        self._recompute()

    # ----- computation -----

    def _recompute(self):
        t = np.linspace(0, 4 * np.pi, self.state.n_samples)
        clean = np.sin(self.state.freq * t) + 0.4 * np.sin(3 * self.state.freq * t)
        rng = np.random.default_rng(seed=42)
        noisy = clean + rng.normal(0, self.state.noise, size=len(t))

        window = max(5, len(t) // 20)
        kernel = np.ones(window) / window
        smooth = np.convolve(noisy, kernel, mode="same")

        # signal power vs noise power
        signal_power = np.mean(clean ** 2)
        noise_power = self.state.noise ** 2
        snr_db = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float("inf")

        # dominant frequency via FFT
        fft_mag = np.abs(np.fft.rfft(noisy))
        freqs = np.fft.rfftfreq(len(t), d=(t[1] - t[0]))
        dominant = freqs[np.argmax(fft_mag[1:]) + 1]

        self.state.t = t.tolist()
        self.state.signal = noisy.tolist()
        self.state.smooth = smooth.tolist()
        self.state.dominant_freq = round(float(dominant), 3)
        self.state.snr_db = round(float(snr_db), 1)

    # ----- callbacks -----

    def on_freq_change(self):
        self.state.freq = get_element_value()
        self._recompute()

    def on_noise_change(self):
        self.state.noise = get_element_value()
        self._recompute()

    def on_samples_change(self):
        self.state.n_samples = int(get_element_value())
        self._recompute()

    # ----- render -----

    def render(self):
        chart_data = {
            "noisy signal": self.state.signal,
            "smoothed": self.state.smooth,
        }

        return container(key="panel", border=True)(
            subheader(key="h")("Signal Explorer"),
            caption(key="c")(
                "Adjust frequency and noise. The component recomputes FFT and "
                "rolling average in the callback — no rerun needed for the math."
            ),
            columns(key="controls")(
                slider(
                    key="freq",
                    min_value=0.5, max_value=8.0, step=0.5,
                    value=self.state.freq,
                    on_change=self.on_freq_change,
                )("Base frequency"),
                slider(
                    key="noise",
                    min_value=0.0, max_value=2.0, step=0.05,
                    value=self.state.noise,
                    on_change=self.on_noise_change,
                )("Noise σ"),
                slider(
                    key="samples",
                    min_value=50, max_value=800, step=50,
                    value=self.state.n_samples,
                    on_change=self.on_samples_change,
                )("Samples"),
            ),
            columns(key="stats")(
                metric(key="snr", label="SNR (dB)", value=self.state.snr_db),
                metric(key="dom_freq", label="Dominant freq (rad/sample)", value=self.state.dominant_freq),
                metric(key="n", label="Samples", value=self.state.n_samples),
            ),
            line_chart(key="chart", data=chart_data, height=280),
        )


# ---------------------------------------------------------------------------
# 2. Distribution Analyzer
#    Generates samples from a chosen distribution, computes descriptive
#    stats and histogram in _analyze() — called from callbacks.
# ---------------------------------------------------------------------------

DISTRIBUTIONS = ["Normal", "Exponential", "Uniform", "Bimodal"]


class DistributionAnalyzer(Component):
    class DistState(State):
        dist: str = "Normal"
        loc: float = 0.0
        scale: float = 1.0
        n: int = 500
        mean: float = 0.0
        std: float = 1.0
        skewness: float = 0.0
        p5: float = 0.0
        p95: float = 0.0
        bin_starts: list = []
        bin_ends: list = []
        counts: list = []

    def component_did_mount(self):
        self._analyze()

    # ----- computation -----

    def _analyze(self):
        rng = np.random.default_rng(seed=0)
        dist = self.state.dist
        loc, scale, n = self.state.loc, self.state.scale, self.state.n

        if dist == "Normal":
            samples = rng.normal(loc, max(scale, 0.01), n)
        elif dist == "Exponential":
            samples = rng.exponential(max(scale, 0.01), n) + loc
        elif dist == "Uniform":
            samples = rng.uniform(loc - scale, loc + scale, n)
        else:  # Bimodal
            s1 = rng.normal(loc - scale, max(scale * 0.4, 0.01), n // 2)
            s2 = rng.normal(loc + scale, max(scale * 0.4, 0.01), n - n // 2)
            samples = np.concatenate([s1, s2])

        samples = samples[(samples >= -10) & (samples <= 10)]
        counts, bin_edges = np.histogram(samples, bins=30, range=(-10, 10))

        m = float(np.mean(samples))
        s = float(np.std(samples))
        skew = float(np.mean(((samples - m) / s) ** 3)) if s > 0 else 0.0

        self.state.mean = round(m, 3)
        self.state.std = round(s, 3)
        self.state.skewness = round(skew, 3)
        self.state.p5 = round(float(np.percentile(samples, 5)), 3)
        self.state.p95 = round(float(np.percentile(samples, 95)), 3)
        self.state.bin_starts = bin_edges[:-1].tolist()
        self.state.bin_ends = bin_edges[1:].tolist()
        self.state.counts = counts.tolist()

    # ----- callbacks -----

    def on_dist_change(self):
        self.state.dist = get_element_value()
        self._analyze()

    def on_loc_change(self):
        self.state.loc = get_element_value()
        self._analyze()

    def on_scale_change(self):
        self.state.scale = get_element_value()
        self._analyze()

    def on_n_change(self):
        self.state.n = int(get_element_value())
        self._analyze()

    # ----- render -----

    def render(self):
        hist_df = pd.DataFrame({
            "start": self.state.bin_starts,
            "end": self.state.bin_ends,
            "count": self.state.counts,
        })
        hist_spec = (
            alt.Chart(hist_df)
            .mark_bar(stroke="white", strokeWidth=0.5)
            .encode(
                x=alt.X("start:Q", scale=alt.Scale(domain=[-10, 10]), title="value"),
                x2="end:Q",
                y=alt.Y("count:Q", title="count"),
            )
            .properties(height=260)
        )

        return container(key="panel", border=True)(
            subheader(key="h")("Distribution Analyzer"),
            caption(key="c")(
                "Choose a distribution family and parameters. "
                "Descriptive stats (mean, std, skewness, percentiles) are "
                "computed from numpy samples inside the callback."
            ),
            columns(key="controls")(
                selectbox(
                    key="dist",
                    options=DISTRIBUTIONS,
                    index=DISTRIBUTIONS.index(self.state.dist),
                    on_change=self.on_dist_change,
                )("Distribution"),
                slider(
                    key="loc",
                    min_value=-5.0, max_value=5.0, step=0.5,
                    value=self.state.loc,
                    on_change=self.on_loc_change,
                )("Center (μ)"),
                slider(
                    key="scale",
                    min_value=0.1, max_value=5.0, step=0.1,
                    value=self.state.scale,
                    on_change=self.on_scale_change,
                )("Spread (σ)"),
                slider(
                    key="n",
                    min_value=100, max_value=5000, step=100,
                    value=self.state.n,
                    on_change=self.on_n_change,
                )("Samples"),
            ),
            columns(key="stats")(
                metric(key="mean", label="Mean", value=self.state.mean),
                metric(key="std", label="Std dev", value=self.state.std),
                metric(key="skew", label="Skewness", value=self.state.skewness),
                metric(key="p5", label="P5", value=self.state.p5),
                metric(key="p95", label="P95", value=self.state.p95),
            ),
            altair_chart(key="hist", width="stretch")(hist_spec),
        )


# ---------------------------------------------------------------------------
# 3. Regression Playground
#    Generates synthetic (x, y) data with configurable noise and a hidden
#    slope.  On every change, _fit() runs numpy polyfit to recover the slope
#    and computes R².  Computation lives in the component, not in Streamlit.
# ---------------------------------------------------------------------------

class RegressionPlayground(Component):
    class RegrState(State):
        true_slope: float = 1.5
        noise: float = 0.5
        n: int = 80
        fitted_slope: float = 0.0
        fitted_intercept: float = 0.0
        r2: float = 0.0
        x: list = []
        y_noisy: list = []
        y_fit: list = []

    def component_did_mount(self):
        self._fit()

    # ----- computation -----

    def _fit(self):
        rng = np.random.default_rng(seed=7)
        x = np.linspace(-3, 3, self.state.n)
        y_clean = self.state.true_slope * x + 0.5
        y_noisy = y_clean + rng.normal(0, max(self.state.noise, 0.01), self.state.n)

        coeffs = np.polyfit(x, y_noisy, deg=1)
        slope, intercept = float(coeffs[0]), float(coeffs[1])
        y_fit = slope * x + intercept

        ss_res = np.sum((y_noisy - y_fit) ** 2)
        ss_tot = np.sum((y_noisy - np.mean(y_noisy)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

        self.state.fitted_slope = round(slope, 3)
        self.state.fitted_intercept = round(intercept, 3)
        self.state.r2 = round(float(r2), 4)
        self.state.x = x.tolist()
        self.state.y_noisy = y_noisy.tolist()
        self.state.y_fit = y_fit.tolist()

    # ----- callbacks -----

    def on_slope_change(self):
        self.state.true_slope = get_element_value()
        self._fit()

    def on_noise_change(self):
        self.state.noise = get_element_value()
        self._fit()

    def on_n_change(self):
        self.state.n = int(get_element_value())
        self._fit()

    def reset(self):
        self.state.true_slope = 1.5
        self.state.noise = 0.5
        self.state.n = 80
        self._fit()

    # ----- render -----

    def render(self):
        slope_error = round(abs(self.state.fitted_slope - self.state.true_slope), 3)

        # scatter + fit line
        scatter_data = {
            "observed": self.state.y_noisy,
            "fit": self.state.y_fit,
        }

        return container(key="panel", border=True)(
            subheader(key="h")("Regression Playground"),
            caption(key="c")(
                "Set the true slope and noise level. The component fits a "
                "least-squares line via numpy inside the callback and computes R²."
            ),
            columns(key="controls")(
                slider(
                    key="slope",
                    min_value=-4.0, max_value=4.0, step=0.25,
                    value=self.state.true_slope,
                    on_change=self.on_slope_change,
                )("True slope"),
                slider(
                    key="noise",
                    min_value=0.0, max_value=3.0, step=0.1,
                    value=self.state.noise,
                    on_change=self.on_noise_change,
                )("Noise σ"),
                slider(
                    key="n",
                    min_value=10, max_value=300, step=10,
                    value=self.state.n,
                    on_change=self.on_n_change,
                )("Data points"),
            ),
            columns(key="stats")(
                metric(key="true_slope", label="True slope", value=self.state.true_slope),
                metric(key="fit_slope", label="Fitted slope", value=self.state.fitted_slope),
                metric(key="error", label="Slope error", value=slope_error),
                metric(key="r2", label="R²", value=self.state.r2),
            ),
            line_chart(key="chart", data=scatter_data, height=280),
            button(key="reset", on_click=self.reset)("Reset defaults"),
        )


# ---------------------------------------------------------------------------
# Top-level layout
# ---------------------------------------------------------------------------

class DSSidebar(Component):
    def render(self):
        return sidebar(key="sidebar")(
            title(key="title")("Data Dashboard"),
            caption(key="sub")("st-components · data science patterns"),
            divider(key="d"),
            markdown(key="desc")(
                "This dashboard shows how Python computation belongs "
                "in **component methods and callbacks**, not in the render "
                "layer.\n\n"
                "Each panel:\n"
                "- holds its computed results in **component state**\n"
                "- runs numpy in a `_compute()` method\n"
                "- calls that method from **on_change callbacks**\n\n"
                "Streamlit only sees the final numbers and chart data."
            ),
            divider(key="d2"),
            text(key="pattern")("Pattern"),
            markdown(key="pattern_code")(
                "```python\n"
                "def on_param_change(self):\n"
                "    self.state.param = get_element_value()\n"
                "    self._recompute()   # ← numpy lives here\n"
                "```"
            ),
        )


class DataDashboard(Component):
    def render(self):
        return container(key="page")(
            DSSidebar(key="sidebar"),
            tabs(key="panels", labels=["Signal", "Distribution", "Regression"])(
                SignalExplorer(key="signal"),
                DistributionAnalyzer(key="dist"),
                RegressionPlayground(key="regression"),
            ),
        )


App(root=DataDashboard(key="ds_dashboard")).render()
