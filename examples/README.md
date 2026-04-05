# Examples

Each example is a self-contained Streamlit app. Run them from the project root.

## basic.py

The minimal entry point. A single stateful `Counter` component — nothing else.

```bash
streamlit run examples/basic.py
```

## data_dashboard.py

A data-science oriented dashboard that shows how Python computation (numpy signal analysis, histogram stats, least-squares regression) lives inside **component methods and callbacks**, keeping the render layer thin. Three panels: Signal Explorer (FFT + rolling mean), Distribution Analyzer (descriptive stats + histogram), Regression Playground (polyfit + R²).

```bash
streamlit run examples/data_dashboard.py
```

## dashboard.py

A fuller tutorial that walks through the core patterns: local component state, `get_element_value()`, `Ref`, callbacks, and layout composition.

```bash
streamlit run examples/dashboard.py
```

## flow.py

Small demo of the flow built-ins: `Conditional`, `KeepAlive`, `Case`, and `Switch`/`Match`/`Default`.

```bash
streamlit run examples/flow.py
```

## functional_typed.py

Typed state and props for functional components: `use_state()` with a `State` instance, `@component` with a typed `Props` annotation, and combining both.

```bash
streamlit run examples/functional_typed.py
```

## functional.py

Demonstrates the `@component` decorator and `use_state` hook for defining components as plain functions instead of classes.

```bash
streamlit run examples/functional.py
```

## primitives.py

A kitchen-sink reference of every built-in element wrapper: inputs, layout, display, media, feedback, and charts.

```bash
streamlit run examples/primitives.py
```

## typed_state.py

Demonstrates typed state schemas using nested `State` subclasses: single-field state without `__init__`, multi-field structured state, and type validation at definition and assignment time.

```bash
streamlit run examples/typed_state.py
```

## typed_props.py

Demonstrates typed props schemas using nested `Props` subclasses: default prop values, `extra="ignore"` for permissive pass-through components, and `extra="forbid"` for strict interface enforcement.

```bash
streamlit run examples/typed_props.py
```

## theme_editor.py

Minimal demo of the `ThemeEditorButton` builtin. Open the dialog from a prewired button and edit the current `App` theme live.

```bash
streamlit run examples/theme_editor.py
```

## multipage/

A multipage app using `Router`, `Page`, and `shared_state`. Shows both inline component pages and file-backed pages synchronized through shared state.

```bash
streamlit run examples/multipage/app.py
```

See [multipage/README.md](multipage/README.md) for details.
