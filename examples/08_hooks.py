"""
07 - Hooks

Progressive introduction to every hook, one section at a time.
Each hook is demonstrated in isolation before they combine in a final demo.
Introduces: use_memo, use_effect, use_ref, use_callback, use_previous, use_id.
(use_state and use_context are covered in earlier examples.)
"""
import st_components as stc
from st_components.elements import (
    button, code, columns, container, divider, markdown, metric, text_input,
)

from examples._source import source_view


@stc.component
def MemoDemo(props):
    """use_memo: memoize expensive computations."""
    state = stc.use_state(text="hello world")
    word_count = stc.use_memo(lambda: len(state.text.split()), deps=[state.text])

    return container(key="card", border=True)(
        markdown(key="h")("### use_memo"),
        markdown(key="desc")(
            "Caches the return value of a factory function. "
            "Recomputes only when **deps** change."
        ),
        text_input(key="text", value=state.text,
                   on_change=lambda v: state.update(text=v))("Type something"),
        metric(key="words", label="Word count (memoized)", value=word_count),
        code(key="c", language="python")(
            "word_count = use_memo(lambda: len(state.text.split()), deps=[state.text])"
        ),
    )


@stc.component
def EffectDemo(props):
    """use_effect: side effects after render."""
    state = stc.use_state(count=0)
    log = stc.use_ref([])

    def effect():
        log.current.append(f"effect ran (count={state.count})")
        if len(log.current) > 5:
            log.current[:] = log.current[-5:]
        def cleanup():
            log.current.append("cleanup")
            if len(log.current) > 5:
                log.current[:] = log.current[-5:]
        return cleanup

    stc.use_effect(effect, deps=[state.count])

    return container(key="card", border=True)(
        markdown(key="h")("### use_effect"),
        markdown(key="desc")(
            "Runs a function **after render** when deps change. "
            "The optional cleanup runs before the next effect or on unmount."
        ),
        button(key="inc", on_click=lambda: state.update(count=state.count + 1),
               type="primary")(f"Increment ({state.count})"),
        markdown(key="log")("**Effect log** (last 5):\n" + "\n".join(
            f"- `{entry}`" for entry in log.current
        ) if log.current else "*Click the button to trigger effects.*"),
        code(key="c", language="python")(
            "def effect():\n"
            "    log.current.append(f\"ran at {state.count}\")\n"
            "    return lambda: log.current.append(\"cleanup\")\n\n"
            "use_effect(effect, deps=[state.count])"
        ),
    )


@stc.component
def RefDemo(props):
    """use_ref: mutable container that persists without triggering reruns."""
    render_count = stc.use_ref(0)
    render_count.current += 1
    state = stc.use_state(trigger=0)

    return container(key="card", border=True)(
        markdown(key="h")("### use_ref"),
        markdown(key="desc")(
            "Returns a `RefValue` that persists across renders. "
            "Unlike state, mutating it does **not** cause a rerun."
        ),
        metric(key="renders", label="Render count (via ref)", value=render_count.current),
        button(key="rerun", on_click=lambda: state.update(trigger=state.trigger + 1))(
            "Force rerun"
        ),
        code(key="c", language="python")(
            "render_count = use_ref(0)\n"
            "render_count.current += 1  # no rerun triggered"
        ),
    )


@stc.component
def PreviousDemo(props):
    """use_previous: track the value from the previous render."""
    state = stc.use_state(name="Ada")
    prev_name = stc.use_previous(state.name, initial="(first render)")

    return container(key="card", border=True)(
        markdown(key="h")("### use_previous"),
        markdown(key="desc")(
            "Returns what *value* was on the **previous** render. "
            "Useful for detecting changes or animating transitions."
        ),
        text_input(key="name", value=state.name,
                   on_change=lambda v: state.update(name=v))("Name"),
        columns(key="compare")(
            metric(key="current", label="Current", value=state.name),
            metric(key="previous", label="Previous", value=prev_name),
        ),
        code(key="c", language="python")(
            "prev_name = use_previous(state.name, initial=\"(first render)\")"
        ),
    )


@stc.component
def CallbackIdDemo(props):
    """use_callback + use_id: stable references and deterministic IDs."""
    state = stc.use_state(count=0)
    hook_id = stc.use_id()
    increment = stc.use_callback(
        lambda: state.update(count=state.count + 1),
        deps=[state.count],
    )

    return container(key="card", border=True)(
        markdown(key="h")("### use_callback & use_id"),
        markdown(key="desc")(
            "`use_callback` memoizes a function (same as `use_memo(lambda: fn, deps)`). "
            "`use_id` returns a stable, unique ID based on the hook's position."
        ),
        button(key="inc", on_click=increment, type="primary")(f"Count: {state.count}"),
        metric(key="id", label="Stable hook ID", value=hook_id),
        code(key="c", language="python")(
            "increment = use_callback(lambda: state.update(count=state.count+1), deps=[state.count])\n"
            "hook_id = use_id()  # deterministic, stable across reruns"
        ),
    )


@stc.component
def HooksDemo(props):
    return container(key="page")(
        markdown(key="intro")(
            "## Hooks\n\n"
            "Hooks let functional components manage state, effects, memoization, "
            "and more — without classes.\n\n"
            "**Rule:** always call hooks in the **same order**, never inside conditions or loops.\n\n"
            "Each section below demonstrates one hook in isolation."
        ),
        divider(key="d1"),
        MemoDemo(key="memo"),
        EffectDemo(key="effect"),
        RefDemo(key="ref"),
        PreviousDemo(key="previous"),
        CallbackIdDemo(key="callback_id"),
        source_view(__file__),
    )


stc.App(page_title="07 - Hooks")(HooksDemo()).render()
