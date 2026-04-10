# API Reference

Comprehensive reference for the `st-components` public API.

## Table of Contents

- [App](#app)
- [Component](#component)
- [Element](#element)
- [State](#state)
- [Props](#props)
- [Functional Components](#functional-components)
- [Hooks](#hooks)
- [Context](#context)
- [Ref and Navigation](#ref-and-navigation)
- [Access API](#access-api)
- [Fragment](#fragment)
- [Column / Tab](#column--tab)
- [Scoped Rerun](#scoped-rerun)
- [Shared State](#shared-state)
- [Local Storage](#local-storage)
- [Query Params](#query-params)
- [Streamlit APIs](#streamlit-apis)
- [Flow Helpers](#flow-helpers)
- [Router / Page](#router--page)
- [Theming](#theming)
- [Elements Catalog](#elements-catalog)
- [Writing Custom Elements](#writing-custom-elements)
- [Fiber (Internals)](#fiber-internals)


[↑ Back to top](#table-of-contents)

---

## App

Singleton root of the component tree.

```python
app = App(
    page_title="My App",
    page_icon=":material/home:",
    layout="wide",
    theme=Theme(primaryColor="#0f766e"),
    css="body { font-size: 16px; }",
    config=Config(client={"toolbarMode": "minimal"}),
    query_params=MyParams,
)
```

| Prop | Description |
|---|---|
| `page_title`, `page_icon`, `layout`, `initial_sidebar_state`, `menu_items` | Forwarded to `st.set_page_config()` |
| `theme` | `Theme` or dict — applied at runtime |
| `css` | CSS string, `.css` path, `Path`, or list |
| `config` | `Config` or dict — Streamlit config sections |
| `query_params` | `QueryParams` subclass for typed URL params |

**Methods:**

| Method | Description |
|---|---|
| `app.render()` | Run the full render cycle |
| `app.render_page(root)` | Render a page through the active router |
| `app.create_shared_state(name, spec)` | Declare a session-scoped shared state |
| `app.create_local_store(name, schema)` | Declare a browser-persisted localStorage namespace |
| `App.get_local_store(name)` | Retrieve an existing localStorage namespace |
| `App.clear_local_store(name)` | Delete a localStorage namespace from the browser |
| `app.set_theme(theme)` / `app.save_theme()` | Update / persist theme |
| `app.set_css(css)` | Update CSS |
| `app.set_config(config)` / `app.save_config()` | Update / persist config |
| `app.rerun(scope, wait)` | Request a scoped rerun |
| `app.wait(delay, scope)` | Request a delay before rerun |
| `app.stop()` | Stop script execution |
| `app.login()` / `app.logout()` | Streamlit Cloud auth |
| `app.connection(name, type)` | Create a Streamlit connection |
| `app.params` | Typed query params proxy |
| `app.user` | Current user info (`UserInfo` modict) |
| `app.secrets` | Proxy to `st.secrets` |
| `app.request_context` | HTTP headers and cookies (`RequestContext` modict) |
| `App.cache_data` / `App.cache_resource` | Re-exported Streamlit cache decorators |

**App-level state:**

```python
app.state = dict(user="", lang="en")   # before render(), no-op on reruns
get_app().state.user                    # accessible from anywhere
```

**Subclassing:**

```python
class MyApp(App):
    class AppState(State):
        user: str = ""

    def render(self):
        return MyLayout(key="layout")

MyApp(page_title="My App").render()
```

`render()` returns the root of the tree. The framework plumbing (page config, styles, routing, rerun) is handled by the decorator — `render()` is a plain method you can override freely.


[↑ Back to top](#table-of-contents)

---

## Component

Base class for stateful UI building blocks.

```python
class Counter(Component):
    class CounterState(State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="btn", on_click=self.increment)(
            str(self.state.count)
        )
```

**Instance members:** `self.props`, `self.children`, `self.state`, `self.is_mounted`

**Methods:**

| Method | Description |
|---|---|
| `set_state(other, **kwargs)` | Update state (dict, State, or kwargs) |
| `sync_state(key)` | Returns `fn(value)` that writes into `self.state[key]` |

**Lifecycle hooks** (override as needed):

| Hook | When |
|---|---|
| `component_did_mount()` | Fiber first created |
| `component_did_update(prev_state)` | State changed since last cycle |
| `component_did_unmount()` | Component removed from tree |

**Callbacks** support two signatures:

```python
def on_change(self, value):  # receives widget value
def on_click(self):          # no value needed
```


[↑ Back to top](#table-of-contents)

---

## Element

Terminal node that renders a Streamlit widget.

```python
class my_widget(Element):
    _default_output_prop = "value"  # auto get_output

    def render(self):
        st.my_widget(widget_child("label"), key=widget_key(), ...)
```

`render()` must return `None`.  Widget output exposed via `state.output`.
Container handles exposed via `state.handle`.


[↑ Back to top](#table-of-contents)

---

## State

Local component state — persists across reruns via fibers.

```python
class CounterState(State):
    count: int = 0
    label: str = "clicks"
```

Or inline: `self.state = dict(count=0)`


[↑ Back to top](#table-of-contents)

---

## Props

Immutable input data. Keys are optional (auto-generated if omitted).

```python
class CardProps(Props):
    _config = modict.config(extra="forbid")
    title: str = "Untitled"
    bordered: bool = True
```


[↑ Back to top](#table-of-contents)

---

## Functional Components

```python
@component
def Greeting(props):
    state = use_state(name="world")
    return text_input(key="name", value=state.name,
                      on_change=lambda v: state.update(name=v))("Name")
```

Typed props via annotation: `def Badge(props: BadgeProps):`


[↑ Back to top](#table-of-contents)

---

## Hooks

All hooks must be called during render, always in the same order.

| Hook | Purpose |
|---|---|
| `use_state(other, **kwargs)` | Local state for functional components |
| `use_context(context)` | Read nearest provider value |
| `use_memo(factory, deps)` | Memoize computed value |
| `use_effect(effect, deps)` | Post-render side effects with cleanup |
| `use_ref(initial)` | Mutable ref that persists without reruns |
| `use_callback(fn, deps)` | Memoize callback identity |
| `use_previous(value, initial)` | Value from previous render |
| `use_id()` | Stable per-hook identifier |

**Deps semantics:** `None` → every render. `[]` → once. `[x, y]` → when x or y changes.


[↑ Back to top](#table-of-contents)

---

## Context

Tree-scoped ambient values without prop drilling.

```python
class ThemeData(ContextData):
    mode: str = "light"

ThemeContext = create_context(ThemeData())

# Provider wraps a subtree
ThemeContext.Provider(key="theme", data={"mode": "dark"})(
    MyComponent(key="child")
)

# Consumer reads from nearest provider
theme = use_context(ThemeContext)  # theme.mode == "dark"
```


[↑ Back to top](#table-of-contents)

---

## Ref and Navigation

Every component is a cursor into its subtree. Navigate children by attribute — each access returns a **Ref** (lightweight path-based handle):

```python
class Dashboard(Component):

    def capture(self):
        # Navigate to children — each returns a Ref
        name = self.form.name.state().output     # read an element's widget value
        count = self.counter.state().count        # read a component's state

    def load(self):
        self.page.results(                        # override children from a callback
            metric(key="n", label="Rows", value=1234),
        )

    def clear(self):
        self.page.results.reset()                 # revert to initial children
```

**Full navigation API:**

```python
self.ref              # Ref to this component
self.parent           # Ref to the parent
self.root             # Ref to the App (tree root)
self.page.results     # Ref to any descendant (attribute chain)
self["page"]["results"]  # same via __getitem__
```

**Ref methods:**

| Method | Description |
|---|---|
| `ref.state()` | Read the node's current state |
| `ref(*children, **props)` | Override children and/or props on the fiber |
| `ref.reset()` | Clear all overrides — revert to parent-passed values |
| `ref.reset_widget()` | Reset an Element's widget value in session_state |
| `ref.parent` | Ref to the parent node |
| `ref.handle` | Streamlit container handle (layout elements) |

**Explicit `Ref()` + `ref=` prop** — use when the accessor is not an ancestor (e.g. sibling to sibling):

```python
ref = Ref()
text_input(key="name", ref=ref)("Name")

# Later, in a callback:
ref.state().output   # read the widget value
```


[↑ Back to top](#table-of-contents)

---

## Access API

Low-level path-based state access — prefer `self.child.state()` for hierarchical access.

| Function | Description |
|---|---|
| `get_state(path_or_ref)` | Read Component or Element state |
| `set_state(path_or_ref, other, **kwargs)` | Update Component state |
| `reset_element(path_or_ref)` | Clear and recreate an Element widget |

All accept a path string, `Ref`, or `None` (current context).


[↑ Back to top](#table-of-contents)

---

## Fragment

Composable re-render boundaries.

```python
from st_components.elements import fragment

# Transparent grouping (default)
fragment(key="grp")(child_a, child_b)

# Scoped re-rendering
fragment(key="live", scoped=True, run_every="2s")(
    LiveChart(key="chart"),
)
```

| Prop | Default | Description |
|---|---|---|
| `scoped` | `False` | Wraps in `st.fragment()` when True |
| `run_every` | `None` | Auto-refresh interval (scoped only) |

Nested fragments re-render independently.


[↑ Back to top](#table-of-contents)

---

## Column / Tab

Named layout nodes for precise tree scoping.

```python
columns(key="grid")(
    column(key="filters")(FilterPanel(key="f")),
    column(key="data")(DataTable(key="t")),
)

tabs(key="nav")(
    tab(key="overview", label="Overview")(OverviewPanel(key="p")),
    tab(key="details", label="Details")(DetailsPanel(key="p")),
)
```

Without explicit `column`/`tab`, children get auto-scoped as `col_0`/`tab_0`.


[↑ Back to top](#table-of-contents)

---

## Scoped Rerun

`rerun()` and `wait()` automatically target the current fragment scope.

```python
from st_components.core.rerun import rerun, wait

rerun()                    # current scope (fragment or app)
rerun(scope="app")         # force app scope
rerun(wait=1.5)            # delay before rerun
wait(1.5)                  # delay without triggering a rerun
```

Each scoped fragment has its own timeline — delays don't interfere across scopes.


[↑ Back to top](#table-of-contents)

---

## Shared State

Session-scoped, in-memory state shared across components.

```python
class WorkspaceState(State):
    team: str = "Core"
    focus: int = 7

app.create_shared_state("workspace", WorkspaceState)
ws = get_shared_state("workspace")
ws.team = "Platform"
```


[↑ Back to top](#table-of-contents)

---

## Local Storage

Browser-persisted state via `localStorage`, typed through modict.

```python
class UserPrefs(LocalStore):
    theme: str = "light"
    font_size: int = 14

app.create_local_store("prefs", UserPrefs)

# Later, anywhere:
prefs = App.get_local_store("prefs")
prefs.theme = "dark"        # persists in browser
prefs.font_size              # 14 (coerced from JSON)

App.clear_local_store("prefs")   # delete from browser
```

| Function | Description |
|---|---|
| `app.create_local_store(name, schema)` | Declare a typed localStorage namespace |
| `App.get_local_store(name)` | Retrieve an existing namespace (raises if not declared) |
| `App.clear_local_store(name)` | Delete namespace from browser localStorage |
| `get_local_store(name)` | Module-level alias for `App.get_local_store` |


[↑ Back to top](#table-of-contents)

---

## Query Params

Typed URL query parameters.

```python
class PageParams(QueryParams):
    page: str = "home"
    debug: bool = False
    limit: int = 20

app = App(query_params=PageParams)
app.params.page          # from URL, coerced to str
app.params.debug = True  # updates URL
app.params.clear()       # reset to defaults
```


[↑ Back to top](#table-of-contents)

---

## Streamlit APIs

Exposed on `App` for consistent access:

| API | Access | Returns |
|---|---|---|
| Secrets | `app.secrets.key` | Value from `.streamlit/secrets.toml` |
| User | `app.user` | `UserInfo` modict (`email`, `name`, `is_logged_in`) |
| Auth | `app.login()` / `app.logout()` | Streamlit Cloud auth |
| Context | `app.request_context` | `RequestContext` modict (`headers`, `cookies`) |
| Stop | `app.stop()` | Halts script execution |
| Connection | `app.connection(name, type)` | Streamlit connection |
| Cache | `@App.cache_data` / `@App.cache_resource` | Streamlit cache decorators |

### play_audio

Invisible audio autoplay from anywhere:

```python
from st_components.elements.media import play_audio

play_audio(tts_bytes)                    # bytes
play_audio("sounds/alert.mp3")           # file path
play_audio(audio, format="opus", volume=0.5)
play_audio(audio, wait=2.0)             # delay via rerun.wait()
```


[↑ Back to top](#table-of-contents)

---

## Flow Helpers

Conditional rendering with state preservation.

| Helper | Description |
|---|---|
| `Conditional(condition=...)` | Show child 1 or child 2 |
| `KeepAlive(active=...)` | Hide child without destroying fiber |
| `Case(case=int)` | Select child by index |
| `Switch(value=...)` + `Match(when=...)` + `Default()` | Pattern matching |
| `ErrorBoundary(fallback=...)` | Catch render errors in children |

Hidden branches keep their fibers alive — state survives.

### ErrorBoundary

Catches exceptions in child render and displays a fallback:

```python
from st_components.builtins import ErrorBoundary

ErrorBoundary(key="safe")(
    RiskyComponent(key="risky"),
)

# Custom fallback (callable receives the error):
ErrorBoundary(key="safe", fallback=lambda e: f"Error: {e}")(...)

# State exposes the captured error:
state = get_state("app.safe")
if state.error is not None:
    log(state.error, state.error_traceback)
```

| Prop | Description |
|---|---|
| `fallback` | Component, string, or `callable(error)`. Default: `st.error()` + traceback. |

| State field | Description |
|---|---|
| `error` | The caught exception, or `None` |
| `error_traceback` | Formatted traceback string, or `None` |


[↑ Back to top](#table-of-contents)

---

## Router / Page

Multipage navigation inside the component tree.

```python
App(
    Router(position="top")(
        Page(key="home", nav_title="Home", default=True)(
            HomePage(key="root")
        ),
        Page(key="report", nav_title="Report")(
            "pages/report.py"  # file-backed
        ),
    )
).render()
```


[↑ Back to top](#table-of-contents)

---

## Theming

`Theme` holds dual palettes (`light` / `dark`) and shared settings.
`color_mode` on `App` selects the active palette at runtime.

```python
theme = Theme(
    font="monospace",
    light=ThemeSection(primaryColor="#2dd4bf", backgroundColor="#fafafa"),
    dark=ThemeSection(primaryColor="#5eead4", backgroundColor="#0e1117"),
)
app = App(theme=theme, color_mode="dark", css="body { font-size: 16px; }")

# Runtime update
app.set_params(color_mode="light")
app.set_theme(Theme(light=ThemeSection(primaryColor="#ff0000")))
app.save_theme()  # persists to .streamlit/stc-config.toml

# Built-in editor
ThemeEditorButton(key="edit")("Edit theme")
```


[↑ Back to top](#table-of-contents)

---

## Elements Catalog

All Streamlit widgets are wrapped in `st_components.elements`:

| Category | Elements |
|---|---|
| **Text** | `title`, `header`, `subheader`, `caption`, `text`, `markdown`, `code`, `latex`, `divider`, `badge`, `space` |
| **Input** | `button`, `download_button`, `link_button`, `form_submit_button`, `checkbox`, `toggle`, `radio`, `selectbox`, `multiselect`, `slider`, `select_slider`, `text_input`, `number_input`, `text_area`, `date_input`, `datetime_input`, `time_input`, `color_picker`, `file_uploader`, `camera_input`, `audio_input`, `chat_input`, `menu_button`, `pills`, `segmented_control`, `data_editor`, `feedback` |
| **Layout** | `container`, `columns`, `column`, `tabs`, `tab`, `form`, `fragment`, `expander`, `popover`, `sidebar`, `empty`, `dialog`, `chat_message`, `status` |
| **Display** | `write`, `dataframe`, `table`, `metric`, `json`, `html`, `iframe`, `pdf`, `exception`, `help`, `page_link`, `logo`, `write_stream` |
| **Charts** | `area_chart`, `bar_chart`, `line_chart`, `scatter_chart`, `altair_chart`, `plotly_chart`, `vega_lite_chart`, `pydeck_chart`, `bokeh_chart`, `pyplot`, `map`, `graphviz_chart` |
| **Media** | `image`, `audio`, `video`, `play_audio` |
| **Feedback** | `success`, `info`, `warning`, `error`, `toast`, `balloons`, `snow`, `spinner`, `progress` |


[↑ Back to top](#table-of-contents)

---

## Writing Custom Elements

**Quick path** — `element_factory`:

```python
text_input = element_factory(st.text_input,
    child_prop="label", callback_prop="on_change", default_prop="value")
```

**Full path** — subclass `Element`:

```python
class my_widget(Element):
    _default_output_prop = "value"

    def __init__(self, *, key, value="", on_change=None, **kw):
        Element.__init__(self, key=key, value=value, on_change=on_change, **kw)

    def render(self):
        st.my_widget(widget_child("label"), key=widget_key(),
                     on_change=widget_callback(), **widget_props("label", "on_change"))
```

Helper imports from `st_components.elements.factory`:
`Element`, `element_factory`, `callback`, `widget_callback`, `widget_child`, `widget_key`, `widget_output`, `widget_props`, `render_handle`, `get_render_target`


[↑ Back to top](#table-of-contents)

---

## Fiber (Internals)

A Fiber is the persistent record that gives a component continuity across reruns.

| Field | Description |
|---|---|
| `state` | Component's local state |
| `previous_state` | Snapshot from last cycle (change detection) |
| `component_id` | Links fiber to current Python instance |
| `hooks` | Ordered list of HookSlot entries |
| `overrides` | Props/children overrides set via `ref(...)` from callbacks |
| `keep_alive` | Prevents unmount when hidden by flow helpers |

**Render cycle:** `begin_render_cycle()` → components render and mark fibers → `end_render_cycle()` unmounts stale fibers, fires lifecycle hooks, flushes effects.

Path derivation is structural: `App > container("home") > Counter("c1")` → `app.home.c1`.

[↑ Back to top](#table-of-contents)
