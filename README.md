# st-components

`st-components` is a React-inspired component-based framework using [Streamlit](https://streamlit.io) as its render engine. 

Simply put, `st-components` adds a higher level component API on top of Streamlit.

It's still 100% Streamlit, same widgets, same runtime, same script-rerun pattern, but it changes the way you **think** about Streamlit components and **how** you will combine them to build an app.

Instead of thinking your components as **functions**,  rendering immediately when called, returning their last known value from the UI, and combined in imperative fashion to achieve a more complex app logic (which is the standard Streamlit mental model):

```python
import streamlit as st

def demo():
    st.header("Demo App")
    with st.container(key="pannel",border=True):
        name=st.text_input(key="name_input", label="Enter your name:", value="")
        if name:
            clicked = st.button(key="greet", label="Show greetings!")
            if clicked :    
                st.markdown(f"Hello {name}!")
                st.balloons()

def app():
    demo()

app()
```

In `st-components`, you think of components as nested **objects**, each with a **render** method returning the widgets it should show on screen, and who manage their **state** and logic internally via **events callbacks**. For those who already know React, it should sound quite familiar:

```python
from st_components import App, Component
from st_components.elements import header, container, text_input, button, markdown, balloons

class Demo(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state=dict(name=None, clicked=False)

    def on_change(self, value):
        self.state.name = value

    def on_click(self, _):
        self.state.clicked = True

    def render(self):
        try:
            return (
                header(key="h")("Demo App"),
                container(key="pannel",border=True)(
                    text_input(key="name_input", label="Enter your name:", value="", on_change=self.on_change),
                    button(key="greet", label="Show greetings!", on_click=self.on_click) if self.state.name else None,
                    markdown(key="m", body=f"Hello {self.state.name}!") if self.state.clicked else None,
                    balloons(key="b") if self.state.clicked else None
                )
            )
        finally:
            self.state.clicked = False

app=App()(
    Demo(key="demo")
)

app.render()
```

Admittedly, the second is a bit more declarative and verbose, so it's probably not that suitable for beginners. But it's much more powerful when it comes to turn components into stateful, reusable and composable building blocks, handling their own state and logic internally.

This short demo already shows the basic idea:
- The base `Component` class lets you declare custom reusable, stateful and reactive UI units by subclassing it.
- `Elements` like `header`, `container`, `text_input` etc. are ready-made thin wrappers around Streamlit primitives.
- `App` serves as the root entry point to render your components. It manages app-level states, render cycles, global config, theming, etc.  



## Table of Contents

- [Installation](#installation)
- [Why This Exists](#why-this-exists)
- [Quick Start](#quick-start)
- [Mental Model](#mental-model)
  - [Component](#component)
  - [Element](#element)
  - [Keys](#keys)
- [Onboarding Path](#onboarding-path)
  - [Pattern 1: Simple component with local state](#pattern-1-declare-a-simple-component-with-local-state)
  - [Pattern 2: Callbacks](#pattern-2-callbacks)
  - [Pattern 3: Refs](#pattern-3-use-ref-for-logical-reachability)
- [API Reference](#api-reference)
  - [App](#app)
  - [Elements](#elements)
  - [Component](#component-1)
  - [State](#state)
  - [Props](#props)
  - [Access API](#access-api)
    - [get_state](#get_statepath_or_refnone)
    - [set_state](#set_statepath_or_refnone-othernone-kwargs)
    - [reset_element](#reset_elementpath_or_refnone)
  - [Functional Components](#functional-components)
  - [Hooks](#hooks)
    - [use_state](#use_state)
    - [use_context](#use_context)
    - [use_memo](#use_memo)
    - [use_effect](#use_effect)
    - [use_ref](#use_ref)
    - [use_callback](#use_callback)
    - [use_previous](#use_previous)
    - [use_id](#use_id)
    - [Hooks in class Components](#hooks-in-class-components)
  - [Fiber](#fiber)
- [Theming and Config](#theming-and-config)
- [Built-ins](#built-ins)
  - [Flow helpers](#flow-helpers)
    - [Conditional](#conditional)
    - [KeepAlive](#keepalive)
    - [Case](#case)
    - [Switch, Match, Default](#switch-match-default)
  - [Router and Page](#router-and-page)
    - [Router](#router)
    - [Page](#page)
  - [Theme tooling](#theme-tooling)
    - [ThemeEditor](#themeeditor)
    - [ThemeEditorDialog](#themeeditordialog)
    - [ThemeEditorButton](#themeeditorbutton)
- [Examples](#examples)
- [Usage Guidelines](#usage-guidelines)
  - [Keep keys local and boring](#keep-keys-local-and-boring)
  - [Do not persist state manually](#do-not-persist-state-manually-in-stsession_state)
  - [Think in paths/refs, not instances](#think-in-pathsrefs-not-instances)
- [Non-Goals](#non-goals)
- [Dev](#dev)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install st-components
```

`st-components` builds on :
- [Streamlit](https://streamlit.io) as its core runtime and UI engine.
- [modict](https://github.com/B4PT0R/modict) for its data models (`State`, `Props`, `Fiber`, `Theme`, `Config`, ...). All are still dicts, but they natively support attribute access, typed fields with defaults, runtime type checking/coercion, traversal utilities, etc.


## Running an app

Run it like a normal Streamlit app:

```bash
streamlit run app.py
```

The library does not replace Streamlit's execution model. It just adds a component layer on top of the usual Streamlit API.

## Why This Exists

Plain Streamlit is fast to start with, low effort for good results, but more sophisticated apps often drift toward:

- One `st.session_state` to do it all... state data is centralized and doesn't live close to where it's used.
- UI structure gets easily mixed with logic and data processing, dependant on script order/conditions/rerun logic, which can be harder to reason about in complex scenarios.
- Streamlit's contraint on absolute widget keys makes achieving fully autonomous reusable blocks pretty tough (requires careful st.session_state management, and to automate key prefixing to avoid namespace collisions when duplicating a same block)
- Reactive logic can live both in-line and in callbacks, with slightly different behaviour, leading to subtle timing issues

`st-components` gives you a more explicit structure:

- Components own their layout and local state
- layout logic lives in the `render()` method
- Reactive logic lives in callbacks and hooks
- keys stay purely local, only required to be unique amongst siblings
- the framework derives full tree paths automatically from the actual nesting of components
- using multiple instances of a same component becomes trivial

## Quick Start

```python
from st_components import App, Component
from st_components.elements import button, container


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=0)

    def increment(self, _):
        self.state.count += 1

    def render(self):
        return button(key="button", on_click=self.increment)(
            f"Clicked {self.state.count} times"
        )


app = App()(
    container(key="home")(
        Counter(key="counter_1"), # "app.home.counter_1.button" (internally)
        Counter(key="counter_2"), # "app.home.counter_2.button" no collision
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

First, `__init__(...)` receives props. Then `__call__(...)` receives children and puts them in `self.props.children` (this step can be ommitted if you don't want to pass any children). This is just syntactic sugar so that tree construction feels readable and close enough to JSX within Python language constraints (without having to implement a dedicated JSX parser).

children can still be passed as a prop if necessary, so these two forms are equivalent:

```python
MyComponent(key="intro")("Hello")
MyComponent(key="intro", children=["Hello"])
```

In practice, the two-step style is the usual one because it makes nested UI trees much easier to read.

## Mental Model

### `Component`

A `Component` is a stateful unit.

- It has persistent local state.
- Its `render()` method returns Components, Elements, renderable values (anything supported by `st.write`) or tuples of these.
- A new Python instance is created on each rerun, but its state is restored from a `Fiber` stored in `st.session_state`.

### `Element`

An `Element` is a render primitive.

- It renders into a corresponding Streamlit widget
- Its `render()` method returns nothing
- The actual value of the widget, if any, lives in `st.session_state`, accessible by element path or ref.
- You can't declare a custom state on it.

You'll generally use ready-made elements from `st_components.elements` (all streamlit widgets can be found there) and won't have to bother how they are implemented, unless you want to wrap a custom or third-party widget. 

Any Component tree must recursively resolve into a tree of pure Elements. 

### Keys

Every Component and Element must have a `key`.

Keys are intentionally local:

- they only need to be unique among siblings
- they are not to be understood as global ids
- the framework will disambiguate from the render context

This means two nodes can both use `key="counter"` safely if they live in different branches.

In the final rendered tree, paths are derived structurally from the nesting of component keys.

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

    def toggle(self, _):
        self.state.open = not self.state.open

    def render(self):
        return container(key="panel", border=True)(
            button(key="toggle", on_click=self.toggle)(
                "Hide details" if self.state.open else "Show details"
            ),
            markdown(key="body")("Lots of details...") if self.state.open else None
        )
```

This is the preferred place for view state, local mode, and coordination between widgets.

### Pattern 2: Callbacks

Every event callback receives the element's **current output value** as its only argument — the same value accessible via `get_state(ref).output`.

All callbacks share the same signature:

- `on_change(value)` for stateful widgets — `value` is the current widget value
- `on_submit(value)` for `chat_input` — `value` is the submitted message
- `on_select(value)` for selection-capable charts and dataframes — `value` is the selection dict
- `on_click(value)` for buttons — `value` is `True` when the button was clicked

For example, a normal `on_change` handler receives the new value directly:

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

There is no separate `args` / `kwargs` callback plumbing layer on top of this. If a handler needs more context than the triggering payload, read it from component state, shared state, `Ref`s, or `get_state(...)`.

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

### Pattern 3: Use `Ref()` for logical reachability

Refs are path-based references to a given component or element in the tree. You attach one to a component or element when you want to access its state or value without having to provide its full path. They don't point to the instance directly, only to its location in the tree, which is enough to retrieve its state from the fiber (or its value from `st.session_state` directly in case of an element).

```python
from st_components import App, Component, Ref, get_state
from st_components.elements import button, container, markdown, text_input


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=0)

    def increment(self, _):
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

    def capture(self, _):
        self.state.snapshot = (
            f"name={get_state(self.name_ref).output or ''}, "
            f"count={get_state(self.counter_ref).count}"
        )

    def render(self):
        return container(key="demo", border=True)(
            text_input(key="name", ref=self.name_ref)("Name"),  # passing it the ref
            Counter(key="counter", ref=self.counter_ref),       # same
            button(key="capture", on_click=self.capture)("Read refs"),
            markdown(key="snapshot")(self.state.snapshot or "Nothing captured yet."),
        )


App()(RefDemo(key="refs")).render()
```

## API Reference

### `App`

`App` is the singleton root of the component tree and the entry point for every render cycle. Its key is always `app`, so all resolved component paths start with `app.`. Call `get_app()` to retrieve the instance from anywhere in the tree.

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
)
```

Props:

- `children`: the single root renderable. The two-step style `App()(MyLayout(key="layout"))` is preferred — it keeps props and tree structure visually separated.
- `page_title`, `page_icon`, `layout`, `initial_sidebar_state`, `menu_items`: forwarded to `st.set_page_config(...)`. Use these instead of calling `st.set_page_config` directly.
- `theme`: app-level Streamlit theme. Accepts a `Theme` instance or a plain dict. Applied at runtime only — use `.save_theme()` to persist to disk.
- `css`: extra CSS injected after the theme. Accepts a raw CSS string, a `.css` file path, a `Path`, or a list mixing those forms.
- `config`: selected Streamlit config values. Accepts a `Config` instance or a plain dict. Supported sections: `client`, `runner`, `browser`, `server`. Applied at runtime only — use `.save_config()` to persist to disk.

Methods:

- `.render()`: run the render cycle for the full app.
- `.render_page(page_tree)`: render a page tree through the active app instance, preserving the current multipage path prefix. Used from file-backed page sources: `get_app().render_page(...)`.
- `.create_shared_state(name, spec)`: declare a named shared state namespace. `spec` must be a `State` instance or subclass. Idempotent — calling it again with the same name is a no-op. Read from anywhere with `get_shared_state(name)`.
- `.set_theme(theme)`: replace the in-memory theme. Accepts a `Theme`, a dict, or `None`.
- `.save_theme(theme=None)`: optionally update, then persist the theme to `.streamlit/config.toml`.
- `.set_css(css)`: replace the in-memory CSS string.
- `.set_config(config)`: replace the in-memory Streamlit config. Accepts a `Config`, a dict, or `None`.
- `.save_config(config=None)`: optionally update, then persist the config to `.streamlit/config.toml`.

For multipage apps, `Router` and `Page` are normal structural components. The active page lives in the path system as `app.router.<page_key>.page...`.

### Elements

All built-in Streamlit widgets are available as ready-made elements in `st_components.elements`, organized by sub-package:

- `text` — `markdown`, `title`, `header`, `subheader`, `caption`, `code`, `latex`, `divider`
- `input` — `button`, `checkbox`, `radio`, `selectbox`, `multiselect`, `slider`, `text_input`, `text_area`, `number_input`, `date_input`, `time_input`, `color_picker`, `toggle`, `file_uploader`, `camera_input`, `chat_input`, `download_button`
- `layout` — `container`, `columns`, `tabs`, `expander`, `sidebar`, `popover`, `dialog`, `empty`
- `display` — `metric`, `json`, `dataframe`, `data_editor`, `table`, `image`
- `charts` — `line_chart`, `bar_chart`, `area_chart`, `scatter_chart`, `altair_chart`, `plotly_chart`, `pyplot`, `map`, `deck_gl_chart`
- `media` — `audio`, `video`
- `feedback` — `progress`, `spinner`, `status`, `toast`, `balloons`, `snow`, `success`, `info`, `warning`, `error`, `exception`

All wrappers share the same two additions over the standard Streamlit signatures:

- `key` is always required — the framework uses it to derive the element's path in the tree
- `ref` is always accepted — attach a `Ref()` to access the element's state later via `get_state(ref)` or `ref.state()`. The state fields follow these conventions:
  - `state.output` — current widget output value (text, number, date, bool, uploaded file, selection dict for charts/dataframes, …)
  - `state.handle` — Streamlit DeltaGenerator or control object returned by the underlying `st.*` call, for layout/container elements (`container`, `columns`, `tabs`, `form`, `expander`, `popover`, `sidebar`, `empty`, `chat_message`, `status`) and `progress`

#### Writing a custom element wrapper

`st_components.elements.factory` is the single import point for wrapping any Streamlit widget as a framework-aware `Element`:

```python
from st_components.elements.factory import (
    Element,          # base class
    element_factory,  # generates an Element class from a st.* callable
    callback,         # wraps an arbitrary callable as a widget callback
    widget_callback,  # wraps a named prop as a widget callback (from context)
    widget_child,     # first child or named prop (from context)
    widget_key,       # Streamlit session-state key (from context)
    widget_output,    # raw session-state value (from context)
    widget_props,     # filtered props dict, ready to splat (from context)
)
```

All context-resolving helpers (`widget_key`, `widget_output`, `widget_callback`, `widget_child`, `widget_props`) take no element argument — they read the currently rendering element from the render context automatically.

**`element_factory` — the quick path**

For widgets that follow the standard pattern, one line is enough:

```python
import streamlit as st
from st_components.elements.factory import element_factory

text_input  = element_factory(st.text_input,  child_prop="label", callback_prop="on_change")
button      = element_factory(st.button,      child_prop="label", callback_prop="on_click")
selectbox   = element_factory(st.selectbox,   child_prop="label", callback_prop="on_change")
dataframe   = element_factory(st.dataframe,   child_prop="data")
```

- `child_prop` — prop name (or `(name, default)` tuple) forwarded as the first positional argument to the `st.*` call via `widget_child()`.
- `callback_prop` — prop name of the event callback, wrapped via `widget_callback(prop_name)`.
- If the `st.*` call returns a context manager, children are rendered inside it automatically.
- An optional `props_schema` (a `Props` subclass) validates and documents accepted props.

**Subclassing `Element` — the full path**

Use `element_factory` for the common case. Subclass `Element` directly when you need a typed `__init__`, a custom `get_output_default`, or `get_output` post-processing:

```python
import streamlit as st
from st_components.elements.factory import Element, widget_key, widget_callback, widget_child, widget_props

class text_input(Element):
    def __init__(self, label=None, value="", on_change=None, *, key, ref=None, **kwargs):
        Element.__init__(self, key=key, label=label, value=value, on_change=on_change, ref=ref, **kwargs)

    def render(self):
        st.text_input(
            widget_child("label", ""),
            key=widget_key(),
            on_change=widget_callback(),       # defaults to "on_change"
            **widget_props("label", "on_change"),
        )
```

Override `get_output(raw)` to control what `state.output` exposes. `raw` is `None` when the widget has not yet been registered in session state (default: returns `None`). Override to return a prop value as the initial default, or to apply post-processing:

```python
# initial value from a "default" prop instead of "value"
class multiselect(Element):
    def get_output(self, raw):
        return self.props.get("default") if raw is None else raw

# post-processing: merge editing deltas back into the original dataframe
class data_editor(Element):
    def get_output(self, raw):
        return self._resolve_output(widget_child("data"), raw)  # handles None raw

    def render(self):
        st.data_editor(widget_child("data"), key=widget_key(), **widget_props("data"))
```

`widget_default(prop_name="value")` is the context-based shorthand for reading a default prop inside `render()`. Use `self.props.get(prop_name)` instead when inside `get_output`, since that method is also called from callbacks where the render context is not active.

When using `element_factory`, pass `default_prop` to wire the initial output automatically:

```python
text_input  = element_factory(st.text_input,  child_prop="label", callback_prop="on_change", default_prop="value")
multiselect = element_factory(st.multiselect, child_prop="label", callback_prop="on_change", default_prop="default")
button      = element_factory(st.button,      child_prop="label", callback_prop="on_click")   # no default needed
```

Use `callback(fn)` directly when the callback value is not a simple prop lookup — for example when wrapping a `on_select` that may be either a callable or a string sentinel:

```python
def render(self):
    on_select = self.props.get("on_select", "ignore")
    st.dataframe(
        widget_child("data"),
        key=widget_key(),
        on_select=callback(on_select) if callable(on_select) else on_select,
        **widget_props("data", "on_select"),
    )
```

### `Component`

`Component` is the base class for all stateful UI units. Subclass it and implement `render()` to return the subtree this component should produce — a Component, an Element, a tuple of those, a plain renderable value, or `None`.

**Instance members:**

- `self.props` — a `Props` modict populated from constructor arguments. Supports attribute access (`self.props.color`). `None` values in `children` are filtered out automatically.
- `self.children` — shorthand for `self.props.children`. A list of the positional arguments passed via `MyComponent(key="x")(*children)`.
- `self.state` — the component's local state. Before mount, writes go to a temporary dict; after mount, reads and writes go through the fiber. Can be initialized by assigning a dict in `__init__`, or by declaring a typed nested `State` subclass.
- `self.is_mounted` — `True` if the component has an active fiber in the current session.

**Methods:**

- `set_state(other=None, /, **kwargs)` — update state fields. Accepts a dict positional argument, keyword arguments, or both. Works whether or not the component is mounted.
- `sync_state(state_key)` — returns a callback suitable for `on_change`. When called with a value, it writes that value into `self.state[state_key]`. Shorthand for simple `on_change` handlers that mirror a widget value into component state.

**Lifecycle methods** (override as needed, default implementation is a no-op):

- `component_did_mount()` — called once when the fiber is first created (first render of this path).
- `component_did_unmount()` — called when the fiber is dropped (component left the tree for a full cycle without `keep_alive`).
- `component_did_update(prev_state)` — called at the end of each render cycle where `self.state` changed. `prev_state` is a snapshot of state from the previous cycle.

**Fragment support:**

Pass `fragment=True` as a class keyword to wrap the component's render in `st.fragment`, enabling partial reruns scoped to this component without rerunning the full app:

```python
class LiveChart(Component, fragment=True, run_every="2s"):

    def render(self):
        ...
```

`run_every` accepts a duration string (`"2s"`, `"500ms"`) or a `timedelta`. When set, Streamlit re-renders the fragment on that interval automatically.

### `State`

State is local, persistent per mounted component path, and restored automatically across reruns.

You can initialize state directly in `__init__`:

```python
def __init__(self, **props):
    super().__init__(**props)
    self.state = dict(count=0, label="clicks")
```

Or skip the `__init__` override and declare a typed nested subclass:

```python
from st_components import Component, State
from st_components.elements import button, container, metric


class Counter(Component):

    class CounterState(State):
        _config=State.config(extra="ignore")
        count: int = 0
        label: str = "clicks"

    def increment(self, _):
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

### Access API

`get_state`, `set_state`, and `reset_element` are the canonical way to reach any Component or Element in the tree from outside its own class, whether from a sibling render, a standalone callback, or a utility function.

All three accept a `path_or_ref` argument that can be:

- a `Ref` attached to a Component or Element at render time
- a fully-qualified path string (e.g. `"app.home.counter"`)
- omitted — defaults to the current render or callback context

```python
from st_components import get_state, set_state, reset_element
```

---

### `get_state(path_or_ref=None)`

Returns the current state of any rendered Element or mounted Component, or `None` if the path doesn't resolve to a live fiber.

- **Component** — returns the live `State` object (mutable, same object as `self.state` during render).
- **Element** — returns the live `ElementState` (frozen — read-only from outside the element's own render). Field conventions:
  - `state.output` — widget output value for all input/display elements (text, number, bool, file, selection dict for charts and dataframes, …)
  - `state.handle` — Streamlit DeltaGenerator / control object for layout and container elements (`container`, `columns`, `tabs`, `expander`, `form`, `popover`, `sidebar`, `empty`, `chat_message`, `status`, `progress`)

```python
# read an element's current value
name = get_state(name_ref).output

# read a component's state field
count = get_state(counter_ref).count

# from within the current context (no ref needed)
snapshot = get_state()

# via ref shorthand
snapshot = name_ref.state()
```

---

### `set_state(path_or_ref=None, other=None, /, **kwargs)`

Replaces or partially updates the state of a **Component**. Raises `RuntimeError` if the target is an Element — element state is managed exclusively by the element's own `render()`.

- *other* — a `dict` or `State` instance that replaces the component state wholesale.
- ***kwargs* — field updates merged on top (or instead) of *other*.

```python
# replace state entirely with a dict
set_state(counter_ref, {"count": 0})

# replace with a typed State instance
set_state(counter_ref, CounterState(count=0, label="restarted"))

# update one field only
set_state(counter_ref, count=0)

# from within the current context (targets the current component)
set_state(count=0)
```

---

### `reset_element(path_or_ref=None)`

Forces a stateful Element to be recreated on the next rerun, clearing its widget value from `st.session_state` so the declared `value=` prop takes effect again.

```python
reset_element(name_ref)
```

### Functional Components

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

When calling the component, you still pass individual props and children normally rather than a props dict. The decorator wraps them into the framework `Props` object and passes it to the function when rendering.

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

    def increment(st):
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

    def increment(st):
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

The provider is a component, so its key also appears in paths such as `app.theme_scope.toolbar`.

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

### Hooks in class Components

Hooks can also be used the same way in the `render()` method of class Components but, for some of them, the class has alternatives to using them:

- `use_state(...)` -> `self.state`
- `use_effect(...)` -> `component_did_mount()`, `component_did_update(prev_state)`, `component_did_unmount()` 
- `use_callback(...)` -> a normal instance method
- `use_previous(...)` -> a `prev_state` inside `component_did_update(...)`

The point is:

- hooks are used for persistent render-cycle data that must survive the short-lived component instance
- `self.state` and lifecycle methods of the class-oriented API surface can do the trick in some cases.

### Fiber

A `Fiber` is the persistent record that gives a component its continuity across reruns.

Because Streamlit reruns the entire script from top to bottom on every user interaction, component Python instances are short-lived — they are created fresh on each rerun and discarded at the end of it. The fiber is what survives between reruns: it lives in `st.session_state`, keyed by the component's resolved path (e.g. `app.home.counter`), and is the actual source of a component's persistent identity.

**What a fiber holds:**

- `state` — the component's local state dict, restored into `self.state` at render time
- `previous_state` — a snapshot of state from the previous render cycle, used to detect changes and feed `component_did_update(prev_state)`
- `component_id` — a UUID linking the fiber to the current Python instance, so lifecycle callbacks (`component_did_update`, `component_did_unmount`) reach the right object
- `hooks` — an ordered list of `HookSlot` entries, one per `use_*` call, each carrying the hook's `value`, `deps`, and optional `cleanup`
- `keep_alive` — a flag set by flow helpers (`Conditional`, `KeepAlive`, `Switch`, ...) to prevent a hidden branch from being unmounted even though it didn't render in this cycle

**The render cycle:**

1. `App.render()` calls `begin_render_cycle()`: all fibers have `keep_alive` reset to `False`, and a snapshot of all current states is saved.
2. Each component renders: its path is derived from the nested `key` context, the fiber at that path is looked up (or created on first render), state is restored from it, hooks are replayed in order, and the fiber is marked as rendered for this cycle.
3. `App.render()` calls `end_render_cycle()`:
   - Fibers that were not marked as rendered (and whose `keep_alive` is `False`) are **unmounted**: `component_did_unmount()` fires and the fiber is deleted.
   - Fibers whose state changed compared to the snapshot trigger `component_did_update(prev_state)`.
   - Pending hook effects are flushed (effects run, previous cleanups are called first if deps changed).
   - `previous_state` is updated for the next cycle.

**On first render**, the fiber does not yet exist: `mount()` creates it and `component_did_mount()` fires.

**Path derivation** is purely structural: every `key_context(self.key)` call pushes the current key onto a thread-local stack, so a component nested as `App > container("home") > Counter("c1")` automatically resolves to `app.home.c1` without any manual plumbing.

**Hook slots** are claimed by index in call order. The framework checks that the count and order of hook calls stays consistent between renders — calling hooks conditionally raises a `RuntimeError`, for the same reason as in React.

You generally do not interact with fibers directly. They are an implementation detail. But understanding them explains:

- why `self.state` survives reruns even though `self` does not
- why path-based reachability (`Ref`, `get_state`) works without holding object references
- why flow helpers need an explicit `keep_alive` mechanism rather than relying on plain Python conditionals
- why hook call order must be stable

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

- `Theme` fields name map to official Streamlit theme config keys
- theme persistence goes through `.streamlit/config.toml`
- live theme change is best-effort; some changes may require a complete rerun, or a restart.
- the persisted config in `.streamlit/config.toml` is the default source.
- CSS is injected after theme application, so CSS can intentionally override theme-driven styles

To see this live:

```bash
python -m st_components.examples theme_editor
```

## Built-ins

`st_components.builtins` contains higher-level structural helpers built on top of the core component model.

```python
from st_components.builtins import (
    Conditional, Case, Switch, Match, Default,
    KeepAlive, ThemeEditorButton, ThemeEditorDialog, Router, Page,
)
```

### Flow helpers

Flow helpers let you express conditional and switched rendering declaratively, as part of the component tree.

The key property they share is **state preservation**: hidden branches are not unmounted — their fibers are kept alive so that state is not lost when a branch becomes visible again. A plain Python `if` would discard the hidden component's fiber on every rerun; flow helpers avoid that.

#### `Conditional`

Renders its first child when `condition` is `True`, its optional second child otherwise.

```python
from st_components.builtins import Conditional

Conditional(key="toggle", condition=self.state.logged_in)(
    Dashboard(key="dashboard"),
    LoginForm(key="login"),
)
```

#### `KeepAlive`

Renders its single child when `active=True`, hides it when `False`, but keeps the fiber alive in both cases.

```python
from st_components.builtins import KeepAlive

KeepAlive(key="panel", active=self.state.show_panel)(
    HeavyPanel(key="content"),
)
```

Useful when hiding a subtree that is expensive to reinitialize, or when you want to preserve its internal state without rendering it.

#### `Case`

Selects one child by integer index. All other branches have their fibers preserved.

```python
from st_components.builtins import Case

Case(key="step", case=self.state.current_step)(
    StepOne(key="step_1"),
    StepTwo(key="step_2"),
    StepThree(key="step_3"),
)
```

#### `Switch`, `Match`, `Default`

`Switch` matches its `value` against a set of `Match(when=...)` children and renders the matching one, falling back to `Default` if present. All unmatched branches have their fibers preserved.

```python
from st_components.builtins import Switch, Match, Default

Switch(key="view", value=self.state.active_tab)(
    Match(key="home",     when="home")(HomePage(key="page")),
    Match(key="settings", when="settings")(SettingsPage(key="page")),
    Default(key="fallback")(NotFound(key="page")),
)
```

### Router and Page

`Router` and `Page` compile Streamlit's multipage navigation while keeping all pages inside the normal component path system.

#### `Router`

Declares the navigation structure. Its children must all be `Page` instances.

```python
from st_components.builtins import Router, Page

Router(key="router", position="sidebar")(
    Page(key="home",     nav_title="Home",     default=True)(HomePage),
    Page(key="settings", nav_title="Settings")(SettingsPage),
)
```

Props:
- `position`: where the navigation is rendered — `"sidebar"` (default), `"top"`, or `"hidden"`.
- `expanded`: whether the sidebar nav is expanded by default.

#### `Page`

Wraps a page source and declares its navigation metadata. The source is passed as the single child and can be:
- a `Component` class or instance
- a callable
- a file path or path string (for file-backed pages)

```python
Page(
    key="report",
    nav_title="Report",
    nav_icon=":material/bar_chart:",
    url_path="report",
    section="Analytics",
    default=False,
    visibility="visible",
    layout="wide",
)(ReportPage)
```

Props:
- `nav_title`, `nav_icon`: label and icon shown in the navigation.
- `url_path`: explicit URL path segment for this page.
- `default`: if `True`, this page is shown when no URL path matches.
- `section`: groups pages under a heading in the navigation.
- `visibility`: `"visible"` (default) or `"hidden"` — hides the page from navigation without removing it.
- `layout`, `page_title`, `page_icon`, `initial_sidebar_state`, `menu_items`: per-page overrides of Streamlit page config.

Pages live inside the component path system: a page component rendered from `Page(key="report")` under `Router(key="router")` produces paths like `app.router.report.page...`.

### Theme tooling

#### `ThemeEditor`

A full inline theme editor widget. Exposes controls for base theme, font, colors, corner radii, widget borders, and optional custom CSS. Changes are applied live and can be saved to `.streamlit/config.toml`.

```python
from st_components.builtins import ThemeEditor

ThemeEditor(key="editor")()
```

#### `ThemeEditorDialog`

Wraps `ThemeEditor` in a Streamlit dialog. Useful when you want the editor accessible but out of the way.

```python
from st_components.builtins import ThemeEditorDialog

ThemeEditorDialog(key="dialog", open=self.state.open, title="Theme editor", width="large")
```

Props: `open`, `title`, `show_css`, `width`.

#### `ThemeEditorButton`

A button that opens a `ThemeEditorDialog`. The most common entry point during development.

```python
from st_components.builtins import ThemeEditorButton

ThemeEditorButton(key="theme_btn", type="primary")("Edit theme")
```

Props: `label`, `title`, `show_css`, `width`, `type`, `help`, `icon`, `use_container_width`, `disabled`, `shortcut`.

See the [Theming and Config](#theming-and-config) section for the recommended development workflow.

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
- `multipage`: demonstrates a bit more advanced patterns: router, pages, component-backed pages, file-backed pages, shared state, and a lightweight provider above the router
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

-> This is already done internally

### Do not persist state manually in `st.session_state`

The framework already does that for you. Reach local component state with `self.state`, and reach any element or component state via `get_state(...)` or `ref.state()`.

If you need custom state shared across several components, declare it once with `app.create_shared_state("my_custom_state", State())` and consume it with `get_shared_state("my_custom_state")`.

### Think in paths/refs, not instances

Because every rerun recreates the tree, the stable identity of a component is its location in the tree materialized as a resolved path, or a `Ref` pointing to it, not the Python object from a previous run.

Component instances are short-lived and not persisted, they won't survive the current render cycle. They will be discarded in the garbage collector at the end of it.

From the point of view of the framework's internals, they are mostly wrappers around their render function and hold no precious state.

All that gives them a useful continuity (state, etc.) is persisted in and fetched from the `Fiber` at rendering time

This is why component coordination should preferably use the dedicated API:

- local state for behavior internal to one component
- context for ambient values shared by one subtree
- shared state for app-level coordination
- refs when you need path-based reachability to a specific mounted node

Any custom data that's attached only on the instance will die with it at the end of the current cyle.

## Non-Goals

`st-components` is not trying to provide:

- a virtual DOM
- JSX syntax/parser
- a replacement for Streamlit's execution model

It is a structuring layer over Streamlit, not a different frontend runtime.

## Dev

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Tests cover the core component model, elements, hooks, functional components, context, and the examples runner. They run without a live Streamlit server.

## Contributing

Contributions are welcome — don't wait for me to think of everything.

If you have an idea for a new built-in, a missing element wrapper, a hook, a better API surface, or just spotted something odd: open an issue or send a PR. The codebase is small and intentionally kept that way, so it is easy to navigate.

Things that are especially useful:
- bug reports with a minimal reproducible example
- missing element wrappers (anything from the Streamlit docs not yet covered)
- new built-ins for structural patterns you hit repeatedly
- docs improvements — if something was unclear to you, it is unclear to the next person too

## License

MIT
