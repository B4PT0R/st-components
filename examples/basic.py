import streamlit as st
from st_components import Component, render, KEY, fibers, App
from st_components.elements import button, container, columns


class Counter(Component):

    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(count=self.props.get('initial_count', 0))

    def increment(self):
        self.state.count += 1

    def get_type(self):
        return "secondary" if self.state.count < 5 else "primary"

    def render(self):
        return button(key="button", on_click=self.increment, type=self.get_type())(
            f"You clicked {self.state.count} times",
        )


class DoubleCounter(Component):

    def render(self):
        return container(key="container")(
            columns(key="columns")(
                Counter(key="counter_1"),
                Counter(key="counter_2")
            )
        )

app = App()(
    container(key="main_container")(
        DoubleCounter(key="double_counter_1"),
        "Hello!",
        DoubleCounter(key="double_counter_2"),
    )
)

app.render()

st.write(fibers())
