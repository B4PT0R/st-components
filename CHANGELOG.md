# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses SemVer.

## [0.2.0] - 2026-04-09

Element authoring toolkit: `element_factory`, context-based widget helpers, and simplified `get_output` API.

### Added

- **`st_components/elements/factory.py`** — new module providing a complete toolkit for authoring custom element wrappers:
  - `element_factory(streamlit_fn, *, child_prop, callback_prop, default_prop, props_schema, spec_prop, spec_type, has_key)` — generates a typed `Element` subclass from a `st.*` callable and a few metadata args. Handles three rendering patterns automatically: plain widgets, single context-manager containers (e.g. `st.expander`), and multi-container functions (e.g. `st.columns`, `st.tabs`) where children are zipped with the returned context managers. The `spec_prop` / `spec_type` parameters control how the spec argument is derived from children count (`"int"` → `len(children)`, `"list"` → `[str(i) for i in range(len(children))]`); `has_key=False` skips the `key=widget_key()` argument for functions that don't accept it.
  - `widget_child(prop_name, default=None)` — returns `props.children[0]` if children are present, otherwise `props.get(prop_name, default)`.
  - `widget_props(*excluded)` — returns all props minus `key`, `children`, `ref`, and any extra names to exclude.
  - `widget_callback(prop_name="on_change")` — reads the named prop from the current render context and wraps it with `callback()`.
  - Re-exports `Element`, `callback`, `widget_key`, `widget_output` for one-stop imports in element modules.

### Changed

- **`get_output(raw)` replaces `get_output_default()`**: the single override hook now receives `raw` (the raw session_state value, or `None` before the widget is first registered). The base implementation returns `raw`. Element subclasses that need a non-`None` initial value override `get_output` and use `self.props.get(prop)` when `raw is None`.
- **`callback(fn)` is now in `core/access.py`** (not `core/__init__.py`); `widget_callback` definition moved from `core/access.py` into `factory.py`.
- `_utils.py` deleted — its content (`widget_child`, `widget_props`, `_props`) merged into `factory.py`.
- All built-in input elements (`checkbox`, `toggle`, `text_input`, `text_area`, `number_input`, `slider`, `select_slider`, `radio`, `selectbox`, `multiselect`, `pills`, `segmented_control`, `feedback`) updated to use the new context-based helpers and `get_output` pattern.

## [0.1.6] - 2026-04-08

Element fiber, unified state API, and API surface cleanup.

### Added

- `ElementFiber` — every rendered `Element` now has a lightweight fiber in `st.session_state` holding its path, widget key, hooks, and a post-processed value cache.
- Hook support in `Element.render()`: `use_effect`, `use_memo`, `use_ref`, `use_callback`, `use_previous`, `use_id`, and `use_context` all work inside custom element subclasses (same rules as in `Component`, except `use_state` which is reserved for functional components).
- `get_state(path_or_ref=None)` — unified state accessor that works for both Elements and Components:
  - for an Element it returns an `ElementState` with a `value` field
  - for a Component it returns its `State` dict
  - returns `None` if the path doesn't resolve to a live fiber
- `ElementState` — a `State` subclass with a single `value` field, returned by `ElementFiber.state`.

### Changed

- **Unified element value storage**: all Streamlit-keyed widget values are now stored under `{path}.raw` (previously `.value`). The `.raw` suffix makes the Streamlit-owned key explicit and leaves `.value` unambiguous as the post-processed accessor via `ElementState.value`.
- **`get_state` replaces `get_element_value` and `get_component_state`**: both old functions still exist for backwards compatibility but the unified `get_state` is now the documented API.
- **`Ref.state()` is now the only state accessor on `Ref`**: `ref.value()` has been removed. Use `ref.state().value` to read an element value through a ref.
- `ElementFiber.state` is a computed modict field that reads from the fiber's cache if set, or falls back to `st.session_state[widget_key]`.
- README and examples updated throughout to use `get_state(...)` and `ref.state().value`.

## [0.1.5] - 2026-04-07

Tree-model and hooks/context stabilization release.

### Added

- Expanded the hook surface with:
  - `use_memo(...)`
  - `use_effect(...)`
  - `use_ref(...)`
  - `use_callback(...)`
  - `use_previous(...)`
  - `use_id(...)`
  - `use_context(...)`
- Added scoped context support with:
  - `create_context(...)`
  - `ContextData`
  - typed `Provider(data=...)` values normalized to the context schema
- Added a dedicated `hooks` example and extended the multipage example to exercise tree-scoped context above `Router(...)`.

### Changed

- Reworked the structural tree model so `App`, `Router`, and `Page` are now real structural components.
- Paths now follow the actual rendered tree and start at the fixed app root key:
  - `app...`
  - multipage paths now use component keys instead of the old `page[...]` namespace layer
