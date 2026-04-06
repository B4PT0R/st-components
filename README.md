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

Run it like a normal Streamlit app:

```bash
streamlit run app.py
```

The library does not replace Streamlit's execution model. It adds a component layer on top of the usual rerun-based script execution.

## Why This Exists

Plain Streamlit is fast to start with, but larger apps often drift toward:

- flattened global `st.session_state`
- implicit UI structure based on script order
- reusable blocks that are hard to make truly stateful
- callbacks that require too much plumbing

`st-components` gives you a more explicit structure:

- Components own their layout and local state
- Elements render as single Streamlit primitives
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

The creation syntax is intentionally two-step:

```python
MyComponent(**props)(
    *children
)
```

First, `__init__(...)` receives props. Then `__call__(...)` receives children (this step can be ommitted if you don't want to pass any children). This is convenience sugar so tree construction feels close to JSX in plain Python.

children can still be passed as a prop if necessary and naturally live in `props.children`, so these two forms are equivalent:

```python
MyComponent(key="intro")("Hello")
MyComponent(key="intro", children=["Hello"])
```

In practice, the two-step style is the usual one because it makes nested UI trees much easier to read.

## Mental Model

### `Component`

A `Component` is a stateful unit.

- It has persistent local state.
- Its `render()` method returns Components, Elements, or renderable values (anything supported by `st.write`).
- A new Python instance is created on each rerun, but its state is restored from a fiber stored in `st.session_state`.

### `Element`

An `Element` is a render primitive.

- It renders into a corresponding Streamlit widget
- Its `render()` method returns None (the actual value of the widget lives in `st.session_state`, accessible by element path or ref).
- You can't declare a state on it.
- Stateful behavior should generally be built by composing Elements inside Components.


### Render Contract

The framework treats `Component` and `Element` renders differently:

- `Component.render()` composes the tree. It may return Components, Elements, tuples, or plain renderable values.
- `Element.render()` performs Streamlit rendering work in place and return nothing. These are terminal rendering leaves.

In practice:

- use the `render()` of Components to compose UI
- use Elements as atomic building blocks
- a widget's current value lives in the element value channel
- a runtime object such as a placeholder or handle returned by the element will also live in that same channel
- both are then reached uniformly through callback context, explicit path, or `Ref` via `get_element_value`

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

### Pattern 2: Callbacks

Widgets already store their value in `st.session_state`. `st-components` keeps using that storage, but exposes the current logical element value through a separate framework-level access path.

Callback payloads follow a simple rule:

- if an event carries a useful value, that value is injected into the handler
- otherwise the handler is called with no extra argument

In practice this means:

- `on_change(value)` for stateful widgets
- `on_submit(value)` for `chat_input`
- `on_select(value)` for selection-capable charts and dataframes
- `on_click()` for plain buttons

For example, a normal `on_change` handler receives the current widget value as `value`:

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
            on_change=self.set_name,
        )("Name")
```

There is no separate `args` / `kwargs` callback plumbing layer on top of this. If a handler needs more context than the triggering payload, read it from component state, shared state, `Ref`s, `get_element_value(...)`, or `get_component_state(...)`.

If the callback does nothing except copy the current widget value into one state field, you do not need to keep a dedicated handler like:

```python
def set_name(self, value):
    self.state.name = value
```

Use `sync_state(...)` instead. It is just a convenience shortcut for that common pattern:

```python
text_input(
    key="name",
    value=self.state.name,
    on_change=self.sync_state("name"),
)("Name")
```

`get_element_value()` exists as the low-level primitive underneath this. You can use it when you need the current value of another element by path or ref.

Conceptually, this is the value channel for Elements:

- stateful widgets expose their current value there
- runtime-backed Elements may expose a handle there
- access stays the same either way

### Pattern 3: Use `Ref()` for logical reachability

Refs are path-based references to a given component or element in the tree. You attach one to a component or element when you want to access its state or value without having to provide its full path. They don't point to the component instance directly, only to its state or value.

```python
from st_components import App, Component, Ref, get_component_state, get_element_value
from st_components.elements import button, container, markdown, text_input


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
        self.name_ref = Ref()
        self.counter_ref = Ref()

    def capture(self):
        self.state.snapshot = (
            f"name={get_element_value(self.name_ref, default='')}, "
            f"count={get_component_state(self.counter_ref).count}"
        )

    def render(self):
        return container(key="demo", border=True)(
            text_input(key="name", ref=self.name_ref)("Name"),
            Counter(key="counter", ref=self.counter_ref),
            button(key="capture", on_click=self.capture)("Read refs"),
            markdown(key="snapshot")(self.state.snapshot or "Nothing captured yet."),
        )


