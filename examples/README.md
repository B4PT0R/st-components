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
| 05 | `05_styles.py` | Inline `style=` dict, slot-based targeting, scoped CSS, pseudo-classes |
| 06 | `06_elements.py` | Catalog of every built-in element wrapper |
| 07 | `07_functional.py` | @component decorator, use_state, class vs functional |
| 08 | `08_refs.py` | self.ref, self.parent, self.root, attribute navigation, fiber overrides |
| 09 | `09_hooks.py` | use_memo, use_effect, use_ref, use_callback, use_previous, use_id |
| 10 | `10_fragments.py` | fragment, scoped re-rendering, run_every, nested fragments |
| 11 | `11_scoped_rerun.py` | rerun, wait, independent per-fragment rerun timelines |
| 12 | `12_dynamic_rendering.py` | self.ref(path), fiber overrides, Ref.parent, column/tab scoping |
| 13 | `13_context.py` | create_context, Provider, use_context — no prop drilling |
| 14 | `14_flow.py` | Conditional, KeepAlive, Case, Switch/Match/Default |
| 15 | `15_theming.py` | ThemeEditorButton, live theme customization |
| 16 | `16_multipage/` | Router, Page, chrome wrapper, shared state, file-backed pages |
| 17 | `17_full_data_app/` | Multipage data-science app — all features combined |
