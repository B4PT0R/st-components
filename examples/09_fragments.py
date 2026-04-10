"""
08 - Fragments

Shows the fragment element for grouping and scoped re-rendering.
Introduces: fragment, scoped, run_every, nested fragments.
"""
import datetime

import st_components as stc
from st_components.elements import (
    button, caption, code, columns, container, divider, fragment, markdown, metric,
)

from examples._source import source_view


# ── Reusable counter that tracks its own render count ────────────────────────

class RenderCounter(stc.Component):
    """Each instance shows clicks and render count — the render count proves
    whether the component was re-executed or not."""

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


# ── 1. Transparent grouping ─────────────────────────────────────────────────

class TransparentDemo(stc.Component):
    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 1. Transparent grouping"),
            caption(key="desc")(
                "`fragment()` with no arguments is a simple grouping element — "
                "like React's `<Fragment>`. No scoping, no wrapper. "
                "Both counters re-render together on any click."
            ),
            fragment(key="grp")(
                columns(key="cols")(
                    RenderCounter(key="a", label="Counter A"),
                    RenderCounter(key="b", label="Counter B"),
                ),
            ),
            code(key="c", language="python")(
                "fragment(key=\"grp\")(\n"
                "    Counter(key=\"a\"),\n"
                "    Counter(key=\"b\"),\n"
                ")"
            ),
        )


# ── 2. Scoped re-rendering ──────────────────────────────────────────────────

class ScopedDemo(stc.Component):
    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 2. Scoped re-rendering"),
            caption(key="desc")(
                "`fragment(scoped=True)` wraps children in `st.fragment()`. "
                "Only the subtree inside the fragment re-runs on interaction — "
                "the outer counter's render count stays stable."
            ),
            markdown(key="try")(
                "**What to try:** click both buttons and compare the render counts."
            ),
            columns(key="cols")(
                container(key="outer_box", border=True)(
                    caption(key="lbl")("Outside the fragment:"),
                    RenderCounter(key="outer", label="Outer"),
                ),
                container(key="inner_box", border=True)(
                    caption(key="lbl")("Inside `fragment(scoped=True)`:"),
                    fragment(key="scoped", scoped=True)(
                        RenderCounter(key="inner", label="Scoped"),
                    ),
                ),
            ),
            code(key="c", language="python")(
                "fragment(key=\"scoped\", scoped=True)(\n"
                "    RenderCounter(key=\"inner\"),\n"
                ")"
            ),
        )


# ── 3. Auto-refresh with run_every ──────────────────────────────────────────

@stc.component
def LiveClock(props):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return container(key="card", border=True)(
        metric(key="time", label="Live time", value=now),
        caption(key="note")("Updates automatically — no click needed."),
    )


class RunEveryDemo(stc.Component):
    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 3. Auto-refresh with run_every"),
            caption(key="desc")(
                "`fragment(scoped=True, run_every='2s')` refreshes its children "
                "every 2 seconds. The static counter next to it is untouched."
            ),
            columns(key="cols")(
                container(key="static_box", border=True)(
                    caption(key="lbl")("Static (outside):"),
                    RenderCounter(key="static", label="Static"),
                ),
                container(key="live_box", border=True)(
                    caption(key="lbl")("Auto-refresh (inside):"),
                    fragment(key="live", scoped=True, run_every="2s")(
                        LiveClock(key="clock"),
                    ),
                ),
            ),
            code(key="c", language="python")(
                "fragment(key=\"live\", scoped=True, run_every=\"2s\")(\n"
                "    LiveClock(key=\"clock\"),\n"
                ")"
            ),
        )


# ── 4. Nested fragments ─────────────────────────────────────────────────────

class NestedDemo(stc.Component):
    def render(self):
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]
        return container(key="panel", border=True)(
            markdown(key="h")("### 4. Nested fragments"),
            caption(key="desc")(
                "Fragments nest naturally. Each scoped boundary re-renders "
                "independently. The inner clock refreshes every second without "
                "touching the outer fragment or the rest of the page."
            ),
            fragment(key="outer", scoped=True)(
                container(key="outer_box", border=True)(
                    caption(key="lbl")("Outer scoped fragment:"),
                    RenderCounter(key="counter", label="Outer"),
                    fragment(key="inner", scoped=True, run_every="1s")(
                        container(key="inner_box", border=True)(
                            caption(key="lbl")("Inner scoped fragment (1s):"),
                            metric(key="time", label="Nested clock", value=now),
                        ),
                    ),
                ),
            ),
            code(key="c", language="python")(
                "fragment(key=\"outer\", scoped=True)(\n"
                "    Counter(key=\"counter\"),\n"
                "    fragment(key=\"inner\", scoped=True, run_every=\"1s\")(\n"
                "        LiveClock(key=\"clock\"),\n"
                "    ),\n"
                ")"
            ),
        )


# ── Page ─────────────────────────────────────────────────────────────────────

class FragmentDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Fragments\n\n"
                "The `fragment` element groups children — and optionally scopes "
                "their re-rendering via `st.fragment()`.\n\n"
                "| Mode | Prop | Effect |\n"
                "|---|---|---|\n"
                "| Transparent | `scoped=False` (default) | Groups children, no wrapper — like React Fragment |\n"
                "| Scoped | `scoped=True` | Only this subtree re-runs on interaction |\n"
                "| Auto-refresh | `scoped=True, run_every=...` | Subtree refreshes on a timer |\n\n"
                "Scoped fragments **nest** — each boundary is independent. "
                "This gives you **fine-grained re-render control** just by placing "
                "`fragment(scoped=True)` nodes in your component tree."
            ),
            divider(key="d1"),
            TransparentDemo(key="transparent"),
            divider(key="d2"),
            ScopedDemo(key="scoped"),
            divider(key="d3"),
            RunEveryDemo(key="run_every"),
            divider(key="d4"),
            NestedDemo(key="nested"),
            source_view(__file__),
        )


stc.App(page_title="08 - Fragments", layout="wide")(FragmentDemo()).render()