App()(RefDemo(key="refs")).render()
```

## Core API

### `App`

`App` is the root entry point and deals with rendering the whole app:

```python
from st_components import App, Component

class MyRoot(Component):

    def render(self):
        return "Hello World!"

app = App()(
    MyRoot(key="root")
)
app.render()
```

It also owns the render cycle logic:

- tracks which component rendered in the current pass
- unmounts components (clear the fibers) that didn't render in the current cycle

You may pass additional props to `App` for theming and configuration:

```python
from st_components import App, Theme, get_app

app = App(theme=Theme(textColor="black"))(
    MyRoot(key="root")
)
app.render()
```

`App` creates a singleton instance and should usually be initialized only once in a project. If you need the current instance elsewhere, call `get_app()`.

Constructor:

```python
App(
    root=None,
    *,
    page_title=None,
    page_icon=None,
    layout=None,
    initial_sidebar_state=None,
    menu_items=None,
    theme=None,
    css=None,
    config=None,
    persist_theme=True,
    persist_config=True,
)
```

Accepted constructor props:

- `root`: optional root node. Usually a `Component`, `Element`, or router root. You can also provide it later with `App()(MyRoot(key="root"))`.
- `page_title`: forwarded to `st.set_page_config(page_title=...)`.
- `page_icon`: forwarded to `st.set_page_config(page_icon=...)`.
- `layout`: forwarded to `st.set_page_config(layout=...)`, typically `"centered"` or `"wide"`.
- `initial_sidebar_state`: forwarded to `st.set_page_config(initial_sidebar_state=...)`.
- `menu_items`: forwarded to `st.set_page_config(menu_items=...)`.
- `theme`: app theme. Accepts either a plain dict or a typed `Theme`.
- `css`: extra CSS injected at render time. Accepts raw CSS text, a `Path`, a path string ending in `.css`, or a list mixing those forms.
- `config`: selected Streamlit config values. Accepts either a plain dict or a typed `Config`.
- `persist_theme`: if `True`, writes the current theme into `.streamlit/config.toml` during render.
- `persist_config`: if `True`, writes the current config into `.streamlit/config.toml` during render.

In practice:

- use page-config props (`page_title`, `layout`, ...) when you would normally call `st.set_page_config(...)`
- use `theme` for Streamlit theme tokens
- use `css` for custom styling not covered by the theme
- use `config` for the supported `client`, `runner`, `browser`, and `server` sections

Useful methods:

- `App()(root)`: attach the single root node after construction. Equivalent to passing `root=...` to the constructor.
- `.render()`: render the app.
- `.create_shared_state(name, instance)`: declare a shared state namespace for the app, then return the app for chaining.
- `.set_theme(theme)`: update the current theme in memory and in session state. Accepts a dict, a `Theme`, or `None`.
- `.save_theme(theme=None)`: optionally set a theme, then persist it to `.streamlit/config.toml`.
- `.set_css(css)`: update the current CSS in memory and in session state.
- `.set_config(config)`: update the current Streamlit config in memory and in session state. Accepts a dict, a `Config`, or `None`.
- `.save_config(config=None)`: optionally set a config, then persist it to `.streamlit/config.toml`.
- `.render_page(root)`: render a page root through the current app instance. This is mainly useful from file-backed multipage sources via `get_app().render_page(...)`.
- `get_app()`: return the current app instance from anywhere in the render tree.

## Elements

`Elements` are the thin wrapper layer over Streamlit primitives. They are the leaves of the tree: they render widgets, text, charts, containers, and runtime-backed handles, but they do not own local component state.

Import Streamlit wrappers from `st_components.elements`:

```python
from st_components.elements import (
    button, checkbox, slider, text_input,
    container, columns, tabs, expander,
    markdown, metric, json,
)
```

Coverage is internally organized by sub-packages:

- `text`
- `input`
- `layout`
- `display`
- `charts`
- `media`
- `feedback`

The wrappers stay close to Streamlit signatures, with two framework-specific additions:

- `key` is always required so the framework can derive a stable logical path
- `ref` is optional and gives you path-based access later through `get_element_value(...)`

Use an `Element` when you want a direct wrapper around one Streamlit primitive. Use a `Component` when you want to combine multiple elements, keep local state, or encapsulate behavior.

### `Component`

Subclass `Component` when you need a reusable, stateful unit with its own render logic. `render()` is where you compose child components, elements, tuples, or plain renderable values.

Useful members:

- `self.props`
- `self.children`
- `self.state`
- `self.set_state(...)`
- `component_did_mount()`
- `component_did_unmount()`
- `component_did_update(prev_state)`

The common pattern is:

- initialize local state in `__init__`
- update it from event handlers
- return the UI tree from `render()`

### `State`

State is local, persistent per mounted component path, and restored automatically across reruns.

You can initialize state directly in `__init__`:

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

Typed state gives you defaults, validation, and a visible schema. It is worth introducing once a component's state shape stabilizes or when you want stronger guarantees than an ad hoc dict.

### `Props`

Props work the same way: you can stay dynamic, or declare a typed nested `Props` subclass once the interface of a component becomes important enough to formalize.

You can declare typed props with a nested `Props` subclass:

```python
from modict import modict
from st_components import Component, Props
from st_components.elements import markdown


