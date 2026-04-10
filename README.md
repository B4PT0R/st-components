# st-components

`st-components` is a React-inspired component-based framework using [Streamlit](https://streamlit.io) as its render engine. 

Simply put, `st-components` adds a higher level component API on top of Streamlit.

It's still 100% Streamlit, same widgets, same runtime, same script-rerun pattern, but it changes the way you **think** about Streamlit components and **how** you will combine them to build an app.

Instead of thinking your components as **functions**,  rendering immediately when called, returning their last known value from the UI, and combined in imperative fashion to achieve a more complex app logic (which is the standard Streamlit mental model):

```python
import streamlit as st

if "greeted_name" not in st.session_state:
    st.session_state.greeted_name = ""

def greet():
    st.session_state.greeted_name = st.session_state.name_input

st.header("Demo App")
with st.container(key="pannel", border=True):
    name = st.text_input(key="name_input", label="Enter your name:")
    if name:
        st.button("Show greetings!", key="greet", on_click=greet)
    if st.session_state.greeted_name:
        st.markdown(f"Hello {st.session_state.greeted_name}!")
```

In `st-components`, you think of components as nested **objects**, each with a **render** method returning the widgets it should show on screen, and who manage their **state** and logic internally via **events callbacks**. For those who already know React, it should sound quite familiar:

```python
from st_components import App, Component
from st_components.elements import header, container, text_input, button, markdown

class Demo(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(name="", greeted_name="")

    def greet(self):
        self.state.greeted_name = self.state.name

    def render(self):
        return (
            header(key="h")("Demo App"),
            container(key="pannel", border=True)(
                text_input(key="name_input", label="Enter your name:", on_change=self.sync_state("name")),
                button(key="greet", label="Show greetings!", on_click=self.greet) if self.state.name else None,
                markdown(key="m")(f"Hello {self.state.greeted_name}!") if self.state.greeted_name else None,
            )
        )

App(Demo(key="demo")).render()
```

Admittedly, the second is a bit more verbose, so it's probably not that suitable for beginners. But it's much more powerful when it comes to turn components into stateful, reusable and composable building blocks, handling their own state and logic internally.

Notice the contrast: the vanilla version requires global `st.session_state` init guards, string-based key references (`st.session_state.name_input`), and a standalone callback. The component version keeps state local, callbacks are methods, and everything is encapsulated.

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
  - [Pattern 3: Refs](#pattern-3-use-refs-for-logical-reachability)
  - [Pattern 4: Fragments and scoped re-rendering](#pattern-4-fragments-and-scoped-re-rendering)
  - [Pattern 5: Dynamic rendering from callbacks](#pattern-5-dynamic-rendering-from-callbacks)
- [API Reference](API_REFERENCE.md)
- [App](#app)
- [Theming](#theming)
- [Built-ins](#built-ins)
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
- Layout logic lives in the `render()` method
- Reactive logic lives in callbacks and hooks
- Keys stay purely local (only unique among siblings) — or auto-generated
- The framework derives full tree paths automatically from the actual nesting of components
- Using multiple instances of a same component becomes trivial
- **Fine-grained re-rendering**: the `fragment` element lets you scope Streamlit fragment boundaries to any subtree — nested fragments re-render independently, giving you precise control over what refreshes and when

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
        return button(key="button", on_click=self.increment)(
            f"Clicked {self.state.count} times"
        )


App(
    container(key="home")(
        Counter(key="counter_1"), # "app.home.counter_1.button" (internally)
        Counter(key="counter_2"), # "app.home.counter_2.button" no collision
    )
).render()
```

Each `Counter` keeps its own state across reruns.

Children can be passed as positional arguments to `__init__`, or via `__call__` in a second step:

```python
# One-step — children as positional args, props as keyword args
MyComponent(child_a, child_b, key="intro")

# Two-step — props first, children second (closer to JSX)
MyComponent(key="intro")(child_a, child_b)
```

Both forms are equivalent. The two-step style is the usual one because in Python keyword arguments must come after positional ones, and having props before children makes nested UI trees much easier to read:

```python
# Two-step: props visually precede children — reads top-down like JSX
container(key="page", border=True)(
    Header(key="h"),
    Body(key="b"),
)

# One-step: children before props — less readable for deep trees
container(Header(key="h"), Body(key="b"), key="page", border=True)
```

In practice, use one-step for simple wrappers with few or no props, and two-step for anything with a richer prop set.

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
- The actual value of the widget, if any, lives in `st.session_state`, accessible via `self.child_key.state().output` from a parent, or `ref.state().output`.
- You can't declare a custom state on it.

You'll generally use ready-made elements from `st_components.elements` (all streamlit widgets can be found there) and won't have to bother how they are implemented, unless you want to wrap a custom or third-party widget. 

Any Component tree must recursively resolve into a tree of pure Elements. 

### Keys

Keys identify a component among its siblings.

- They only need to be unique among siblings, not globally.
- The framework derives full tree paths from the nesting: `app.dashboard.filters.name`.
- Two nodes can both use `key="counter"` safely if they live in different branches.

Keys are **optional**. When omitted, the framework auto-generates `{ClassName}_{child_index}`:

```python
# Explicit keys (recommended for stateful widgets and refs)
text_input(key="username", value="Alice")("Username")

# Auto-keys (fine for static layouts)
container()(
    Header(),       # → Header_0
    Sidebar(),      # → Sidebar_1
    Content(),      # → Content_2
)
```

Explicit keys are always preferred when state persistence or ref access matters.

## Onboarding Path

If you're new to the library, this is the shortest useful path:

1. Start with `App`, `Component`, and a few `elements`.
2. Use `self.state` inside components for local UI state.
3. Pipe event handlers to deal with app logic.
4. Navigate children with `self.child_key` — it returns a `Ref` you can read state from.
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
            markdown(key="body")("Lots of details...") if self.state.open else None
        )
```

This is the preferred place for view state, local mode, and coordination between widgets.

### Pattern 2: Callbacks

Element callbacks support **two signatures**:

- **With value** — `fn(value)` — receives the widget's current output, useful for `on_change` handlers that need the new value.
- **Without value** — `fn()` — called with no arguments, useful for simple `on_click` actions that don't need the widget value.

The framework inspects the callback's signature at render time and adapts automatically. Both styles work for all event props (`on_change`, `on_click`, `on_submit`, `on_select`).

```python
from st_components import Component, State
from st_components.elements import button, text_input

class Form(Component):

    class FormState(State):
        name: str = ""

    # Receives the new value — common for on_change
    def sync_name(self, value):
        self.state.name = value

    # No value needed — common for on_click
    def submit(self):
        print(f"Submitted: {self.state.name}")

    def render(self):
        return (
            text_input(key="name", value=self.state.name,
                       on_change=self.sync_name)("Name"),
            button(key="go", on_click=self.submit)("Submit"),
        )
```

Lambdas work the same way:

```python
# Receives value
on_change=lambda value: state.update(name=value)

# No value
on_click=lambda: state.update(count=state.count + 1)
```

If the callback does nothing except copy the widget value into a state field, use the `sync_state(...)` shortcut:

```python
text_input(
    key="name",
    value=self.state.name,
    on_change=self.sync_state("name"),
)("Name")
```

### Pattern 3: Use refs for logical reachability

Every component is a cursor into the tree. Navigate to any descendant with attribute access — the returned `Ref` lets you read state, override children, or reset the node:

```python
from st_components import App, Component
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

    def capture(self):
        # Navigate to children by attribute — each returns a Ref
        name_output = self.name.state().output or ""
        count_value = self.counter.state().count
        self.state.snapshot = f"name={name_output}, count={count_value}"

    def render(self):
        return container(key="demo", border=True)(
            text_input(key="name")("Name"),
            Counter(key="counter"),
            button(key="capture", on_click=self.capture)("Read refs"),
            markdown(key="snapshot")(self.state.snapshot or "Nothing captured yet."),
        )


App(RefDemo(key="refs")).render()
```

`self.name` resolves to `Ref("app.refs.demo.name")` — a lightweight path cursor. Call `.state()` to read, `ref(*children, **props)` to override, `.reset()` to clear.

You can also create an explicit `Ref()` and pass it via the `ref=` prop — useful when the accessing component is not an ancestor (e.g. a sibling reading another sibling's state via shared parent):

```python
from st_components import Ref

ref = Ref()
text_input(key="name", ref=ref)("Name")

# Later, in a callback:
ref.state().output  # read the widget value
```

### Pattern 4: Fragments and scoped re-rendering

In vanilla Streamlit, every widget interaction re-runs the entire script. With `st-components`, you can scope re-rendering to a subtree using the `fragment` element.

**Step 1 — The problem.** Two counters on the same page. Click one, both re-render:

```python
class Page(Component):
    class S(State):
        a: int = 0
        b: int = 0

    def render(self):
        return columns(key="cols")(
            button(key="a", on_click=lambda: self.state.update(a=self.state.a + 1))(f"A: {self.state.a}"),
            button(key="b", on_click=lambda: self.state.update(b=self.state.b + 1))(f"B: {self.state.b}"),
        )
```

**Step 2 — Scope it.** Wrap one side in `fragment(scoped=True)`. Now clicking inside the fragment only re-renders that subtree:

```python
from st_components.elements import fragment

class Page(Component):
    class S(State):
        a: int = 0
        b: int = 0

    def render(self):
        return columns(key="cols")(
            button(key="a", on_click=lambda: self.state.update(a=self.state.a + 1))(f"A: {self.state.a}"),
            fragment(key="right", scoped=True)(
                button(key="b", on_click=lambda: self.state.update(b=self.state.b + 1))(f"B: {self.state.b}"),
            ),
        )
```

Clicking B no longer re-renders A. That's it — one line of wrapping.

**Step 3 — Auto-refresh.** Add `run_every` and the fragment refreshes on a timer, independently:

```python
fragment(key="clock", scoped=True, run_every="2s")(
    metric(key="time", label="Live", value=datetime.datetime.now().strftime("%H:%M:%S")),
)
```

The clock ticks every 2 seconds. The rest of the page is untouched.

**Step 4 — Nest them.** Fragments nest naturally. Each is an independent re-render boundary:

```python
fragment(key="outer", scoped=True)(
    Controls(key="ctrl"),       # re-renders with outer
    fragment(key="inner", scoped=True, run_every="1s")(
        LiveChart(key="chart"), # re-renders alone every 1s
    ),
)
```

Clicking a control in `outer` re-renders `outer` (including `inner`). But the inner clock ticks on its own without touching `outer` or the rest of the page.

**Step 5 — Named columns.** Use `column(key=...)` so each side of a layout has its own path in the tree:

```python
columns(key="grid")(
    column(key="sidebar")(FilterPanel(key="f")),   # path: grid.sidebar.f
    column(key="main")(DataTable(key="t")),         # path: grid.main.t
)
```

No key collisions, precise scoping, and refs resolve to the exact column.

This is **composable, fine-grained re-render control** — just by placing nodes in the tree.

### Pattern 5: Dynamic rendering from callbacks

Every node in the tree is pilotable from callbacks. The component IS a cursor — navigate children with attribute access, override with `__call__`, reset with `.reset()`.

```python
from st_components import App, Component
from st_components.elements import button, caption, container, fragment, metric


class Dashboard(Component):

    def load(self):
        # Navigate to the node and override its children
        self.page.results(
            metric(key="n", label="Rows loaded", value=1234),
        )

    def reset(self):
        self.page.results.reset()  # back to initial children

    def render(self):
        return container(key="page")(
            fragment(key="results")(
                caption(key="hint")("No data yet."),  # initial content
            ),
            button(key="load", on_click=self.load)("Load data"),
            button(key="reset", on_click=self.reset)("Reset"),
        )


App(Dashboard()).render()
```

How it works:

1. **In `render()`** — `fragment(key="results")` declares a node with initial children.
2. **In the callback** — `self.page.results(children)` stores overrides on the fiber.
3. **On the next rerun** — the node renders the overrides instead of the initial children.
4. **`.reset()`** — clears overrides, node reverts to parent-passed content.

Navigation is fluent — `self.page.results` resolves to the fiber path `app.Dashboard.page.results`. Override props with kwargs: `self.page.card(color="blue")("child")`. Chain freely.

The full navigation API — all expressions return **Ref objects** (lightweight path-based cursors), not Component instances:

```python
self.ref              # Ref to this component
self.parent           # Ref to the parent
self.root             # Ref to the App (tree root)
self.page.results     # Ref to any descendant
self.root.other.node  # absolute path from root
```

A `Ref` is an ephemeral cursor — it holds only a path string and reconstructs itself on every access. The fiber at that path holds the actual state. Use `ref.state()` to read, `ref(*children, **props)` to override, `ref.reset()` to clear.

## API Reference

See **[API_REFERENCE.md](API_REFERENCE.md)** for the full reference covering all public APIs:

App, Component, Element, State, Props, Hooks, Context, Ref, Fragment, Slot, Column/Tab, Scoped Rerun, Shared State, Local Storage, Query Params, Streamlit APIs, Flow Helpers, Router/Page, Theming, Elements Catalog, and Custom Element authoring.

---

## App

`App` is the root of every `st-components` application. It manages page config, theming, CSS, render cycles, and app-level state.

### App-level state

Set `app.state` before `render()` to initialize state — it works like a Component's state setter (no-op on subsequent reruns once the fiber exists):

```python
from st_components import App, State
from st_components.elements import container, text_input

class AppState(State):
    user: str = ""
    lang: str = "en"

app = App(page_title="My App")
app.state = AppState()  # initial state, ignored on reruns

app(
    MyLayout(key="layout")
).render()
```

The state is then accessible from anywhere via `get_app().state`.

### Subclassing App

You can subclass `App` and declare a `State` inner class, just like any `Component`. Override `render()` to return the root of your tree:

```python
class MyApp(App):
    class AppState(State):
        user: str = ""
        lang: str = "en"

    def render(self):
        return container(key="main")(
            Header(key="header"),
            Body(key="body"),
        )

MyApp(page_title="My App").render()
```

`render()` is fully overridable — return any Component, Element, Router, or tree of them. The framework infrastructure (page config, styles, routing, rerun control) is handled by the decorator, not by `render()` itself.

You can still use the `App(root)` pattern without subclassing — the default `render()` just returns the child passed at init or via `__call__`.

## Theming

`Theme` holds dual palettes (`light` / `dark`) and shared settings. `color_mode` on `App` selects the active palette.

```python
from st_components import App, Theme, ThemeSection

app = App(
    theme=Theme(
        dark=ThemeSection(
            primaryColor="#2dd4bf",
            backgroundColor="#0f172a",
            textColor="#e2e8f0",
        ),
        dark_sidebar=ThemeSection(backgroundColor="#111827"),
    ),
    color_mode="dark",
    css="body { font-size: 16px; }",
)(MyLayout(key="layout"))  # or pass as first arg: App(MyLayout(...), theme=...)
```

Drop a `ThemeEditorButton` anywhere to tune the theme visually during development, then persist the result with **Save**:

```python
from st_components.builtins import ThemeEditorButton

ThemeEditorButton(key="theme", type="primary")("Edit theme")
```

Theme and CSS changes are applied live. Saved themes persist to `.streamlit/stc-config.toml`.

## Built-ins

`st_components.builtins` provides higher-level helpers built on top of the core model. See the [API Reference](API_REFERENCE.md) for full props and signatures.

### Fragment

`fragment(scoped=True)` wraps children in a `st.fragment()` — an **independent re-render boundary**. Widget interactions inside the fragment only re-run that subtree, not the whole app. Fragments can be nested, each with its own rerun timeline.

```python
container(key="dashboard")(
    fragment(key="sidebar", scoped=True)(
        FilterPanel(key="filters"),
    ),
    fragment(key="main", scoped=True)(
        DataTable(key="table"),
        fragment(key="live", scoped=True, run_every="2s")(
            LiveMetrics(key="metrics"),
        ),
    ),
)
```

Without `scoped=True`, `fragment` is transparent grouping (like React's `<Fragment>`).

### Scoped Rerun

`rerun()` and `wait()` are automatically scoped to the current fragment. Each scoped fragment has its own independent timeline.

```python
rerun()                  # current scope (fragment or app)
rerun(scope="app")       # force full app rerun
rerun(wait=1.5)          # rerun after delay
rerun(wait=False)        # immediate hard rerun
wait(1.5)                # delay next rerun
```

Also available as `App.rerun()` and `App.wait()`.

### Flow helpers

Declarative conditional rendering with **state preservation** — hidden branches keep their fibers alive, unlike a plain `if`.

```python
from st_components.builtins import Conditional, KeepAlive, Case, Switch, Match, Default

# Show/hide with preserved state
Conditional(key="auth", condition=logged_in)(Dashboard(key="dash"), LoginForm(key="login"))
KeepAlive(key="panel", active=show)(HeavyPanel(key="content"))

# Select by index
Case(key="step", case=current_step)(StepOne(key="s1"), StepTwo(key="s2"), StepThree(key="s3"))

# Select by value
Switch(key="view", value=active_tab)(
    Match(key="home", when="home")(HomePage(key="page")),
    Match(key="settings", when="settings")(SettingsPage(key="page")),
    Default(key="fallback")(NotFound(key="page")),
)
```

### Router and Page

Multipage navigation built on `st.navigation`, with pages inside the component path system.

```python
from st_components.builtins import Router, Page

Router(key="router", position="sidebar")(
    Page(key="home", nav_title="Home", default=True)(HomePage),
    Page(key="settings", nav_title="Settings")(SettingsPage),
    Page(key="report", nav_title="Report", section="Analytics")(ReportPage),
)
```

Pages can be component classes, instances, callables, or file paths.

## Examples

The `examples/` directory contains numbered, self-contained Streamlit apps forming a guided progression:

```bash
python -m st_components.examples 01_hello
python -m st_components.examples --list
```

| # | Name | What you learn |
|---|---|---|
| 01 | `01_hello` | Component, State, render — the absolute minimum |
| 02 | `02_state` | Typed State, multi-field state, fiber persistence |
| 03 | `03_callbacks` | on_change receives the value, sync_state shortcut |
| 04 | `04_composition` | Children, nesting, layout, reusable building blocks |
| 05 | `05_elements` | Catalog of every built-in element wrapper |
| 06 | `06_functional` | @component decorator, use_state, class vs functional |
| 07 | `07_refs` | self.ref, self.parent, self.root, attribute navigation, fiber overrides |
| 08 | `08_hooks` | use_memo, use_effect, use_ref, use_callback, use_previous, use_id |
| 09 | `09_fragments` | fragment, scoped re-rendering, run_every, nested fragments |
| 10 | `10_scoped_rerun` | rerun, wait, independent per-fragment rerun timelines |
| 11 | `11_dynamic_rendering` | self.child navigation, fiber overrides, Ref.parent, column/tab scoping |
| 12 | `12_context` | create_context, Provider, use_context — no prop drilling |
| 13 | `13_flow` | Conditional, KeepAlive, Case, Switch/Match/Default |
| 14 | `14_theming` | ThemeEditorButton, live theme customization |
| 15 | `15_multipage` | Router, Page, shared state, file-backed pages |
| 16 | `16_full_data_app` | Multipage data-science app — all features combined |

You can also run files directly: `streamlit run examples/01_hello.py`.

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

The framework already does that for you. Reach local state with `self.state`, and reach any child's state via attribute navigation: `self.child_key.state()`. For non-hierarchical access, use `get_state(path)`.

If you need custom state shared across several components, declare it once with `app.create_shared_state("my_custom_state", State())` and consume it with `get_shared_state("my_custom_state")`.

### Think in paths/refs, not instances

Because every rerun recreates the tree, the stable identity of a component is its location in the tree materialized as a resolved path, or a `Ref` pointing to it, not the Python object from a previous run.

Component instances are short-lived and not persisted, they won't survive the current render cycle. They will be discarded in the garbage collector at the end of it.

From the point of view of the framework's internals, they are mostly wrappers around their render function and hold no precious state.

All that gives them a useful continuity (state, etc.) is persisted in and fetched from the `Fiber` at rendering time

This is why component coordination should preferably use the dedicated API:

- `self.state` for behavior internal to one component
- `self.child_key.state()` to read a child's state from a callback
- context for ambient values shared by one subtree
- shared state for app-level coordination
- explicit `Ref()` + `ref=` prop only when you need cross-branch reachability (sibling to sibling)

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
