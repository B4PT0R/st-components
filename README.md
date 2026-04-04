# st-components

React-inspired stateful components for [Streamlit](https://streamlit.io), in pure Python.

`st-components` does not try to fight Streamlit's rerun model. It accepts that the script reruns from top to bottom on every interaction, then adds a small component system on top:

- `Component` gives you local persistent state.
- `Element` wraps Streamlit primitives in a composable tree.
- widget values remain in `st.session_state`, where Streamlit already expects them.
- refs and path-based helpers let you reach parts of the tree without relying on fragile Python instances.

The result is a style that feels closer to React composition, but stays idiomatic to Streamlit.

## Status

This project is currently a small experimental library.

The goal is not to reproduce React completely. The goal is to make Streamlit apps easier to structure once they stop being "just a script".

## Installation

```bash
pip install st-components
```

## Why This Exists

Plain Streamlit is simple and productive, but larger apps often become awkward:

- state ends up flattened into global `st.session_state`
- UI structure is implicit in script order
- reusable widgets are hard to turn into real stateful units
- callbacks often need too much plumbing

`st-components` gives you a more explicit structure:

- Components own local state.
- Elements describe renderable primitives.
- keys stay short and local.
- the framework derives full tree paths automatically.

## Mental Model

There are only two core building blocks.

### `Component`

A `Component` is a stateful unit.

- It has persistent local state.
- Its `render()` method returns Elements, Components, or plain values.
- A new Python instance is created on each rerun, but its state is restored from a fiber stored in `st.session_state`.

### `Element`

An `Element` is a terminal render primitive.

- It usually wraps one Streamlit primitive.
- It does not own persistent local state.
- Rich behavior should be built by composing Elements inside Components.

### Keys

Every Component and Element must have a `key`.

Keys are deliberately simple:

- they only need to be unique among siblings
- they are not global ids
- the framework computes the full path automatically from the render context

This means two nodes can both use `key="counter"` safely if they live in different branches of the tree.

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


app = App(
    root=container(key="app")(
        Counter(key="counter_a"),
        Counter(key="counter_b"),
    )
)

app.render()
```

Each `Counter` keeps its own `count` across reruns.

## The Main Patterns

Most real usage falls into four patterns.

### 1. Keep local state in Components

Use `self.state` for state that conceptually belongs to a component.

```python
class Panel(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(open=False)

    def toggle(self):
        self.state.open = not self.state.open
```

This is the preferred place for:

- view state
- local UI mode
- derived workflow state
- state coordinated across several child widgets

### 2. Read widget values with `get_element_value()`

Stateful Streamlit widgets already store their value in `st.session_state`.

`st-components` keeps using that storage. It does not duplicate widget state into a second store.

Instead, stateful Elements expose their value by element path, and `get_element_value()` reads it.

```python
from st_components import Component, get_element_value
from st_components.elements import text_input


class NameForm(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(name="")

    def sync_name(self):
        self.state.name = get_element_value()

    def render(self):
        return text_input(
            key="name",
            value=self.state.name,
            on_change=self.sync_name,
        )("Name")
```

This is the intended pattern for widget callbacks:

1. a widget changes
2. Streamlit stores the widget value
3. the callback runs
4. `get_element_value()` reads the current value for that Element
5. the Component updates its own state if needed

### 3. Use `Ref()` for path-based reachability

Refs are supported, but they are not React-style object refs.

Because Streamlit reruns recreate all Python instances, a ref cannot safely point to a living object. In `st-components`, a ref stores a resolved logical path.

```python
from st_components import Ref
from st_components.elements import text_input


name_ref = Ref()

text_input(key="name", ref=name_ref)("Name")

name_ref.path
name_ref.value()
```

Refs are useful when you want to reach a node later without hardcoding its full path as a string.

For Components:

```python
counter_ref = Ref()

Counter(key="counter", ref=counter_ref)

counter_ref.state()
counter_ref.get("count")
```

Use refs for path-based lookup. Do not think of them as imperative handles to living instances.

### 4. Build rich behavior by composition

The library intentionally keeps base Elements small.

The intended design is:

- one Element wraps one Streamlit primitive
- layouts compose children
- stateful interactions live in Components

That keeps the model simple and predictable.

### 5. Use `@component` for simple stateless components

If a component does not need lifecycle hooks or explicit class syntax, you can define it as a function.

```python
from st_components import component
from st_components.elements import markdown


@component
def Callout(props):
    return markdown(key="body")(f"**{props.title}**\n\n{props.children[0]}")
```

This decorator turns the function into a component instantiator:

```python
Callout(key="intro", title="Heads up")("This is a functional component.")
```

Rules:

- the decorated function must use the shape `func(props)`
- `props` is a `modict`-style object with attribute access and helpers like `exclude()`
- the decorated function receives regular props plus `children`
- framework props like `key` and `ref` are not passed to the function
- under the hood, `@component` caches a generated `Component` subclass

You can also add local state inside a functional component with `use_state()`:

```python
from st_components import component, use_state


@component
def Counter(props):
    state = use_state(count=props.initial)

    def increment():
        state.count += 1
```

## API Overview

### `App`

Small entry point that renders a root Component or Element.

```python
App(root=MyRoot(key="root")).render()
```

`App` also owns the render cycle:

- it tracks which component fibers were rendered during the current pass
- it unmounts fibers that disappeared from the tree
- it calls `component_did_unmount()` for those stale components

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

State is stored in a fiber keyed by the Component's resolved tree path.

`component_did_update(prev_state)` is called after a render cycle when the Component was already mounted and its state changed since the previous cycle.

### `@component`

Decorator that turns a function `func(props)` into a component instantiator backed by a cached generated `Component` subclass.

```python
@component
def Badge(props):
    return markdown(key="body")(props.label)
```

The generated class is cached per function, and exposed on `Badge.component_class`.

### `use_state(**kwargs)`

Minimal state hook for functional components.

```python
@component
def Counter(props):
    state = use_state(count=0)
```

Behavior:

- on the first render, `kwargs` initialize the component state
- on later renders, the existing persisted state is returned
- later `kwargs` are ignored

`use_state()` must be called while rendering a Component.

### `Element`

Subclass `Element` when you want to wrap a Streamlit primitive directly.

An Element may:

- render Streamlit UI directly
- render its children
- return a simple value or handle when needed

But Elements should stay simple. If behavior starts becoming stateful or orchestration-heavy, move it into a Component.

### `render(obj)`

Renders:

- an `Element`
- a `Component`
- or any other object via `st.write()`

This is mainly useful when iterating over heterogeneous children.

### `KEY(key)`

`KEY()` is only meant for internal use inside `Element.render()`, when calling a raw Streamlit widget function with a `key=...`.

Example:

```python
class checkbox(Element):
    def render(self):
        return st.checkbox("Enabled", key=KEY("widget"))
```

You do not call `KEY()` when instantiating Components or Elements themselves.

### `get_element_value(path=None, default=None)`

Returns the current value of a stateful Element.

Rules:

- if called inside the current Element's `render()`, `path` may be omitted
- if called inside a widget callback, `path` may also be omitted
- if called elsewhere, pass the Element path explicitly

```python
get_element_value("app.form.name")
```

Convention:

- stateful widget Elements use an internal widget key at `element_path + ".widget"`
- the public API stays based on the Element path, not the internal widget key

This keeps the API stable even if the internal Streamlit primitive changes.

### `Ref`

Logical handle to a rendered Component or Element path.

Available members:

- `ref.path`
- `ref.value(default=None)` for Element refs
- `ref.state()` for Component refs
- `ref.get(key, default=None)` as a shortcut to component state fields

Important:

- a `Ref` does not point to a live Python instance
- a `Ref` becomes usable only after the tree has rendered

### `fibers()`

Returns the raw component fiber store in `st.session_state`.

This is mostly a debugging tool.

## Built-in Elements

The package currently provides wrappers for common Streamlit primitives.

```python
from st_components.elements import (
    button, checkbox, slider, text_input, text_area,
    container, columns, tabs, expander, sidebar,
    markdown, metric, json,
)
```

Broad categories:

- text: `title`, `header`, `subheader`, `caption`, `text`, `markdown`, `code`, `latex`, `divider`
- input: `button`, `checkbox`, `toggle`, `radio`, `selectbox`, `multiselect`, `slider`, `text_input`, `text_area`, and others
- layout: `container`, `columns`, `tabs`, `expander`, `popover`, `sidebar`, `empty`
- display: `write`, `dataframe`, `table`, `metric`, `json`
- media: `image`, `audio`, `video`
- feedback: `success`, `info`, `warning`, `error`, `toast`, `progress`, `spinner`, `balloons`, `snow`

## Recommended Usage Rules

If you want code that stays readable, these are the rules to follow.

### Prefer Components for behavior

If something:

- has local state
- coordinates several widgets
- needs callbacks plus derived state
- behaves like a reusable UI block

it should probably be a `Component`.

### Prefer Elements for thin wrappers

If something is just a direct Streamlit primitive with a cleaner compositional API, keep it as an `Element`.

### Keep keys local and boring

Good:

- `key="name"`
- `key="filters"`
- `key="save"`

Bad:

- globally namespaced keys everywhere
- encoded hierarchy inside the user key

Let the framework derive the full path.

### Do not duplicate widget state unless you need to

Widget values already live in `st.session_state`.

Only copy them into `self.state` when:

- you want a component-level snapshot
- you want derived state
- you want to coordinate multiple widgets together

### Think in paths, not instances

This is especially important for refs.

Because reruns recreate the tree, the stable identity is the resolved path, not the Python object you saw during a previous run.

## Tutorial Demo

The repository includes a richer tutorial dashboard:

```bash
streamlit run examples/dashboard.py
```

It walks through:

- local component state
- `get_element_value()`
- `Ref()`
- composition patterns

If you want to understand the library quickly, start there.

There is also a smaller dedicated example for functional components:

```bash
streamlit run examples/functional.py
```

## Non-Goals

`st-components` is not trying to provide:

- a virtual DOM
- hooks
- a JSX syntax
- imperative control of live UI instances
- a replacement for Streamlit's execution model

It is a small structuring layer over Streamlit, not a different frontend runtime.

## License

MIT
