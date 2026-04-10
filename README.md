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

    def on_click(self):
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
  - [Pattern 4: Fragments and scoped re-rendering](#pattern-4-fragments-and-scoped-re-rendering)
  - [Pattern 5: Dynamic rendering from callbacks](#pattern-5-dynamic-rendering-from-callbacks)
- [API Reference](API_REFERENCE.md)
- [Theming and Config](#theming-and-config)
- [Built-ins](#built-ins)
  - [Fragment](#fragment)
  - [Scoped Rerun](#scoped-rerun)
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

### Pattern 3: Use `Ref()` for logical reachability

Refs are path-based references to a given component or element in the tree. You attach one to a component or element when you want to access its state or value without having to provide its full path. They don't point to the instance directly, only to its location in the tree, which is enough to retrieve its state from the fiber (or its value from `st.session_state` directly in case of an element).

```python
from st_components import App, Component, Ref, get_state
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


App()(Dashboard()).render()
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

## Theming and Config

Use `theme=...`, `css=...`, and `config=...` on `App(...)` to control the visual shell of the app.

- `theme` covers Streamlit's theme tokens
- `css` covers custom styling outside those tokens
- `config` covers the supported Streamlit config sections exposed by the library

Use a `Theme` passed to `App` to control Streamlit theming (a plain dict also works):

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

### Fragment

The `fragment` element is one of the most powerful tools in `st-components`. It gives you **fine-grained control over Streamlit's re-rendering** — something that's awkward or impossible with vanilla Streamlit.

```python
from st_components.elements import fragment
```

**Two modes:**

- `scoped=False` (default) — transparent grouping, like React's `<Fragment>`. Children render in sequence, no wrapper. Useful to return multiple elements from `render()` without an extra container.
- `scoped=True` — wraps children in `st.fragment()`. Streamlit only re-runs **this subtree** on widget interactions within it, leaving the rest of the page untouched.

```python
# Transparent grouping
fragment(key="grp")(header, body, footer)

# Scoped re-rendering
fragment(key="live", scoped=True, run_every="5s")(
    LiveChart(key="chart"),
    RefreshButton(key="btn"),
)
```

**Nested fragments re-render independently.** Streamlit natively supports fragment nesting, and `st-components` leverages this transparently:

```python
container(key="dashboard")(
    fragment(key="sidebar", scoped=True)(
        FilterPanel(key="filters"),       # re-runs alone when filters change
    ),
    fragment(key="main", scoped=True)(
        DataTable(key="table"),           # re-runs alone when sorting
        fragment(key="live", scoped=True, run_every="2s")(
            LiveMetrics(key="metrics"),   # auto-refreshes without touching anything
        ),
    ),
)
```

Each scoped fragment is an independent re-render boundary. Clicking inside `filters` doesn't re-run `table` or `metrics`. The `live` fragment refreshes every 2 seconds without touching anything else. This is **free fine-grained re-render control** — just by placing `fragment(scoped=True)` nodes in your component tree.

| Prop | Default | Description |
|---|---|---|
| `scoped` | `False` | When `True`, wraps children in `st.fragment()` |
| `run_every` | `None` | Auto-refresh interval (only when `scoped=True`) — accepts seconds, timedelta, or Pandas duration strings |


### Scoped Rerun

`rerun()` and `wait()` are **automatically scoped** to the current fragment. Each scoped fragment has its own independent rerun timeline — delays in one fragment don't block others or the app.

```python
from st_components.core.rerun import rerun, wait
```

**Inside a scoped fragment**, `rerun()` and `wait()` target that fragment only:

```python
fragment(key="live", scoped=True)(
    # rerun() here only re-runs this fragment
    # wait(1.5) here only delays this fragment's rerun
)
```

**Outside any fragment**, they target the full app. Use `scope="app"` to force app-level rerun from inside a fragment:

```python
rerun()                  # current scope (fragment or app)
rerun(scope="app")       # force full app rerun
rerun(wait=1.5)          # rerun current scope after 1.5s
rerun(wait=False)        # immediate hard rerun
wait(1.5)                # delay current scope's next rerun by 1.5s
```

**Multiple calls merge** — the longest delay within a scope wins. Different scopes are fully independent:

```python
# Two fragments with different timelines, zero interference
fragment(key="fast", scoped=True)(
    # rerun(wait=0.3) → ticks at 0.3s
)
fragment(key="slow", scoped=True)(
    # rerun(wait=2.0) → ticks at 2.0s
)
# App-level rerun(wait=5) runs independently of both
```

**Nested fragments** each have their own scope. The inner fragment's `rerun()` doesn't touch the outer one:

```python
fragment(key="outer", scoped=True)(
    Controls(key="ctrl"),                    # rerun() → outer scope
    fragment(key="inner", scoped=True)(
        LiveChart(key="chart"),              # rerun() → inner scope only
    ),
)
```

| Function | Default scope | Description |
|---|---|---|
| `rerun(scope, wait)` | Current fragment or app | Request a scoped rerun with optional delay |
| `wait(delay, scope)` | Current fragment or app | Request a minimum delay without triggering a rerun |
| `check_rerun(scope)` | Current fragment or app | Execute pending rerun (called automatically) |

Also available as `App.rerun()` and `App.wait()`.


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
| 11 | `11_dynamic_rendering` | self.ref(path), fiber overrides, Ref.parent, column/tab scoping |
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
