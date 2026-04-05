"""
Typed state and props for functional components.

Demonstrates:
- use_state() with a State instance instead of kwargs
- @component with a typed Props annotation
- combining both in a single component
"""
from modict import modict

from st_components import App, component, State, use_state
from st_components.core.models import Props
from st_components.elements import (
    button, code, columns, container, divider, markdown, metric, subheader, text_input,
)

from examples._source import source_view


# --- 1. use_state with a State instance ---
# Pass a State subclass instance to use_state() instead of flat kwargs.
# The instance carries types, defaults, and is preserved as-is on first render.

class CounterState(State):
    count: int = 0
    step: int = 1


@component
def Counter(props):
    state = use_state(CounterState())

    def increment():
        state.count += state.step

    return columns(key="row")(
        metric(key="count", label="Count", value=state.count),
        button(key="inc", on_click=increment)(f"+ {state.step}"),
    )


# --- 2. @component with a typed Props annotation ---
# Annotate the props parameter with a Props subclass.
# The framework uses it to cast and validate props at instantiation.

class BadgeProps(Props):
    label: str = "badge"
    color: str = "gray"


@component
def Badge(props: BadgeProps):
    return markdown(key="body")(f":{props.color}[**{props.label}**]")


# --- 3. Combining both ---
# A typed Props annotation controls inputs, use_state() controls internal state.

class CardProps(Props):
    _config = modict.config(extra="ignore")
    title: str = "Untitled"


class CardState(State):
    open: bool = False
    views: int = 0


@component
def Card(props: CardProps):
    state = use_state(CardState())

    def toggle():
        state.open = not state.open
        state.views += 1

    label = "▾ Hide" if state.open else "▸ Show"
    return container(key="box", border=True)(
        columns(key="header")(
            markdown(key="title")(f"**{props.title}**"),
            button(key="toggle", on_click=toggle)(label),
            metric(key="views", label="Views", value=state.views),
        ),
        markdown(key="body")("Content is visible.") if state.open else None,
    )


App()(
    container(key="page")(
        subheader(key="h1")("1. use_state with a State instance"),
        markdown(key="desc1")(
            "Pass a `State` subclass instance to `use_state()`. "
            "Types and defaults are declared on the class, not scattered across kwargs."
        ),
        Counter(key="counter"),
        code(key="code1", language="python")(
            "class CounterState(State):\n"
            "    count: int = 0\n"
            "    step: int = 1\n\n"
            "@component\n"
            "def Counter(props):\n"
            "    state = use_state(CounterState())\n"
            "    ..."
        ),
        divider(key="d1"),
        subheader(key="h2")("2. Typed Props annotation"),
        markdown(key="desc2")(
            "Annotate `props` with a `Props` subclass. "
            "The framework uses it to cast props at instantiation — defaults, coercion, and schema constraints all apply."
        ),
        Badge(key="badge_default"),
        Badge(key="badge_custom", label="active", color="green"),
        code(key="code2", language="python")(
            "class BadgeProps(Props):\n"
            "    label: str = \"badge\"\n"
            "    color: str = \"gray\"\n\n"
            "@component\n"
            "def Badge(props: BadgeProps):\n"
            "    return markdown(key=\"body\")(f\":{props.color}[**{props.label}**]\")\n\n"
            "Badge(key=\"b\")                           # label=\"badge\", color=\"gray\"\n"
            "Badge(key=\"b\", label=\"active\", color=\"green\")"
        ),
        divider(key="d2"),
        subheader(key="h3")("3. Combining both"),
        markdown(key="desc3")(
            "Typed Props control the public interface. "
            "`use_state()` with a State instance controls internal state. "
            "The two are independent and compose naturally."
        ),
        Card(key="card_a", title="Card A", tooltip="ignored by extra=ignore"),
        Card(key="card_b", title="Card B"),
        code(key="code3", language="python")(
            "class CardProps(Props):\n"
            "    _config = modict.config(extra=\"ignore\")\n"
            "    title: str = \"Untitled\"\n\n"
            "class CardState(State):\n"
            "    open: bool = False\n"
            "    views: int = 0\n\n"
            "@component\n"
            "def Card(props: CardProps):\n"
            "    state = use_state(CardState())\n"
            "    ..."
        ),
        source_view(__file__),
    )
).render()
