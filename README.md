# st-components

React-inspired stateful components for [Streamlit](https://streamlit.io), in pure Python.

`st-components` adds a small component model on top of Streamlit:

- `Component` for reusable, stateful UI units
- `Element` for thin wrappers around Streamlit primitives
- `App` for render-cycle orchestration, shared theme/config, and app-level rendering

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
    container(key="home")(
        Counter(key="counter_1"),
        Counter(key="counter_2"),
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

Any Component tree must recursively resolve into a tree of pure Elements

### Render Contract

The framework treats `Component` and `Element` renders differently:

- `Component.render()` composes the tree. It may return Components, Elements, tuples, or plain renderable values.
- `Element.render()` performs Streamlit rendering work in place and return nothing. These are terminal rendering leaves.

In practice:

- use the `render()` of Components to compose UI
- use Elements as atomic building blocks
- an element's output value lives in the element value channel
- this value can be accessed by callback context, explicit path, or `Ref` via `get_element_value`

### Keys

Every Component and Element must have a `key`.

Keys are intentionally local:

- they only need to be unique among siblings
- they are not global ids
- the framework computes the full path automatically from the render context

This means two nodes can both use `key="counter"` safely if they live in different branches.

In the final tree, paths are derived structurally from real component keys. For example:

- a simple top-level branch might render under `app.home.panel.toggle`
- a multipage branch might render under `app.router.report.page.note`
- a provided subtree might render under `app.theme_scope.toolbar`

## Onboarding Path

If you're new to the library, this is the shortest useful path:

1. Start with `App`, `Component`, and a few `elements`.
2. Use `self.state` inside components for local UI state.
3. Pipe event handlers to deal with app logic.
4. Use `Ref()` only when you need path-based reachability later.
5. Add typed `State` and `Props` models once the shape stabilizes.

### Pattern 1: Declare a simple component with local state

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
            on_change=self.sync_name,
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

Refs are path-based references to a given component or element in the tree. You attach one to a component or element when you want to access its state or value without having to provide its full path. They don't point to the instance directly, only to its location in the tree, which is enough to retrieve its state from the fiber (or its value from `st.session_state` directly in case of an element).

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

class MyLayout(Component):

    def render(self):
        return "Hello World!"

app = App()(
    MyLayout(key="layout")
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
    MyLayout(key="layout")
)
app.render()
```

`App` creates a singleton instance and should usually be initialized only once in a project. If you need the current instance elsewhere, call `get_app()`.

`App` is also the structural root of the rendered tree. Its key is fixed to `app`, so every mounted path starts with `app...`.

Constructor:

```python
App(
    *,
    children=None,
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

- `children`: optional list containing a single renderable (Component, Element or value). In practice, `App()(MyLayout(key="layout"))` is the recommended style because it keeps props and tree structure clearly separated.
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
- `.render()`: render the app.
- `.create_shared_state(name, instance)`: declare a shared state namespace for the app, then return the app for chaining.
- `.set_theme(theme)`: update the current theme in memory and in session state. Accepts a dict, a `Theme`, or `None`.
- `.save_theme(theme=None)`: optionally set a theme, then persist it to `.streamlit/config.toml`.
- `.set_css(css)`: update the current CSS in memory and in session state.
- `.set_config(config)`: update the current Streamlit config in memory and in session state. Accepts a dict, a `Config`, or `None`.
- `.save_config(config=None)`: optionally set a config, then persist it to `.streamlit/config.toml`.
- `.render_page(page_tree)`: render a page tree through the current app instance. This is mainly useful from file-backed multipage sources via `get_app().render_page(...)`, and it preserves the active multipage path prefix such as `app.router.report...`.
- `get_app()`: return the current app instance from anywhere in the render tree.

For multipage apps, `Router` and `Page` are normal structural components too. The current page therefore lives in the same path system as the rest of the tree, for example `app.router.overview.page...` or `app.router.report.page...`.

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

### Hooks

Hooks are the general mechanism for storing and managing information on the mounted component fiber rather than on the transient Python instance recreated on each rerun.

This matters because component instances are not persistent across reruns, but fibers are. Hooks therefore give you a place to keep state, memoized values, technical refs, effects, and other render-adjacent data that must survive from one render cycle to the next.

Hooks are relevant for both functional components and class-based components:

- in functional components, they are the primary way to access persistent local state and render-cycle helpers
- in class components, they complement `self.state` when you need persistent technical data that should not live in ordinary instance attributes

Hooks are evaluated in call order during render, and their data persists on the mounted component fiber.

Available hooks:

- `use_state(...)`: local render state for functional components. This is the functional equivalent of `self.state`.
- `use_context(context)`: read a tree-scoped ambient value from the nearest matching provider.
- `use_memo(factory, deps=None)`: memoize a computed value between renders.
- `use_effect(effect, deps=None)`: run an effect after render, with optional cleanup support.
- `use_ref(initial=None)`: keep a mutable technical value across renders through `.current`.
- `use_callback(callback, deps=None)`: memoize a callback identity. This is a small convenience wrapper over `use_memo(...)`.
- `use_previous(value, initial=None)`: read the value from the previous render.
- `use_id()`: get a stable id for the current hook slot in the mounted component.

#### `use_state`

Use `use_state()` when a functional component needs local render state:

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

#### `use_context`

Use `create_context(initial_context_data)` to define a typed tree-scoped ambient value, wrap a subtree with `MyContext.Provider(...)`, then read it from any descendant with `use_context(MyContext)`.

This is useful when a value should be shared across a branch without being threaded manually through several layers of props.

Unlike `shared_state`, context is scoped by tree position rather than by global namespace. Two different branches can therefore provide different values for the same context at the same time.

Contexts are typed through `ContextData`. The initial context object is the default value returned by `use_context(...)` when no provider is present, and later providers replace the current context for their subtree with a new instance of the same schema.

You can pass either:

- a `ContextData` instance, if you want a custom typed subclass
- or a plain `dict`, which is automatically cast to the base `ContextData` class and then returned as such by `use_context(...)`

The same rule applies to `Provider(data=...)`: it accepts either a `ContextData` instance or a plain `dict`, normalizes it to the context's original schema class, and rejects anything else. The provider does not implicitly merge with the previous scoped value.

Resolution follows the rendered tree:

- if a matching provider exists above the current component, `use_context(...)` returns the value from the nearest one
- otherwise it returns the context default
- nested providers override outer ones naturally for their own subtree

```python
from st_components import ContextData, component, create_context, use_context


class ThemeData(ContextData):
    mode: str = "light"


ThemeContext = create_context(ThemeData(mode="light"))


@component
def Toolbar(props):
    theme = use_context(ThemeContext)
    return f"Theme: {theme.mode}"
```

```python
App()(
    ThemeContext.Provider(key="theme_scope", data={"mode": "dark"})(
        Toolbar(key="toolbar")
    )
).render()
```

The provider is a normal structural component, so its key also appears in paths such as `app.theme_scope.toolbar`.

#### `use_memo`

Use `use_memo(factory, deps)` to reuse a computed value until its dependencies change.

- `deps=None`: recompute on every render
- `deps=[]`: compute once per mounted component
- otherwise: recompute only when the deps tuple changes between renders

```python
from st_components import component, use_memo


@component
def Summary(props):
    total = use_memo(
        lambda: sum(props.values),
        deps=[tuple(props.values)],
    )
    return f"Total: {total}"
```

#### `use_effect`

Use `use_effect(effect, deps)` for post-render work.

- the effect runs after render
- if it returns a callable, that callable is used as cleanup
- cleanup runs before the effect reruns and when the component unmounts

```python
from st_components import component, use_effect


@component
def Logger(props):
    use_effect(
        lambda: print(f"value changed to {props.value}"),
        deps=[props.value],
    )
    return None
```

#### `use_ref`

Use `use_ref(initial)` for mutable technical state that should persist across renders without being part of the render state.

```python
from st_components import component, use_ref


@component
def PreviousTracker(props):
    previous = use_ref(None)
    seen = previous.current
    previous.current = props.value
    return f"Previous: {seen}"
```

#### `use_callback`

Use `use_callback(callback, deps)` when you want a stable callback identity between renders.

Conceptually:

```python
use_callback(fn, deps) == use_memo(lambda: fn, deps)
```

#### `use_previous`

Use `use_previous(value)` when you want the previous render's value directly.

```python
from st_components import component, use_previous


@component
def Delta(props):
    previous = use_previous(props.value)
    return f"Previous={previous}, Current={props.value}"
```

#### `use_id`

Use `use_id()` when you need a stable per-hook identifier for the mounted component.

Class components still have natural equivalents for some of these ideas:

- `use_state(...)` -> `self.state`
- `use_effect(...)` -> `component_did_mount()`, `component_did_update(prev_state)`, `component_did_unmount()`
- `use_ref(...)` -> a persistent technical cell on the fiber, which is usually safer than a plain instance attribute if the value must survive reruns
- `use_memo(...)` -> fiber-backed memoization, which is usually safer than instance-level caching if the value must survive reruns
- `use_callback(...)` -> a normal instance method
- `use_previous(...)` -> an instance attribute or `prev_state` inside `component_did_update(...)`
- `use_id()` -> a fiber-backed stable identifier

So the intended split is mostly:

- hooks for persistent render-cycle data
- `self.state` and lifecycle methods for the class-oriented API surface

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
    MyLayout(key="layout"),
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

`Router` and `Page` are structural components used by `App.render()` to compile Streamlit multipage navigation while still keeping normal component paths such as `app.router.report.page...`.



## Examples

The repository includes several runnable examples. They are the fastest way to see the library's patterns in context:

- `python -m st_components.examples basic`
- `python -m st_components.examples dashboard`
- `python -m st_components.examples functional`
- `python -m st_components.examples flow`
- `python -m st_components.examples hooks`
- `python -m st_components.examples multipage`
- `python -m st_components.examples theme_editor`
- `python -m st_components.examples primitives`

What they are good for:

- `basic`: smallest class-component examples
- `primitives`: broad survey of available elements
- `dashboard`: larger composed UI with more realistic structure
- `functional`: `@component` and `use_state()` patterns
- `hooks`: compact overview of the hook system in one screen
- `flow`: structural built-ins such as switching and conditional rendering
- `multipage`: router, pages, file-backed pages, shared state, and a lightweight provider above the router
- `theme_editor`: live theme tuning workflow

You can also run example files directly from the repository with `streamlit run examples/<name>.py` when that is more convenient.

If you want the fastest onboarding path, start with:

1. `python -m st_components.examples basic`
2. `python -m st_components.examples primitives`
3. `python -m st_components.examples dashboard`
4. `python -m st_components.examples functional`
5. `python -m st_components.examples hooks`
6. `python -m st_components.examples theme_editor`

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
- context for ambient values shared by one subtree
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
