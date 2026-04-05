"""
Typed state schema with nested State subclasses.

Demonstrates three patterns:
- declaring initial state as a typed nested class (no __init__ needed)
- multi-field structured state
- type validation on state assignment
"""
from modict import modict

from st_components import App, Component, State
from st_components.elements import (
    button, code, columns, container, divider, error, markdown, metric, subheader,
)

from examples._source import source_view


# --- 1. Basic typed state ---
# A nested State subclass replaces the __init__ override.
# Fields are typed and get default values.

class Counter(Component):

    class CounterState(State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="btn", on_click=self.increment)(
            f"Clicked {self.state.count} times"
        )


# --- 2. Multi-field structured state ---
# Group related state fields with explicit types and defaults.

class ToggleCard(Component):

    class ToggleCardState(State):
        open: bool = False
        visits: int = 0

    def toggle(self):
        self.state.open = not self.state.open
        self.state.visits += 1

    def render(self):
        label = "Hide" if self.state.open else "Show"
        return container(key="card", border=True)(
            columns(key="cols")(
                button(key="toggle", on_click=self.toggle)(label),
                metric(key="visits", label="Opened", value=self.state.visits),
            ),
            markdown(key="body")("Details are visible.") if self.state.open else None,
        )


# --- 3. Type validation ---
# modict raises if you assign a value of the wrong type.

class TypedCounter(Component):

    class TypedCounterState(State):
        count: int = 0

    def set_invalid(self):
        try:
            self.state.count = "not_an_int"
        except Exception as e:
            self.state.count = -1

    def render(self):
        return columns(key="cols")(
            metric(key="count", label="count", value=self.state.count),
            button(key="bad", on_click=self.set_invalid)("Assign wrong type"),
        )


class Demo(Component):

    def render(self):
        # Type error caught at definition time
        try:
            class BadState(State):
                count: int = "not_an_int"
            type_error_display = error(key="miss")("Expected an error but got none.")
        except Exception as e:
            type_error_display = error(key="err_type")(f"Bad default — {e}")

        return container(key="page")(
            subheader(key="h1")("1. Basic typed state"),
            markdown(key="desc1")(
                "A nested `State` subclass declares the initial state. "
                "No `__init__` override needed."
            ),
            Counter(key="counter"),
            code(key="code1", language="python")(
                "class Counter(Component):\n"
                "    class CounterState(State):\n"
                "        count: int = 0\n\n"
                "    def increment(self):\n"
                "        self.state.count += 1\n\n"
                "    def render(self):\n"
                "        return button(key=\"btn\", on_click=self.increment)(\n"
                "            f\"Clicked {self.state.count} times\"\n"
                "        )"
            ),
            divider(key="d1"),
            subheader(key="h2")("2. Multi-field structured state"),
            markdown(key="desc2")(
                "Group related fields with explicit types. "
                "Defaults make the initial shape of the state self-documenting."
            ),
            ToggleCard(key="card"),
            code(key="code2", language="python")(
                "class ToggleCardState(State):\n"
                "    open: bool = False\n"
                "    visits: int = 0"
            ),
            divider(key="d2"),
            subheader(key="h3")("3. Type validation"),
            markdown(key="desc3")(
                "modict raises if a field receives a value of the wrong type — "
                "both at class definition (bad default) and at assignment."
            ),
            type_error_display,
            TypedCounter(key="typed_counter"),
            code(key="code3", language="python")(
                "class BadState(State):\n"
                "    count: int = \"not_an_int\"   # raises at class definition\n\n"
                "state.count = \"oops\"             # raises at assignment"
            ),
            source_view(__file__),
        )


App(root=Demo(key="demo")).render()
