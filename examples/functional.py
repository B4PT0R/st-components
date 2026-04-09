from st_components import App, component, use_state
from st_components.elements import (
    button, caption, code, columns, container, divider, json, markdown, metric,
    subheader, text_input, title,
)

from examples._source import source_view


@component
def Section(props):
    return container(key="box", border=True)(
        subheader(key="title")(props.title),
        *props.children,
    )


@component
def KeyValue(props):
    clean_props = props.exclude("label", "value", "children")
    return container(key="row", **clean_props)(
        markdown(key="label")(f"**{props.label}**"),
        caption(key="value")(str(props.value)),
    )


@component
def Callout(props):
    tone = props.get("tone", "info")
    prefix = {
        "info": "Info",
        "tip": "Tip",
        "warning": "Warning",
    }.get(tone, "Note")
    body = props.children[0] if props.children else ""
    return markdown(key="body")(f"**{prefix}.** {body}")


@component
def FunctionalCounter(props):
    state = use_state(count=props.get("initial", 0))

    def increment(_):
        state.count += 1

    return container(key="box", border=True)(
        metric(key="count", label=props.label, value=state.count),
        button(key="increment", on_click=increment, type="primary")("Increment"),
        caption(key="caption")("State is owned by the function component through use_state()."),
    )


@component
def FunctionalDemo(props):
    state = use_state(name="Baptiste", clicks=0)

    def sync_name(value):
        state.name = value

    def increment(_):
        state.clicks += 1

    snapshot = {
        "name": state.name,
        "clicks": state.clicks,
    }

    return container(key="page")(
        title(key="title")("Functional components example"),
        caption(key="caption")(
            "This file is intentionally 100% functional: even the root component uses `@component` and `use_state()`."
        ),
        divider(key="d1"),
        Section(key="intro", title="What functional components receive")(
            Callout(key="callout", tone="tip")(
                "The decorated function receives a single `props` object with attribute access, `children`, and helpers like `exclude()`."
            ),
            code(key="snippet", language="python")(
                "@component\n"
                "def Callout(props):\n"
                "    return markdown(key=\"body\")(props.children[0])"
            ),
        ),
        Section(key="live", title="Live demo")(
            text_input(
                key="name",
                value=state.name,
                on_change=sync_name,
            )("Name"),
            button(key="increment", on_click=increment, type="primary")("Increment root counter"),
            columns(key="stats")(
                metric(key="name_metric", label="Current name", value=state.name),
                metric(key="clicks_metric", label="Root functional clicks", value=state.clicks),
            ),
            FunctionalCounter(key="functional_counter", label="Nested functional counter", initial=3),
            columns(key="details")(
                KeyValue(key="name_value", label="props.label example", value=state.name),
                KeyValue(key="clicks_value", label="props.value example", value=state.clicks),
            ),
            json(key="snapshot")(snapshot),
        ),
        Section(key="pattern", title="Stateful functional pattern")(
            markdown(key="body")(
                "A functional component can own local state through `use_state()` and still use regular callbacks."
            ),
            code(key="pattern", language="python")(
                "@component\n"
                "def FunctionalCounter(props):\n"
                "    state = use_state(count=0)\n"
                "\n"
                "    def increment(_):\n"
                "        state.count += 1\n"
                "\n"
                "    return button(key=\"inc\", on_click=increment)(...)"
            ),
        ),
        source_view(__file__),
    )


App()(FunctionalDemo(key="app")).render()
