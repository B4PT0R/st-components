"""
10 - Scoped Rerun

Shows how rerun() and wait() are scoped to the current fragment.
Each scoped fragment has its own independent rerun timeline —
delays inside a fragment don't interfere with the app or other fragments.

Introduces: rerun, wait, scoped rerun timelines.
"""
import datetime

import st_components as stc
from st_components.core.rerun import rerun, wait
from st_components.elements import (
    button, caption, code, columns, container, divider, fragment,
    markdown, metric, slider,
)

from examples._source import source_view


# ── Counter with render tracking ─────────────────────────────────────────────

class RenderCounter(stc.Component):
    class S(stc.State):
        clicks: int = 0
        renders: int = 0

    def increment(self):
        self.state.clicks += 1

    def render(self):
        self.state.renders += 1
        return container(key="card", border=True)(
            metric(key="clicks", label=self.props.get("label", "Clicks"),
                   value=self.state.clicks),
            metric(key="renders", label="Renders", value=self.state.renders),
            button(key="inc", on_click=self.increment, type="primary")("+1"),
        )


# ── 1. Basic scoped rerun ───────────────────────────────────────────────────

class BasicRerunDemo(stc.Component):
    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 1. Scoped rerun()"),
            caption(key="desc")(
                "Inside a scoped fragment, `rerun()` targets that fragment only. "
                "The outer counter is untouched."
            ),
            columns(key="cols")(
                container(key="outer_box", border=True)(
                    caption(key="lbl")("App scope (outside):"),
                    RenderCounter(key="outer", label="Outer"),
                ),
                container(key="inner_box", border=True)(
                    caption(key="lbl")("Fragment scope (inside):"),
                    fragment(key="frag", scoped=True)(
                        RenderCounter(key="inner", label="Scoped"),
                    ),
                ),
            ),
            code(key="c", language="python")(
                "# Inside the fragment, rerun() only reruns the fragment:\n"
                "rerun()           # targets current fragment scope\n"
                "rerun(scope=\"app\") # explicit: targets the full app"
            ),
        )


# ── 2. Scoped wait() ────────────────────────────────────────────────────────

@stc.component
def WaitDemo(props):
    state = stc.use_state(last_toast="(none)")

    def toast_and_rerun():
        state.last_toast = datetime.datetime.now().strftime("%H:%M:%S")
        wait(1.5)      # fragment gets 1.5s before rerunning
        rerun()         # targets this fragment only

    return container(key="panel", border=True)(
        markdown(key="h")("### 2. Scoped wait()"),
        caption(key="desc")(
            "`wait(1.5)` inside a fragment delays only that fragment's rerun. "
            "The app and other fragments are unaffected."
        ),
        columns(key="cols")(
            container(key="static_box", border=True)(
                caption(key="lbl")("App scope (unaffected):"),
                RenderCounter(key="static", label="Static"),
            ),
            container(key="frag_box", border=True)(
                caption(key="lbl")("Fragment with wait(1.5):"),
                fragment(key="frag", scoped=True)(
                    metric(key="toast", label="Last toast time", value=state.last_toast),
                    button(key="fire", on_click=toast_and_rerun, type="primary")(
                        "Toast + wait(1.5) + rerun"
                    ),
                    caption(key="note")("The fragment waits 1.5s before refreshing."),
                ),
            ),
        ),
        code(key="c", language="python")(
            "def toast_and_rerun():\n"
            "    wait(1.5)    # this fragment waits 1.5s\n"
            "    rerun()      # then reruns just this fragment"
        ),
    )


# ── 3. Independent timelines ────────────────────────────────────────────────

@stc.component
def FastFragment(props):
    state = stc.use_state(ticks=0)

    def tick():
        state.ticks += 1
        rerun(wait=0.3)

    return container(key="card", border=True)(
        caption(key="lbl")(props.get("label", "Fast")),
        metric(key="ticks", label="Ticks", value=state.ticks),
        button(key="go", on_click=tick)("Tick (0.3s)"),
    )


@stc.component
def SlowFragment(props):
    state = stc.use_state(ticks=0)

    def tick():
        state.ticks += 1
        rerun(wait=2.0)

    return container(key="card", border=True)(
        caption(key="lbl")(props.get("label", "Slow")),
        metric(key="ticks", label="Ticks", value=state.ticks),
        button(key="go", on_click=tick)("Tick (2.0s)"),
    )


class IndependentDemo(stc.Component):
    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 3. Independent timelines"),
            caption(key="desc")(
                "Two fragments side by side, each with its own rerun delay. "
                "Click both — the fast one ticks at 0.3s, the slow one at 2.0s. "
                "Neither blocks the other."
            ),
            columns(key="cols")(
                fragment(key="fast", scoped=True)(
                    FastFragment(key="f", label="Fast fragment (0.3s)"),
                ),
                fragment(key="slow", scoped=True)(
                    SlowFragment(key="s", label="Slow fragment (2.0s)"),
                ),
            ),
            code(key="c", language="python")(
                "# Each fragment has its own timeline:\n"
                "fragment(key=\"fast\", scoped=True)(\n"
                "    # rerun(wait=0.3) here only affects this fragment\n"
                ")\n"
                "fragment(key=\"slow\", scoped=True)(\n"
                "    # rerun(wait=2.0) here only affects this fragment\n"
                ")"
            ),
        )


# ── 4. Nested scope isolation ───────────────────────────────────────────────

class NestedRerunDemo(stc.Component):
    def render(self):
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]
        return container(key="panel", border=True)(
            markdown(key="h")("### 4. Nested scope isolation"),
            caption(key="desc")(
                "A fragment inside a fragment. Each level has its own rerun scope. "
                "The inner clock refreshes every second without touching the outer counter."
            ),
            fragment(key="outer", scoped=True)(
                container(key="outer_box", border=True)(
                    caption(key="lbl")("Outer fragment:"),
                    RenderCounter(key="counter", label="Outer"),
                    fragment(key="inner", scoped=True, run_every="1s")(
                        container(key="inner_box", border=True)(
                            caption(key="lbl")("Inner fragment (auto 1s):"),
                            metric(key="time", label="Clock", value=now),
                        ),
                    ),
                ),
            ),
        )


# ── Page ─────────────────────────────────────────────────────────────────────

class ScopedRerunDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Scoped Rerun\n\n"
                "`rerun()` and `wait()` automatically target the **current fragment scope**. "
                "Each scoped fragment has its own independent rerun timeline — "
                "delays in one fragment don't block others or the app.\n\n"
                "| Called from | `rerun()` targets | `wait()` targets |\n"
                "|---|---|---|\n"
                "| App (no fragment) | Full app | Full app |\n"
                "| Scoped fragment | That fragment only | That fragment only |\n"
                "| Nested fragment | Innermost fragment | Innermost fragment |\n\n"
                "Use `rerun(scope=\"app\")` to explicitly target the app from inside a fragment."
            ),
            divider(key="d1"),
            BasicRerunDemo(key="basic"),
            divider(key="d2"),
            WaitDemo(key="wait"),
            divider(key="d3"),
            IndependentDemo(key="independent"),
            divider(key="d4"),
            NestedRerunDemo(key="nested"),
            source_view(__file__),
        )


stc.App(ScopedRerunDemo(), page_title="10 - Scoped Rerun", layout="wide").render()