- Simplified `App` creation:
  - removed the `root=` prop
  - the app tree is now passed only through `children=` or `App(...)(...)`
- Clarified context semantics:
  - `create_context(...)` remains a free helper suitable for module-level declarations
  - each provider replaces the current scoped context value instead of implicitly merging with the parent scope
- Reworked the README and examples to match the stabilized tree, hooks, and context APIs.

## [0.1.4] - 2026-04-06

API clarification and documentation pass.

### Changed

- Simplified callback semantics across input elements:
  - event handlers now receive only the element payload when the event carries one
  - plain click handlers now receive no injected extra arguments
  - removed callback `args` / `kwargs` plumbing from element APIs to keep the mental model explicit
- Clarified `App` lifecycle and naming:
  - shared state declaration is now exposed as `App.create_shared_state(...)`
  - page rendering now goes through the current app instance via `get_app().render_page(...)`
  - `App.render()` no longer accepts navigation overrides and relies on `Router(...)` props instead
- Tightened the render contract:
  - `Element.render()` is now fully side-effect oriented and does not expose a return-value data channel
  - primitive values are rendered directly through the component tree rather than treated as element return values
- Reworked the README substantially:
  - documented the JSX-like two-step props/children creation pattern
  - expanded `App` constructor and method documentation
  - clarified callbacks, refs, elements, state, props, built-ins, examples, and usage guidelines
- Updated examples and tests to match the simplified callback model and clarified API names.

## [0.1.3] - 2026-04-06

Runtime/value-channel cleanup and feedback primitive expansion.

### Added

- Declarative `spinner(...)` Element for wrapping slow-to-render children.
- Declarative `progress(...)` Element that stores its runtime handle in the element value channel, so it can be reached later through `ref.value()`.
- Runtime helpers for callback-only effects:
  - `show_spinner(...)`
  - `show_progress(...)`
  - `show_balloons()`
  - `show_snow()`
  - `show_toast(...)`
- Expanded `primitives` demo coverage and runtime-oriented examples for feedback/media/layout edge cases.

### Changed

- Clarified and standardized the render contract:
  - `Component.render()` composes and may return Components, Elements, or plain renderable values
  - `Element.render()` performs Streamlit side effects and does not use its return value as a data channel
  - runtime values now flow explicitly through `set_element_value(...)` / `get_element_value(...)`
- Standardized element value storage around the canonical `"{element_path}.value"` key.
- Stateful widget value access and runtime handle access now share the same logical retrieval API:
  - current callback context
  - explicit element path
  - `Ref`
- Reworked the `primitives` example app so the demo components are more self-contained and pedagogical.

## [0.1.2] - 2026-04-05

Python 3.10 compatibility patch.

### Fixed

- Replaced the remaining `tomllib` usage in tests with `toml`, matching the package runtime and avoiding CI/import failures on Python 3.10.

## [0.1.1] - 2026-04-05

First stabilization patch after the initial public release.

### Added

- Package `__version__` export.
- Minimal GitHub Actions CI covering tests, builds, and an installed example-launcher smoke test.

### Changed

- Example runner tests now verify the exposed package version.
- Example apps were manually smoke-tested after installation and in-repo.

## [0.1.0] - 2026-04-05

Initial public release.

### Added

- React-style `Component` model for Streamlit with local state preserved across reruns.
- `Ref` handles plus helper-based access through `get_element_value(...)`, `get_component_state(...)`, and `refresh_element(...)`.
- Shared state support through `App.create_shared_state(...)` and `get_shared_state(...)`.
- Functional components through `@component` and `use_state(...)`.
- Theme and config support on `App`, including runtime theme editing through `ThemeEditor`, `ThemeEditorDialog`, and `ThemeEditorButton`.
- Flow built-ins: `Conditional`, `KeepAlive`, `Case`, `Switch`, `Match`, and `Default`.
- Multipage built-ins: `Router` and `Page`.
- Packaged example launcher via `python -m st_components.examples <name>`.

### Changed

- Standardized callback payloads: if an event carries a useful value, that value is injected into the handler.
- Aligned wrapped element signatures with Streamlit 1.56.0 while keeping `key` and optional `ref` in the framework layer.
- Reorganized `st_components.elements` into subpackages with shared helper/type modules for readability.
- Simplified the public API surface:
  - `st_components` exposes the core primitives
  - `st_components.elements` exposes Streamlit element wrappers
  - `st_components.builtins` exposes higher-level built-ins
- Reworked examples and README for onboarding, with inline source expanders in the example apps.

### Notes

- This is the first tagged release of the project.
