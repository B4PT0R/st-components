# 17 - Full Data App

A realistic multipage data-science application built with st-components.

```bash
streamlit run examples/17_full_data_app/app.py
```

## Structure

```
17_full_data_app/
├── app.py              # Entry point: Router(chrome=AppChrome), Pages, shared state, context
├── shared.py           # AppSettings, DisplayContext, AppSidebar, AppFooter, AppChrome
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
| **Chrome wrapper** | `Router(chrome=AppChrome)` — sidebar + footer rendered once around every page; chrome fiber lives at `app.router.chrome`, so its state survives navigation |
| **Shared state** | `shared.py` — AppSettings shared across all pages via sidebar |
| **Context** | `shared.py` → `app.py` — DisplayContext wraps the router |
| **Typed State** | Every page component — multi-field State with defaults |
| **Typed Props** | `components.py` — StatCard, Section with validated interfaces |
| **Lifecycle hooks** | `component_did_mount` triggers initial computation |
| **Computation in callbacks** | `_recompute` / `_analyze` / `_fit` — numpy runs in callbacks, not render |
| **Reusable components** | AppSidebar, AppFooter, StatsRow, Section composed freely |
| **use_context** | Pages read DisplayConfig for conditional stats / chart height |
| **set_state** | Regression page batch-resets via `set_state(slope=..., noise=...)` |
| **sync_state** | Sidebar sliders use `sync_state`-like lambdas |

## Best practices shown

1. **Chrome for shared layout** — sidebar and footer live in `AppChrome` (the Router's chrome wrapper), not in each page. Pages only render their own content; the chrome takes care of everything else around them. Chrome's fiber sits above the page key in the tree (`app.router.chrome`), so chrome state survives navigation — useful for things like a global search box or breadcrumbs with history.
2. **Separate computation from rendering** — numpy/pandas logic lives in `_recompute()` methods, called from callbacks. `render()` only lays out the results.
3. **Shared state for cross-page data** — sidebar controls write to a single `AppSettings` instance read on every page.
4. **Context for ambient config** — display preferences (show stats, chart height) flow through the tree without being threaded as props.
5. **Typed interfaces** — every component declares its Props/State as inner classes, making the API self-documenting.
6. **Small reusable components** — `StatCard`, `StatsRow`, `Section` are thin wrappers that can be composed freely.
