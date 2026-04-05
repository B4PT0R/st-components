# Examples

Each example is a self-contained Streamlit app.

Installed package:

```bash
python -m st_components.examples <name>
python -m st_components.examples --list
```

From the repository root, you can also run the files directly with `streamlit run`.

## basic.py

The minimal entry point. A single stateful `Counter` component — nothing else.

```bash
python -m st_components.examples basic
streamlit run examples/basic.py
```

## data_dashboard.py

A data-science oriented dashboard that shows how Python computation (numpy signal analysis, histogram stats, least-squares regression) lives inside **component methods and callbacks**, keeping the render layer thin. Three panels: Signal Explorer (FFT + rolling mean), Distribution Analyzer (descriptive stats + histogram), Regression Playground (polyfit + R²).

```bash
python -m st_components.examples data_dashboard
streamlit run examples/data_dashboard.py
```

## dashboard.py

A fuller tutorial that walks through the core patterns: local component state, `on_change(value)` callbacks, `Ref`, and layout composition.

```bash
python -m st_components.examples dashboard
streamlit run examples/dashboard.py
```

## flow.py

Small demo of the flow built-ins: `Conditional`, `KeepAlive`, `Case`, and `Switch`/`Match`/`Default`.

```bash
python -m st_components.examples flow
streamlit run examples/flow.py
```

## functional_typed.py

Typed state and props for functional components: `use_state()` with a `State` instance, `@component` with a typed `Props` annotation, and combining both.

```bash
python -m st_components.examples functional_typed
streamlit run examples/functional_typed.py
```

## functional.py

Demonstrates the `@component` decorator and `use_state` hook for defining components as plain functions instead of classes.

```bash
python -m st_components.examples functional
streamlit run examples/functional.py
```

## primitives.py

A kitchen-sink reference of every built-in element wrapper: inputs, layout, display, media, feedback, and charts.

```bash
python -m st_components.examples primitives
streamlit run examples/primitives.py
```

## typed_state.py

Demonstrates typed state schemas using nested `State` subclasses: single-field state without `__init__`, multi-field structured state, and type validation at definition and assignment time.

```bash
python -m st_components.examples typed_state
streamlit run examples/typed_state.py
```

## typed_props.py

Demonstrates typed props schemas using nested `Props` subclasses: default prop values, `extra="ignore"` for permissive pass-through components, and `extra="forbid"` for strict interface enforcement.

```bash
python -m st_components.examples typed_props
streamlit run examples/typed_props.py
```

## theme_editor.py

Minimal demo of the `ThemeEditorButton` builtin. Open the dialog from a prewired button and edit the current `App` theme live.

```bash
python -m st_components.examples theme_editor
streamlit run examples/theme_editor.py
```

## multipage/

A multipage app using `Router`, `Page`, and `shared_state`. Shows both inline component pages and file-backed pages synchronized through shared state.

```bash
python -m st_components.examples multipage
streamlit run examples/multipage/app.py
```

See [multipage/README.md](multipage/README.md) for details.
