"""
Signal Explorer page.

Demonstrates:
- use_memo for reactive computation (recalculates when ANY input changes)
- Shared state as computation input (seed, n_samples from sidebar)
- Separation of computation from rendering
"""
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parents[1]
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import st_components as stc
from st_components.elements import (
    caption, columns, container, divider, line_chart, markdown, slider,
)
from examples._source import source_view
from shared import AppSidebar, DisplayContext
from components import Section, StatsRow


def _compute_signal(freq, noise, seed, n_samples):
    """Pure computation — no side effects, no state."""
    t = np.linspace(0, 4 * np.pi, n_samples)
    clean = np.sin(freq * t) + 0.4 * np.sin(3 * freq * t)
    rng = np.random.default_rng(seed=seed)
    noisy = clean + rng.normal(0, noise, size=n_samples)

    window = max(5, n_samples // 20)
    smooth = np.convolve(noisy, np.ones(window) / window, mode="same")

    signal_power = np.mean(clean ** 2)
    noise_power = noise ** 2
    snr_db = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float("inf")

    fft_mag = np.abs(np.fft.rfft(noisy))
    freqs = np.fft.rfftfreq(n_samples, d=(t[1] - t[0]))
    dominant = freqs[np.argmax(fft_mag[1:]) + 1]

    return {
        "signal": noisy.tolist(),
        "smooth": smooth.tolist(),
        "dominant_freq": round(float(dominant), 3),
        "snr_db": round(float(snr_db), 1),
    }


class SignalExplorer(stc.Component):
    class SignalState(stc.State):
        freq: float = 2.0
        noise: float = 0.3

    def render(self):
        settings = stc.get_shared_state("settings")
        display = stc.use_context(DisplayContext)

        # use_memo: recomputes only when ANY input changes
        computed = stc.use_memo(
            lambda: _compute_signal(
                self.state.freq, self.state.noise,
                settings.seed, settings.n_samples,
            ),
            deps=[self.state.freq, self.state.noise, settings.seed, settings.n_samples],
        )

        return container(key="page")(
            AppSidebar(key="sidebar"),
            Section(key="header", title="Signal Explorer",
                    description="Adjust frequency and noise — or change seed/samples in the sidebar. "
                                "Computation reruns automatically via use_memo when any input changes."),
            columns(key="controls")(
                slider(key="freq", min_value=0.5, max_value=8.0, step=0.5,
                       value=self.state.freq,
                       on_change=self.sync_state("freq"))("Base frequency"),
                slider(key="noise", min_value=0.0, max_value=2.0, step=0.05,
                       value=self.state.noise,
                       on_change=self.sync_state("noise"))("Noise level (σ)"),
            ),
            StatsRow(key="stats", stats=[
                {"label": "SNR (dB)", "value": computed["snr_db"]},
                {"label": "Dominant freq", "value": computed["dominant_freq"]},
                {"label": "Samples", "value": settings.n_samples},
                {"label": "Seed", "value": settings.seed},
            ]) if display.show_stats else None,
            line_chart(key="chart", data={
                "noisy": computed["signal"],
                "smoothed": computed["smooth"],
            }, height=display.chart_height),
            source_view(__file__),
        )


stc.get_app().render_page(SignalExplorer(key="root"))
