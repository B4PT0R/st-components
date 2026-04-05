import datetime
from st_components import App, Component, Ref, get_component_state, get_element_value
from st_components.elements import (
    button, caption, code, columns, container, divider, expander, header, info,
    json, markdown, metric, sidebar, slider, subheader, success, tabs, text,
    text_area, text_input, title, toggle, warning,
)

from examples._source import source_view


class CounterCard(Component):
    """Simple stateful component used across the tutorial."""

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=self.props.get("initial", 0))

    def increment(self):
        self.state.value += 1

    def decrement(self):
        self.state.value = max(0, self.state.value - 1)

    def reset(self):
        self.state.value = 0

    def render(self):
        return container(key="card", border=True)(
            metric(key="metric", label=self.props.label, value=self.state.value),
            columns(key="actions")(
                button(key="dec", on_click=self.decrement, disabled=self.state.value == 0, width="stretch")("−"),
                button(key="inc", on_click=self.increment, width="stretch")("+"),
                button(key="rst", on_click=self.reset, width="stretch")("↺"),
            ),
        )


class IntroCard(Component):
    def render(self):
        today = datetime.date.today().strftime("%A, %B %d")
        return container(key="intro", border=True)(
            title(key="title")("st-components tutorial dashboard"),
            caption(key="date")(today),
            markdown(key="body")(
                "`st-components` gives Streamlit a small component model:\n\n"
                "- `Component` keeps local state across reruns.\n"
                "- `Element` wraps Streamlit primitives.\n"
                "- `on_change` handlers receive the current widget value.\n"
                "- `Ref()` lets you reach a component or stateful element later without hardcoding full paths."
            ),
            info(key="tip")(
                "Use the tabs below in order. Each section is interactive and illustrates one part of the API."
            ),
        )


class LocalStateDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="h")("1. Local component state"),
            caption(key="c")(
                "Each CounterCard is recreated every rerun, but its state is restored from its fiber."
            ),
            columns(key="cards")(
                CounterCard(key="tasks", label="Tasks done", initial=2),
                CounterCard(key="reviews", label="PR reviews", initial=1),
                CounterCard(key="bugs", label="Bugs fixed", initial=0),
            ),
            code(key="snippet", language="python")(
                "class CounterCard(Component):\n"
                "    def __init__(self, **props):\n"
                "        super().__init__(**props)\n"
                "        self.state = dict(value=0)\n"
                "\n"
                "    def increment(self):\n"
                "        self.state.value += 1"
            ),
        )


class ElementValueDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(
            task="Prototype refs",
            focus=7,
            blocked=False,
            notes="",
            last_event="Waiting for a widget change",
        )

    def sync_task(self, value):
        self.state.task = value
        self.state.last_event = f"task -> {value!r}"

    def sync_focus(self, value):
        self.state.focus = value
        self.state.last_event = f"focus -> {value}"

    def sync_blocked(self, value):
        self.state.blocked = value
        self.state.last_event = f"blocked -> {value}"

    def sync_notes(self, value):
        self.state.notes = value
        self.state.last_event = f"notes -> {len(value)} chars"

    def render(self):
        snapshot = {
            "task": self.state.task,
            "focus": self.state.focus,
            "blocked": self.state.blocked,
            "notes": self.state.notes,
            "last_event": self.state.last_event,
        }

        return container(key="panel", border=True)(
            subheader(key="h")("2. Widget values in callbacks"),
            caption(key="c")(
                "Stateful Elements pass their current value to `on_change`, so simple widget-to-state sync stays explicit and lightweight."
            ),
            text_input(key="task", value=self.state.task, on_change=self.sync_task)("Current task"),
            slider(key="focus", min_value=0, max_value=10, value=self.state.focus, on_change=self.sync_focus)("Focus level"),
            toggle(key="blocked", value=self.state.blocked, on_change=self.sync_blocked)("Blocked right now"),
            text_area(
                key="notes",
                value=self.state.notes,
                height=120,
                on_change=self.sync_notes,
                placeholder="Type here to update component state from a widget callback.",
            )("Notes"),
            columns(key="metrics")(
                metric(key="task_metric", label="Task", value=self.state.task or "None"),
                metric(key="focus_metric", label="Focus", value=self.state.focus),
                metric(key="blocked_metric", label="Blocked", value="Yes" if self.state.blocked else "No"),
            ),
            success(key="hint")(
                f"Last callback: {self.state.last_event}"
            ),
            json(key="snapshot")(snapshot),
            code(key="snippet", language="python")(
                "def sync_task(self, value):\n"
                "    self.state.task = value\n"
                "\n"
                "def render(self):\n"
                "    return text_input(key=\"task\", on_change=self.sync_task)(\"Current task\")"
            ),
        )


class RefInspectorDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.name_ref = Ref()
        self.notes_ref = Ref()
        self.counter_ref = Ref()
        self.state = dict(
            name="Shipping tutorial dashboard",
            notes="Refs resolve to stable logical paths.",
            snapshot={},
        )

    def capture_refs(self):
        self.state.snapshot = {
            "name_ref_path": self.name_ref.path,
            "name_ref_value": get_element_value(self.name_ref),
            "notes_ref_path": self.notes_ref.path,
            "notes_ref_value": get_element_value(self.notes_ref),
            "counter_ref_path": self.counter_ref.path,
            "counter_ref_state": dict(get_component_state(self.counter_ref)),
        }

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="h")("3. Reach things later with Ref()"),
            caption(key="c")(
                "Refs store logical paths, not Python instances. Render first, then pass them to helpers like get_element_value(...) or get_component_state(...)."
            ),
            text_input(
                key="name",
                ref=self.name_ref,
                value=self.state.name,
                on_change=self.sync_state("name"),
            )("Title tracked by ref"),
            text_area(
                key="notes",
                ref=self.notes_ref,
                value=self.state.notes,
                height=100,
                on_change=self.sync_state("notes"),
            )("Notes tracked by ref"),
            CounterCard(key="counter", ref=self.counter_ref, label="Counter reached through ref", initial=3),
            button(key="read_refs", on_click=self.capture_refs, type="primary")("Read refs now"),
            json(key="snapshot")(self.state.snapshot or {"status": "Click 'Read refs now' after changing the inputs or counter."}),
            code(key="snippet", language="python")(
                "name_ref = Ref()\n"
                "counter_ref = Ref()\n"
                "\n"
                "text_input(key=\"name\", ref=name_ref)(\"Name\")\n"
                "CounterCard(key=\"counter\", ref=counter_ref)\n"
                "\n"
                "snapshot = {\n"
                "    \"name\": get_element_value(name_ref),\n"
                "    \"count\": get_component_state(counter_ref).value,\n"
                "}"
            ),
        )


class CompositionDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(saved=False)

    def mark_dirty(self, value):
        self.state.saved = False

    def mark_saved(self):
        self.state.saved = True

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="h")("4. Compose simple Elements into richer Components"),
            caption(key="c")(
                "The library stays small by making each base Element wrap one Streamlit primitive. Rich behavior lives in Components."
            ),
            expander(key="notes_box", label="Mini editor built by composition", expanded=True)(
                text_area(
                    key="draft",
                    height=140,
                    placeholder="Write something, then click save.",
                    on_change=self.mark_dirty,
                )("Draft"),
                columns(key="row")(
                    button(key="save", on_click=self.mark_saved, type="primary")("Save"),
                    success(key="saved")("Saved") if self.state.saved else warning(key="dirty")("Unsaved changes"),
                ),
            ),
            markdown(key="body")(
                "This mini editor is not a special built-in widget. It is just:\n\n"
                "- `text_area`\n"
                "- `button`\n"
                "- feedback Elements\n"
                "- a small `Component` holding local state"
            ),
        )


class SidebarGuide(Component):
    def render(self):
        return sidebar(key="sidebar")(
            header(key="h")("st-components"),
            caption(key="c")("React-like patterns for Streamlit"),
            divider(key="d1"),
            markdown(key="agenda")(
                "This dashboard demonstrates:\n\n"
                "1. local component state\n"
                "2. widget values in callbacks\n"
                "3. `Ref()`\n"
                "4. composition of simple Elements"
            ),
            divider(key="d2"),
            text(key="rule")("Mental model"),
            markdown(key="model")(
                "- Components own state through fibers.\n"
                "- Widgets keep their value in `st.session_state`.\n"
                "- Refs point to paths, not instances."
            ),
        )


class Dashboard(Component):
    def render(self):
        return container(key="page")(
            SidebarGuide(key="guide"),
            IntroCard(key="intro"),
            tabs(key="sections", tabs=["State", "Widget values", "Refs", "Composition"])(
                LocalStateDemo(key="state_demo"),
                ElementValueDemo(key="element_demo"),
                RefInspectorDemo(key="ref_demo"),
                CompositionDemo(key="composition_demo"),
            ),
            source_view(__file__),
        )


App(root=Dashboard(key="dashboard")).render()
