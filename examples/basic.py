from st_components import Component, App
from st_components.elements import button, container

from examples._source import source_view


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=0)

    def increment(self):
        self.state.count += 1

    def render(self):
        return button(key="btn", on_click=self.increment)(
            f"Clicked {self.state.count} times"
        )


class BasicDemo(Component):
    def render(self):
        return container(key="page")(
            Counter(key="counter"),
            source_view(__file__),
        )


App()(BasicDemo(key="app")).render()
