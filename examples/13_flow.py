"""
09 - Flow Control

Shows conditional rendering with built-in flow components.
Each branch preserves its own state independently.
Introduces: Conditional, KeepAlive, Case, Switch/Match/Default.
"""
import st_components as stc
from st_components.builtins import Case, Conditional, Default, KeepAlive, Match, Switch
from st_components.elements import (
    button, caption, columns, container, divider, markdown, metric,
)

from examples._source import source_view


class CounterBox(stc.Component):
    """Small counter used in every demo — shows that each branch owns its state."""

    class CounterBoxState(stc.State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return container(key="box", border=True)(
            metric(key="val", label=self.props.get("label", "Count"), value=self.state.count),
            button(key="inc", on_click=self.increment, width="stretch")("+1"),
        )


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

class ConditionalDemo(stc.Component):
    class S(stc.State):
        show_primary: bool = True

    def toggle(self):
        self.state.show_primary = not self.state.show_primary

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### Conditional"),
            caption(key="desc")(
                "Shows one of two branches. The hidden branch's state is preserved."
            ),
            button(key="toggle", on_click=self.toggle)(
                "Show fallback" if self.state.show_primary else "Show primary"
            ),
            Conditional(key="cond", condition=self.state.show_primary)(
                CounterBox(key="primary", label="Primary"),
                CounterBox(key="fallback", label="Fallback"),
            ),
            caption(key="tip")(
                "Increment both counters, then toggle — their values survive."
            ),
        )


class KeepAliveDemo(stc.Component):
    class S(stc.State):
        active: bool = True

    def toggle(self):
        self.state.active = not self.state.active

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### KeepAlive"),
            caption(key="desc")(
                "Hides the child without destroying its fiber. State survives even when hidden."
            ),
            button(key="toggle", on_click=self.toggle)(
                "Hide" if self.state.active else "Show"
            ),
            KeepAlive(key="ka", active=self.state.active)(
                CounterBox(key="child", label="Cached counter"),
            ),
        )


class CaseDemo(stc.Component):
    class S(stc.State):
        index: int = 0

    def render(self):
        labels = ["Alpha", "Beta", "Gamma"]
        return container(key="panel", border=True)(
            markdown(key="h")("### Case"),
            caption(key="desc")(
                "Selects one child by index. Other branches are preserved."
            ),
            columns(key="btns")(
                *[button(key=f"btn_{i}", on_click=lambda i=i: self.state.update(index=i),
                         type="primary" if self.state.index == i else "secondary")(label)
                  for i, label in enumerate(labels)]
            ),
            Case(key="case", case=self.state.index)(
                *[CounterBox(key=f"panel_{i}", label=label) for i, label in enumerate(labels)]
            ),
        )


class SwitchDemo(stc.Component):
    class S(stc.State):
        status: str = "loading"

    def render(self):
        statuses = ["loading", "ready", "error"]
        return container(key="panel", border=True)(
            markdown(key="h")("### Switch / Match / Default"),
            caption(key="desc")(
                "Pattern-matches a value against Match(when=...) branches, "
                "with an optional Default fallback."
            ),
            columns(key="btns")(
                *[button(key=s, on_click=lambda s=s: self.state.update(status=s),
                         type="primary" if self.state.status == s else "secondary")(s)
                  for s in statuses]
            ),
            Switch(key="switch", value=self.state.status)(
                Match(key="loading", when="loading")(CounterBox(key="p", label="Loading...")),
                Match(key="ready", when="ready")(CounterBox(key="p", label="Ready")),
                Default(key="default")(CounterBox(key="p", label="Unknown status")),
            ),
        )


class FlowDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Flow Control\n\n"
                "Built-in components for conditional rendering. "
                "Each branch preserves its own state independently.\n\n"
                "**What to try:** increment a counter in one branch, switch to another, "
                "then come back — the value is still there."
            ),
            divider(key="d"),
            ConditionalDemo(key="conditional"),
            KeepAliveDemo(key="keepalive"),
            CaseDemo(key="case"),
            SwitchDemo(key="switch"),
            source_view(__file__),
        )


stc.App(page_title="09 - Flow")(FlowDemo()).render()