class Badge(Component):

    class BadgeProps(Props):
        _config = Props.config(extra="forbid")
        label: str = "badge"
        color: str = "blue"

    def render(self):
        return markdown(key="body")(f":{self.props.color}[**{self.props.label}**]")
```

This is useful when you want defaults, validation, or stricter control over accepted inputs.

### `@component`

Use `@component` to turn functions into components. The function behaves as the render method and should accept a `props` parameter.

```python
from st_components import App, component
from st_components.elements import container, markdown


@component
def Callout(props):
    return container(key="box", border=True)(
        markdown(key="body")(f"**{props.title}**\n\n{props.children[0]}")
    )
```

When calling the component, you still pass individual props and children normally rather than a props dict. The decorator wraps them into the framework `Props` object for you.

```python
app = App()(
    Callout(key="intro", title="Heads up")(
        "This is a functional component"
    )
)
app.render()
```

### `use_state`

You can also give local state to functional components through `use_state()`. This is the functional equivalent of `self.state` on class components:

```python
from st_components import component, use_state
from st_components.elements import button, markdown


@component
def Counter(props):
    state = use_state(count=0)

    def increment():
        state.count += 1

    return (
        markdown(key="value")(f"Count: **{state.count}**"),
        button(key="inc", on_click=increment)("Increment"),
    )
```

Or pass a typed `State` instance:

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

### `get_element_value(path_or_ref=None, default=None)`

Returns the current value of a given rendered Element.

- inside the current element's `render()` or its callbacks, `path_or_ref` may be omitted, defaulting to the caller element
- elsewhere, pass the element path or an element `Ref` explicitly

Examples:

- widget value: `get_element_value("app.form.name")`
- current callback caller: `get_element_value()`
- via a ref: `get_element_value(ref)` or `ref.value()`

### `get_component_state(path_or_ref)`

`get_component_state` works similarly for mounted Components and returns their current local state object.

Examples:

- component state by path: `get_component_state("app.form.counter")`
- current render or callback caller: `get_component_state()`
- via a ref: `get_component_state(ref)` or `ref.state()`

### `reset_element(path_or_ref)`

Forces a stateful Element to be recreated on the next rerun, so its declared default value is applied again.

```python
reset_element(name_ref)
```

## Theming and Config

Use `theme=...`, `css=...`, and `config=...` on `App(...)` to control the visual shell of the app.

- `theme` covers Streamlit's theme tokens
- `css` covers custom styling outside those tokens
- `config` covers the supported Streamlit config sections exposed by the library

Use a `Theme` passed to `App` to control Streamlit theming (a plain dict also works):

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


app = App()(
    Home(key="home")
)
app.render()
```

