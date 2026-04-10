"""
02 - Component State

Shows how to declare typed state, update it, and see it persist across reruns.
Introduces: State subclass, set_state, state properties, lifecycle.
"""
import st_components as stc
from st_components.elements import (
    button, columns, container, divider, json, markdown, metric,
)

from examples._source import source_view


# ---------------------------------------------------------------------------
# 1. Basic typed state — a nested class replaces the __init__ override
# ---------------------------------------------------------------------------

class StepCounter(stc.Component):
    class StepCounterState(stc.State):
        count: int = 0

    def increment(self):
        self.state.count += self.props.get("step", 1)

    def reset(self):
        self.state.count = 0

    def render(self):
        return container(key="card", border=True)(
            metric(key="value", label=self.props.get("label", "Count"), value=self.state.count),
            columns(key="actions")(
                button(key="inc", on_click=self.increment, type="primary")(
                    f"+{self.props.get('step', 1)}"
                ),
                button(key="rst", on_click=self.reset)("Reset"),
            ),
        )


# ---------------------------------------------------------------------------
# 2. Multi-field state — group related fields together
# ---------------------------------------------------------------------------

class TaskTracker(stc.Component):
    class TaskTrackerState(stc.State):
        done: int = 0
        skipped: int = 0

    def do_task(self):
        self.state.done += 1

    def skip_task(self):
        self.state.skipped += 1

    def render(self):
        total = self.state.done + self.state.skipped
        return container(key="card", border=True)(
            columns(key="metrics")(
                metric(key="done", label="Done", value=self.state.done),
                metric(key="skipped", label="Skipped", value=self.state.skipped),
                metric(key="total", label="Total", value=total),
            ),
            columns(key="actions")(
                button(key="do", on_click=self.do_task, type="primary")("Done"),
                button(key="skip", on_click=self.skip_task)("Skip"),
            ),
        )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

class StateDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Component State\n\n"
                "State is declared as an inner `State` subclass with typed fields and defaults. "
                "It persists across Streamlit reruns automatically.\n\n"
                "**What to try:**\n"
                "- Click the buttons — state updates are reflected instantly.\n"
                "- Reload the page — state survives because it lives in the fiber, not the Python instance."
            ),
            divider(key="d1"),
            markdown(key="h1")("### Basic typed state"),
            markdown(key="desc1")(
                "Each counter uses a `step` prop to control the increment size. "
                "The state class declares a single `count: int = 0` field."
            ),
            columns(key="counters")(
                StepCounter(key="by_1", label="Step = 1", step=1),
                StepCounter(key="by_5", label="Step = 5", step=5),
                StepCounter(key="by_10", label="Step = 10", step=10),
            ),
            divider(key="d2"),
            markdown(key="h2")("### Multi-field state"),
            markdown(key="desc2")(
                "Group related fields in one State class. "
                "Here `done` and `skipped` are two independent counters that derive a `total`."
            ),
            TaskTracker(key="tracker"),
            divider(key="d3"),
            markdown(key="h3")("### Fiber snapshot"),
            markdown(key="desc3")(
                "The JSON below shows the raw fibers — the internal data structure "
                "that keeps your component state alive across reruns."
            ),
            json(key="fibers", expanded=False)(stc.fibers()),
            source_view(__file__),
        )


stc.App(page_title="02 - State")(StateDemo()).render()
