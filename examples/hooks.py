from st_components import (
    App,
    ContextData,
    component,
    create_context,
    use_callback,
    use_context,
    use_effect,
    use_id,
    use_memo,
    use_previous,
    use_ref,
    use_state,
)
from st_components.elements import (
    button,
    caption,
    code,
    columns,
    container,
    divider,
    json,
    markdown,
    metric,
    subheader,
    text_input,
    title,
)

from examples._source import source_view


class ToneData(ContextData):
    mode: str = "neutral"


ToneContext = create_context(ToneData(mode="neutral"), name="tone")


@component
def Section(props):
    return container(key="box", border=True)(
        subheader(key="title")(props.title),
        *props.children,
    )


@component
def ContextBadge(props):
    tone = use_context(ToneContext)
    return markdown(key="tone")(f"**Active tone from context:** `{tone.mode}`")


@component
def HooksDemo(props):
    state = use_state(name="Ada", count=0)
    tone = use_context(ToneContext)
    render_id = use_id()
    previous_count = use_previous(state.count)
    technical = use_ref({"effect_runs": 0})

    derived = use_memo(
        lambda: {
            "name_upper": state.name.upper(),
            "doubled_count": state.count * 2,
            "summary": f"{state.name} clicked {state.count} times",
        },
        deps=[state.name, state.count],
    )

    def effect():
        technical.current["effect_runs"] += 1

    use_effect(effect, deps=[state.name, state.count])

    increment = use_callback(lambda: state.update(count=state.count + 1), deps=[state.count])
    reset = use_callback(lambda: state.update(count=0), deps=[])

    snapshot = {
        "render_id": render_id,
        "name": state.name,
        "count": state.count,
        "previous_count": previous_count,
        "memoized_summary": derived["summary"],
        "effect_runs": technical.current["effect_runs"],
        "tone": dict(tone),
    }

    return container(key="page")(
        title(key="title")("Hooks example"),
        caption(key="caption")(
            "A compact demo of the main hooks: state, context, memo, effect, ref, callback, previous, and id."
        ),
        divider(key="divider"),
        Section(key="live", title="Live demo")(
            text_input(
                key="name",
                value=state.name,
                on_change=lambda value: state.update(name=value),
            )("Name"),
            columns(key="actions")(
                button(key="increment", on_click=increment, type="primary")("Increment"),
                button(key="reset", on_click=reset)("Reset"),
            ),
            columns(key="metrics")(
                metric(key="count", label="Count", value=state.count),
                metric(key="previous", label="Previous count", value=previous_count if previous_count is not None else "-"),
                metric(key="effect_runs", label="Effect runs", value=technical.current["effect_runs"]),
                metric(key="tone_mode", label="Context tone", value=tone.mode),
            ),
            markdown(key="summary")(f"**Memoized summary:** {derived['summary']}"),
            json(key="snapshot")(snapshot),
        ),
        Section(key="notes", title="What each hook is doing")(
            markdown(key="body")(
                "- `use_state(...)` stores render state for `name` and `count`\n"
                "- `use_memo(...)` derives a summary object from `name` and `count`\n"
                "- `use_effect(...)` increments a technical counter after matching renders\n"
                "- `use_ref(...)` keeps that technical counter outside render state\n"
                "- `use_context(...)` reads a tree-scoped ambient value from the nearest provider\n"
                "- `use_previous(...)` exposes the previous count value\n"
                "- `use_callback(...)` gives stable callbacks tied to their deps\n"
                f"- `use_id()` produced a stable hook id for this mounted component: `{render_id}`"
            ),
            code(key="snippet", language="python")(
                "class ToneData(ContextData):\n"
                "    mode: str = 'neutral'\n\n"
                "ToneContext = create_context(ToneData(mode='neutral'))\n"
                "state = use_state(name='Ada', count=0)\n"
                "tone = use_context(ToneContext)\n"
                "previous_count = use_previous(state.count)\n"
                "technical = use_ref({'effect_runs': 0})\n"
                "derived = use_memo(lambda: ..., deps=[state.name, state.count])\n"
                "use_effect(lambda: technical.current.__setitem__('effect_runs', technical.current['effect_runs'] + 1), deps=[state.name, state.count])\n"
                "increment = use_callback(lambda: state.update(count=state.count + 1), deps=[state.count])\n"
                "render_id = use_id()"
            ),
        ),
        Section(key="context", title="Context")(
            ContextBadge(key="tone_badge"),
            markdown(key="context_body")(
                "This subtree sits under `ToneContext.Provider(...)`, so `use_context(ToneContext)` "
                "can read an ambient value without threading it through props. The live metric above is reading `tone.mode` from context."
            ),
        ),
        source_view(__file__),
    )


App()(
    ToneContext.Provider(key="tone_scope", data=ToneData(mode="ocean"))(
        HooksDemo(key="app")
    )
).render()
