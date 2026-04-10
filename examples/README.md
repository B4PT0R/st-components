# Examples

Each example is a self-contained Streamlit app. They are numbered to form a
guided progression — start at 01 and work your way up.

```bash
# Via the installed runner
python -m st_components.examples 01_hello
python -m st_components.examples --list

# Or directly
streamlit run examples/01_hello.py
```

## Guided progression

| # | File | What you learn |
|---|---|---|
| 01 | `01_hello.py` | Component, State, render — the absolute minimum |
| 02 | `02_state.py` | Typed State, multi-field state, fiber persistence |
| 03 | `03_callbacks.py` | on_change receives the value, sync_state shortcut |
| 04 | `04_composition.py` | Children, nesting, layout, reusable building blocks |
| 05 | `05_elements.py` | Catalog of every built-in element wrapper |
| 06 | `06_functional.py` | @component decorator, use_state, class vs functional |
| 07 | `07_refs.py` | self.ref, self.parent, self.root, attribute navigation, fiber overrides |
| 08 | `08_hooks.py` | use_memo, use_effect, use_ref, use_callback, use_previous, use_id |
| 09 | `09_fragments.py` | fragment, scoped re-rendering, run_every, nested fragments |
| 10 | `10_scoped_rerun.py` | rerun, wait, independent per-fragment rerun timelines |
| 11 | `11_dynamic_rendering.py` | self.ref(path), fiber overrides, Ref.parent, column/tab scoping |
| 12 | `12_context.py` | create_context, Provider, use_context — no prop drilling |
| 13 | `13_flow.py` | Conditional, KeepAlive, Case, Switch/Match/Default |
| 14 | `14_theming.py` | ThemeEditorButton, live theme customization |
| 15 | `15_multipage/` | Router, Page, shared state, file-backed pages |
| 16 | `16_full_data_app/` | Multipage data-science app — all features combined |
