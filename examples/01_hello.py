"""
01 - Hello st-components

The simplest possible example: a button that counts clicks.
Introduces: Component, State, render, App.
"""
import st_components as stc
from st_components.elements import button, container, markdown, metric

from examples._source import source_view


class Counter(stc.Component):
    """A button that remembers how many times it was clicked."""

    class CounterState(stc.State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="btn", on_click=self.increment, type="primary")(
            f"Clicked {self.state.count} times"
        )


class HelloDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Hello st-components\n\n"
                "This is the simplest example: a `Component` with local state.\n\n"
                "- **Component** is the base class for stateful UI building blocks.\n"
                "- **State** declares typed fields with defaults — no `__init__` override needed.\n"
                "- State **persists across reruns** — click the buttons and watch the counts diverge.\n"
                "- Each component has a **key** that identifies it among its siblings."
            ),
            metric(key="label_1", label="Counter A"),
            Counter(key="counter_1"),
            metric(key="label_2", label="Counter B"),
            Counter(key="counter_2"),
            markdown(key="note")(
                "> The two counters are independent instances of the same class. "
                "Each owns its own state through the fiber system."
            ),
            source_view(__file__),
        )


stc.App(HelloDemo(), page_title="01 - Hello").render()
