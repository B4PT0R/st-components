from st_components import App, Component, State
from st_components.builtins import Case, Conditional, Default, KeepAlive, Match, Switch
from st_components.elements import button, caption, columns, container, divider, metric, subheader, tabs, title

from examples._source import source_view


class CounterBox(Component):
    class CounterBoxState(State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return container(key="box", border=True)(
            subheader(key="title")(self.props.label),
            metric(key="count", label="count", value=self.state.count),
            button(key="increment", on_click=self.increment)("Increment"),
        )


class ConditionalDemo(Component):
    class ConditionalDemoState(State):
        show: bool = True

    def toggle_show(self):
        self.state.show = not self.state.show

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("Conditional"),
            caption(key="caption")("Conditional(...)(primary, fallback)"),
            button(key="toggle", on_click=self.toggle_show)(
                "Show primary" if not self.state.show else "Show fallback"
            ),
            Conditional(key="conditional", condition=self.state.show)(
                CounterBox(key="primary", label="Primary"),
                CounterBox(key="fallback", label="Fallback"),
            ),
        )


class KeepAliveDemo(Component):
    class KeepAliveDemoState(State):
        active: bool = True

    def toggle_active(self):
        self.state.active = not self.state.active

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("KeepAlive"),
            caption(key="caption")("KeepAlive(...)(child)"),
            button(key="toggle", on_click=self.toggle_active)(
                "Activate panel" if not self.state.active else "Hide panel"
            ),
            KeepAlive(key="keep_alive", active=self.state.active)(
                CounterBox(key="panel", label="Cached panel")
            ),
        )


class CaseDemo(Component):
    class CaseDemoState(State):
        case: int = 0

    def set_case(self, value):
        self.state.case = value

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("Case"),
            caption(key="caption")("Case(...)(child_0, child_1, child_2)"),
            columns(key="controls")(
                button(key="case_0", on_click=lambda: self.set_case(0))("0"),
                button(key="case_1", on_click=lambda: self.set_case(1))("1"),
                button(key="case_2", on_click=lambda: self.set_case(2))("2"),
            ),
            Case(key="case", case=self.state.case)(
                CounterBox(key="first", label="Case 0"),
                CounterBox(key="second", label="Case 1"),
                CounterBox(key="third", label="Case 2"),
            ),
        )


class SwitchDemo(Component):
    class SwitchDemoState(State):
        status: str = "loading"

    def set_status(self, value):
        self.state.status = value

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("Switch"),
            caption(key="caption")("Switch(...)(Match(...), Match(...), Default(...))"),
            columns(key="controls")(
                button(key="loading", on_click=lambda: self.set_status("loading"))("loading"),
                button(key="ready", on_click=lambda: self.set_status("ready"))("ready"),
                button(key="other", on_click=lambda: self.set_status("other"))("other"),
            ),
            Switch(key="switch", value=self.state.status)(
                Match(key="loading", when="loading")(CounterBox(key="panel", label="Loading")),
                Match(key="ready", when="ready")(CounterBox(key="panel", label="Ready")),
                Default(key="default")(CounterBox(key="panel", label="Default")),
            ),
        )


class FlowDemo(Component):
    def render(self):
        return container(key="page")(
            title(key="title")("Flow built-ins"),
            caption(key="caption")("One tab per built-in. Each branch keeps its own local counter."),
            divider(key="divider"),
            tabs(
                key="tabs",
                tabs=["Conditional", "KeepAlive", "Case", "Switch"],
            )(
                ConditionalDemo(key="conditional_demo"),
                KeepAliveDemo(key="keep_alive_demo"),
                CaseDemo(key="case_demo"),
                SwitchDemo(key="switch_demo"),
            ),
            source_view(__file__),
        )


App()(FlowDemo(key="app")).render()
