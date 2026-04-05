from st_components import Component, App
from st_components.elements import button


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


App(root=Counter(key="counter")).render()
