"""
05 - Functional Components

Shows the @component decorator and use_state() hook as a lighter
alternative to class-based components.
Introduces: @component, use_state, props object.
"""
import st_components as stc
from st_components.elements import (
    button, caption, code, columns, container, divider, markdown, metric,
    text_input,
)

from examples._source import source_view


@stc.component
def Counter(props):
    """Functional counter — state lives in a hook, not in a class."""
    state = stc.use_state(count=0)

    def increment():
        state.count += 1

    return container(key="card", border=True)(
        metric(key="val", label=props.get("label", "Count"), value=state.count),
        button(key="inc", on_click=increment, type="primary")("+1"),
    )


@stc.component
def GreetingForm(props):
    """Demonstrates the props object and two-way binding with use_state."""
    state = stc.use_state(name=props.get("initial", "world"))

    return container(key="card", border=True)(
        text_input(key="name", value=state.name,
                   on_change=lambda v: state.update(name=v))("Your name"),
        markdown(key="greeting")(f"Hello, **{state.name}**!"),
    )


@stc.component
def FunctionalDemo(props):
    return container(key="page")(
        markdown(key="intro")(
            "## Functional Components\n\n"
            "The `@component` decorator turns a plain function into a Component. "
            "Use `use_state()` to own local state — same persistence, less boilerplate.\n\n"
            "**Class vs functional — same power, different style:**\n\n"
            "| Class | Functional |\n"
            "|---|---|\n"
            "| `class Counter(Component):` | `@component` |\n"
            "| `class State: count = 0` | `use_state(count=0)` |\n"
            "| `self.state.count` | `state.count` |\n"
            "| `self.props.label` | `props.label` |\n"
        ),
        divider(key="d1"),
        markdown(key="h1")("### Stateful counter"),
        markdown(key="desc1")(
            "Each counter owns its state through `use_state()`. "
            "Independent instances, same function."
        ),
        columns(key="counters")(
            Counter(key="a", label="Counter A"),
            Counter(key="b", label="Counter B"),
        ),
        code(key="code1", language="python")(
            "@component\n"
            "def Counter(props):\n"
            "    state = use_state(count=0)\n"
            "\n"
            "    def increment():\n"
            "        state.count += 1\n"
            "\n"
            "    return button(key=\"inc\", on_click=increment)(str(state.count))"
        ),
        divider(key="d2"),
        markdown(key="h2")("### Two-way binding"),
        markdown(key="desc2")(
            "The `props` object is a dict-like with attribute access. "
            "Use it to pass initial values, then let state take over."
        ),
        GreetingForm(key="greet", initial="Ada"),
        code(key="code2", language="python")(
            "@component\n"
            "def GreetingForm(props):\n"
            "    state = use_state(name=props.get(\"initial\", \"world\"))\n"
            "    return text_input(key=\"name\", value=state.name,\n"
            "                      on_change=lambda v: state.update(name=v))(\"Name\")"
        ),
        divider(key="d3"),
        markdown(key="h3")("### When to use which?"),
        markdown(key="tip")(
            "- **Functional** — great for leaf components, quick prototypes, and hooks-heavy logic.\n"
            "- **Class** — better when you need lifecycle hooks (`component_did_mount`), "
            "multiple methods, or complex state management."
        ),
        source_view(__file__),
    )


stc.App(FunctionalDemo(), page_title="05 - Functional").render()
