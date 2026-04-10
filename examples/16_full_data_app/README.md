# 12 - Full Data App

A realistic multipage data-science application built with st-components.

```bash
streamlit run examples/12_full_data_app/app.py
```

## Structure

```
12_full_data_app/
├── app.py              # Entry point: Router, Pages, shared state, context
├── shared.py           # AppSettings, DisplayContext, AppSidebar
├── components.py       # Reusable data viz components (StatCard, StatsRow, Section)
└── pages/
    ├── signal_page.py        # FFT + rolling average
    ├── distribution_page.py  # Histogram + descriptive stats
    └── regression_page.py    # Least-squares fit + R²
```

## Features demonstrated

| Feature | Where |
|---|---|
| **Multipage routing** | `app.py` — Router / Page with file-backed sources |
| **Shared state** | `shared.py` — AppSettings shared across all pages via sidebar |
| **Context** | `shared.py` → `app.py` — DisplayContext wraps the router |
| **Typed State** | Every page component — multi-field State with defaults |
| **Typed Props** | `components.py` — StatCard, Section with validated interfaces |
| **Lifecycle hooks** | `component_did_mount` triggers initial computation |
| **Computation in callbacks** | `_recompute` / `_analyze` / `_fit` — numpy runs in callbacks, not render |
| **Reusable components** | AppSidebar, StatsRow, Section used across all pages |
| **use_context** | Pages read DisplayConfig for conditional stats / chart height |
| **set_state** | Regression page batch-resets via `set_state(slope=..., noise=...)` |
| **sync_state** | Sidebar sliders use `sync_state`-like lambdas |

## Best practices shown

1. **Separate computation from rendering** — numpy/pandas logic lives in `_recompute()` methods, called from callbacks. `render()` only lays out the results.
2. **Shared state for cross-page data** — sidebar controls are the same on every page, writing to the same `AppSettings` instance.
3. **Context for ambient config** — display preferences (show stats, chart height) flow through the tree without being threaded as props.
4. **Typed interfaces** — every component declares its Props/State as inner classes, making the API self-documenting.
5. **Small reusable components** — `StatCard`, `StatsRow`, `Section` are thin wrappers that can be composed freely.