This is useful during development when you want to find a good theme quickly, then later replace it with a fixed theme in `App(theme=...)` or `config.toml` once the design is settled.

Notes:

- `Theme` fields map to official Streamlit theme config keys
- theme persistence goes through `.streamlit/config.toml`
- live theme change is best-effort; some changes will require a complete rerun.
- the persisted config in `.streamlit/config.toml` is the default source of truth
- CSS is injected after theme application, so CSS can intentionally override theme-driven styles

To see this live:

```bash
python -m st_components.examples theme_editor
```

## Built-ins

`st_components.builtins` contains higher-level structural helpers built on top of the core component model.

Import them from `st_components.builtins`:

```python
from st_components.builtins import (
    Conditional, Case, Switch, Match, Default,
    KeepAlive, ThemeEditorButton, ThemeEditorDialog, Router, Page,
)
```

Current built-ins include:

- flow helpers: `Conditional`, `Case`, `Switch`, `Match`, `Default`, `KeepAlive`
- multipage app helpers: `Router`, `Page`
- theme tooling: `ThemeEditor`, `ThemeEditorButton`, `ThemeEditorDialog`



## Examples

The repository includes several runnable examples. They are the fastest way to see the library's patterns in context:

- `python -m st_components.examples basic`
- `python -m st_components.examples dashboard`
- `python -m st_components.examples functional`
- `python -m st_components.examples flow`
- `python -m st_components.examples multipage`
- `python -m st_components.examples theme_editor`
- `python -m st_components.examples primitives`

What they are good for:

- `basic`: smallest class-component examples
- `primitives`: broad survey of available elements
- `dashboard`: larger composed UI with more realistic structure
- `functional`: `@component` and `use_state()` patterns
- `flow`: structural built-ins such as switching and conditional rendering
- `multipage`: router, pages, file-backed pages, and shared state
- `theme_editor`: live theme tuning workflow

You can also run example files directly from the repository with `streamlit run examples/<name>.py` when that is more convenient.

If you want the fastest onboarding path, start with:

1. `python -m st_components.examples basic`
2. `python -m st_components.examples primitives`
3. `python -m st_components.examples dashboard`
4. `python -m st_components.examples functional`
5. `python -m st_components.examples theme_editor`

## Usage Guidelines

### Keep keys local and boring

Keys identify siblings inside one branch, not global entities across the whole app.

Good:

- `key="name"`
- `key="filters"`
- `key="save"`

Bad:

- globally namespaced keys everywhere
- encoded hierarchy inside user keys

### Do not persist local state manually in `st.session_state`

The framework already does that for you. Reach local component state with `self.state` or `get_component_state(...)`, and reach element values with `get_element_value(...)`.

If you need custom state shared across several components, declare it once with `app.create_shared_state("my_custom_state", State())` and consume it with `get_shared_state("my_custom_state")`.

### Think in paths/refs, not instances

Because every rerun recreates the tree, the stable identity of a component is its location in the tree materialized as a resolved path, or a `Ref` pointing to it, not the Python object from a previous run.

This is why cross-component coordination should usually use:

- local state for behavior internal to one component
- shared state for app-level coordination
- refs only when you need path-based reachability to a specific mounted node

## Non-Goals

`st-components` is not trying to provide:

- a virtual DOM
- exact JSX syntax
- imperative control over live UI instances
- a replacement for Streamlit's execution model

It is a structuring layer over Streamlit, not a different frontend runtime.

## License

MIT
