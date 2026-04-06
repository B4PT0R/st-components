# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses SemVer.

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
- Shared state support through `App.shared_state(...)` and `get_shared_state(...)`.
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
