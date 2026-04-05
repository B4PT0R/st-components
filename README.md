# st-components

React-inspired stateful components for [Streamlit](https://streamlit.io), in pure Python.

`st-components` adds a small component model on top of Streamlit:

- `Component` for reusable, stateful UI units
- `Element` for thin wrappers around Streamlit primitives
- `App` for render-cycle orchestration, shared theme/config, and root rendering

It keeps Streamlit's rerun model, but gives larger apps a clearer tree structure, local state, and more composable UI.

## Table of Contents

- [Installation](#installation)
- [Why This Exists](#why-this-exists)
- [Quick Start](#quick-start)
- [Mental Model](#mental-model)
- [Onboarding Path](#onboarding-path)
- [Core API](#core-api)
- [Theming and Config](#theming-and-config)
- [Elements](#elements)
- [Built-ins](#built-ins)
- [Examples](#examples)
- [Usage Guidelines](#usage-guidelines)
- [Non-Goals](#non-goals)
- [License](#license)

## Installation

```bash
pip install st-components
```

`st-components` builds on [modict](https://github.com/B4PT0R/modict) for its data models. `State`, `Props`, fibers, `Theme`, and `Config` are all modict-based, so they support both attribute access and dict-style access.

## Why This Exists

Plain Streamlit is fast to start with, but larger apps often drift toward:

- flattened global `st.session_state`
- implicit UI structure based on script order
- reusable blocks that are hard to make truly stateful
- callbacks that require too much plumbing

`st-components` gives you a more explicit structure:

- Components own local state
- Elements wrap Streamlit primitives
- keys stay short and local
- the framework derives full tree paths automatically

## Quick Start

```python
from st_components import App, Component
from st_components.elements import button, container


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=0)

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="inc", on_click=self.increment)(
            f"Clicked {self.state.count} times"
        )


app = App()(
    container(key="app")(
        Counter(key="a"),
        Counter(key="b"),
    )
)

app.render()
```

Each `Counter` keeps its own state across reruns.

## Mental Model

### `Component`

A `Component` is a stateful unit.

- It has persistent local state.
- Its `render()` method returns Components, Elements, or plain values.
- A new Python instance is created on each rerun, but its state is restored from a fiber stored in `st.session_state`.

### `Element`

An `Element` is a render primitive.

- It usually wraps one Streamlit primitive.
- It does not own persistent local component state.
- Stateful behavior should generally be built by composing Elements inside Components.

### Keys

Every Component and Element must have a `key`.

Keys are intentionally local:

- they only need to be unique among siblings
- they are not global ids
- the framework computes the full path automatically from the render context

This means two nodes can both use `key="counter"` safely if they live in different branches.

## Onboarding Path

If you're new to the library, this is the shortest useful path:

1. Start with `App`, `Component`, and a few `elements`.
2. Use `self.state` inside components for local UI state.
3. `on_change` handlers receive the current widget value as `value`.
4. Use `Ref()` only when you need path-based reachability later.
5. Add typed `State` and `Props` models once the shape stabilizes.

### Pattern 1: Keep local state in Components

```python
from st_components import Component
from st_components.elements import button, container, markdown


class Panel(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(open=False)

    def toggle(self):
        self.state.open = not self.state.open

    def render(self):
        return container(key="panel", border=True)(
            button(key="toggle", on_click=self.toggle)(
                "Hide details" if self.state.open else "Show details"
            ),
            markdown(key="body")(
                "Local component state controls this panel."
                if self.state.open
                else "Click the button to reveal more content."
            ),
        )
```

This is the preferred place for view state, local mode, and coordination between widgets.

### Pattern 2: `on_change` handlers receive `value`

Widgets already store their value in `st.session_state`. `st-components` keeps using that storage instead of duplicating it.

For ordinary `on_change` handlers, the current widget value is passed to your callback as `value`:

```python
from st_components import Component
from st_components.elements import text_input


class NameForm(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(name="")

    def sync_name(self, value):
        self.state.name = value

    def render(self):
        return text_input(
            key="name",
            value=self.state.name,
            on_change=self.sync_name,
        )("Name")
```

If the callback does nothing except copy the current widget value into one state field, you do not need to write a separate handler like:

```python
def sync_name(self, value):
    self.state.name = value
```

Use `sync_state(...)` instead. It reduces this kind of boilerplate by generating that simple sync callback for you:

```python
text_input(
    key="name",
    value=self.state.name,
    on_change=self.sync_state("name"),
)("Name")
```

More generally, callback payloads follow a simple rule:

- if an event carries a useful value, that value is injected into the handler
- otherwise the handler is called with no extra argument

In practice this means:

- `on_change(value)` for stateful widgets
- `on_submit(value)` for `chat_input`
- `on_select(value)` for selection-capable charts and dataframes
- `on_click()` for plain buttons

`get_element_value()` still exists as the low-level primitive underneath this. Inside a widget callback, it resolves to the Element that triggered that callback through the callback context, so you can still use it when you need the current value indirectly or want to read another element by path.

### Pattern 3: Use `Ref()` for logical reachability

Refs are path-based handles, not live object refs. In practice, you will usually pass them to helpers instead of calling methods on the ref directly.

```python
from st_components import App, Component, Ref, get_component_state, get_element_value
from st_components.elements import button, container, markdown, text_input


name_ref = Ref()
counter_ref = Ref()


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=0)

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="inc", on_click=self.increment)(
            f"Count: {self.state.count}"
        )


class RefDemo(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(snapshot="")

    def capture(self):
        self.state.snapshot = (
            f"name={get_element_value(name_ref, default='')}, "
            f"count={get_component_state(counter_ref).count}"
        )

    def render(self):
        return container(key="demo", border=True)(
            text_input(key="name", ref=name_ref)("Name"),
            Counter(key="counter", ref=counter_ref),
            button(key="capture", on_click=self.capture)("Read refs"),
            markdown(key="snapshot")(self.state.snapshot or "Nothing captured yet."),
        )


App()(RefDemo(key="refs")).render()
```

## Core API

### `App`

`App` is the root entry point:

```python
App()(MyRoot(key="root")).render()
```

It also owns the render cycle:

- tracks which component fibers rendered in the current pass
- unmounts fibers that disappeared from the tree
- calls `component_did_unmount()` for stale components

### `Component`

Subclass `Component` and implement `render()`.

Useful members:

- `self.props`
- `self.children`
- `self.state`
- `self.set_state(...)`
- `component_did_mount()`
- `component_did_unmount()`
- `component_did_update(prev_state)`

### `State`

You can initialize state in `__init__`:

```python
self.state = dict(count=0)
```

Or declare a typed nested subclass:

```python
from st_components import Component, State
from st_components.elements import button, container, metric


class Counter(Component):

    class CounterState(State):
        count: int = 0
        label: str = "clicks"

    def increment(self):
        self.state.count += 1

    def render(self):
        return container(key="panel", border=True)(
            metric(key="metric", label=self.state.label, value=self.state.count),
            button(key="inc", on_click=self.increment)("Increment"),
        )
```

Typed state gives you defaults, validation, and a visible schema.

### `Props`

You can also declare typed props with a nested `Props` subclass:

```python
from modict import modict
from st_components import Component, Props
from st_components.elements import markdown


class Badge(Component):

    class BadgeProps(Props):
        _config = modict.config(extra="forbid")
        label: str = "badge"
        color: str = "blue"

    def render(self):
        return markdown(key="body")(f":{self.props.color}[**{self.props.label}**]")
```

### `@component`

Use `@component` for simple functional components:

```python
from st_components import App, component
from st_components.elements import container, markdown


@component
def Callout(props):
    return container(key="box", border=True)(
        markdown(key="body")(f"**{props.title}**\n\n{props.children[0]}")
    )


App()(Callout(key="intro", title="Heads up")("This is a functional component.")).render()
```

It can also use local state through `use_state()`:

```python
from st_components import component, use_state
from st_components.elements import button, markdown


@component
def Counter(props):
    state = use_state(count=props.initial)

    def increment():
        state.count += 1

    return (
        markdown(key="value")(f"Count: **{state.count}**"),
        button(key="inc", on_click=increment)("Increment"),
    )
```

### `use_state(other=None, /, **kwargs)`

Minimal state hook for functional components.

```python
@component
def Counter(props):
    state = use_state(count=0)
```

You can also pass a typed `State` instance:

```python
from st_components import State, component, use_state
from st_components.elements import button, markdown


class CounterState(State):
    count: int = 0
    step: int = 1


@component
def Counter(props):
    state = use_state(CounterState(count=0, step=2))

    def increment():
        state.count += state.step

    return (
        markdown(key="value")(f"Count: **{state.count}**"),
        button(key="inc", on_click=increment)(f"+ {state.step}"),
    )
```

### `get_element_value(path=None, default=None)`

Returns the current value of a stateful Element.

- inside the current element or its callback, `path` may be omitted
- elsewhere, pass the element path or an Element `Ref`

```python
get_element_value("app.form.name")
get_element_value(name_ref)
```

### `get_component_state(path_or_ref)`

Returns the current local state of a mounted Component.

```python
get_component_state("app.counter")
get_component_state(counter_ref)
```

### `refresh_element(path_or_ref)`

Forces a stateful Element to be recreated on the next rerun, so its declared default value is applied again.

```python
refresh_element(name_ref)
```

### `Ref`

Logical handle to a rendered Component or Element path.

Typical use:

- keep a `Ref()` instance on the component
- attach it to an Element or Component with `ref=...`
- later pass it to `get_element_value(ref)`, `get_component_state(ref)`, or `refresh_element(ref)`

Available members:

- `ref.path`
- `ref.value(default=None)` for Element refs
- `ref.state()` for Component refs

The methods stay available, but the preferred style is usually to pass refs to helpers.

### `Element`

Subclass `Element` when you want to wrap a Streamlit primitive directly.

Elements should stay thin. If behavior becomes stateful or orchestration-heavy, move it into a `Component`.

## Theming and Config

`App` exposes official Streamlit theming and selected config options.

```python
from st_components import App, Theme


app = App(
    theme=Theme(
        base="dark",
        primaryColor="#2dd4bf",
        backgroundColor="#0f172a",
        textColor="#e2e8f0",
        sidebar={"backgroundColor": "#111827"},
    ),
)(
    MyRoot(key="root"),
)
```

You can also use the built-in `ThemeEditorButton` to tune a theme visually while building your app:

```python
from st_components import App, Component
from st_components.builtins import ThemeEditorButton
from st_components.elements import container, markdown


class Home(Component):

    def render(self):
        return container(key="page")(
            container(key="hero", border=True)(
                markdown(key="title")("# Hello"),
                markdown(key="body")("Use the built-in theme editor to tune the app live."),
                ThemeEditorButton(key="open", type="primary", title="Theme editor")(),
            )
        )


App()(Home(key="home")).render()
```

This is useful during development when you want to find a good theme quickly, then later replace it with a fixed `Theme(...)` in `App(...)` once the design is settled. If you want the lower-level primitive, `ThemeEditorDialog` is still available too.

Relevant entry points:

- `theme=...` accepts a plain dict or typed `Theme`
- `css=...` accepts raw CSS, a `.css` path, or a list mixing both
- `config=...` accepts selected runtime-relevant `config.toml` options
- `get_app()` returns the current app instance, so you can call `get_app().set_theme(...)`, `set_css(...)`, `save_theme()`, and related helpers during a rerun

Notes:

- `Theme` fields map to Streamlit theme config keys
- theme persistence goes through `.streamlit/config.toml`
- runtime application is best-effort; persisted config is the stable source of truth
- CSS is injected after theme application, so CSS can intentionally override theme-driven styles

To see this live:

```bash
python -m st_components.examples theme_editor
```

## Elements

Import Streamlit wrappers from `st_components.elements`:

```python
from st_components.elements import (
    button, checkbox, slider, text_input,
    container, columns, tabs, expander,
    markdown, metric, json,
)
```

Coverage is organized by package:

- `text`
- `input`
- `layout`
- `display`
- `charts`
- `media`
- `feedback`

The wrappers stay aligned with Streamlit signatures, with framework-specific `key` and optional `ref`.

## Built-ins

Import higher-level structural components from `st_components.builtins`:

```python
from st_components.builtins import (
    Conditional, Case, Switch, Match, Default,
    KeepAlive, ThemeEditorButton, ThemeEditorDialog, Router, Page,
)
```

Current built-ins include:

- flow helpers: `Conditional`, `Case`, `Switch`, `Match`, `Default`, `KeepAlive`
- app helpers: `Router`, `Page`
- theme tooling: `ThemeEditor`, `ThemeEditorButton`, `ThemeEditorDialog`

## Examples

Useful examples:

- `python -m st_components.examples dashboard`
- `python -m st_components.examples functional`
- `python -m st_components.examples flow`
- `python -m st_components.examples theme_editor`
- `python -m st_components.examples primitives`

You can also still run example files directly from the repository with `streamlit run examples/<name>.py`.

If you want the fastest onboarding path, start with:

1. `python -m st_components.examples dashboard`
2. `python -m st_components.examples functional`
3. `python -m st_components.examples theme_editor`

## Usage Guidelines

### Prefer Components for behavior

If something has local state, coordinates several widgets, or behaves like a reusable UI block, it should usually be a `Component`.

### Prefer Elements for thin wrappers

If something is just a direct Streamlit primitive with a compositional API, keep it as an `Element`.

### Keep keys local and boring

Good:

- `key="name"`
- `key="filters"`
- `key="save"`

Bad:

- globally namespaced keys everywhere
- encoded hierarchy inside user keys

### Do not duplicate widget state unless you need to

Widget values already live in `st.session_state`. Copy them into component state only when you want a component-level snapshot, derived state, or cross-widget coordination.

### Think in paths, not instances

Because reruns recreate the tree, the stable identity is the resolved path, not the Python object from a previous run.

## Non-Goals

`st-components` is not trying to provide:

- a virtual DOM
- JSX
- imperative control over live UI instances
- a replacement for Streamlit's execution model

It is a structuring layer over Streamlit, not a different frontend runtime.

## License

MIT
