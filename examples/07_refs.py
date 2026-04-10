"""
07 - Refs

Shows how to navigate the component tree and interact with any node
via Ref objects — lightweight path-based cursors on the fiber tree.

Introduces: self.ref, self.parent, self.root, attribute navigation,
            ref.state(), ref(*children, **props), ref.reset().
"""
import st_components as stc
from st_components.elements import (
    button, code, columns, container, divider, fragment, json, markdown,
    metric, text_input,
)

from examples._source import source_view


class CounterCard(stc.Component):
    class CounterCardState(stc.State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return container(key="card", border=True)(
            metric(key="val", label=self.props.get("label", "Count"), value=self.state.count),
            button(key="inc", on_click=self.increment, width="stretch")("+1"),
        )


# ── 1. Relative navigation ──────────────────────────────────────────────────

class RelativeDemo(stc.Component):
    class S(stc.State):
        snapshot: dict = {}

    def inspect(self):
        """Read state from children using attribute navigation."""
        self.state.snapshot = {
            "self.ref.path": self.ref.path,
            "self.panel.name (output)": self.panel.name.state().output,
            "self.panel.counter (count)": self.panel.counter.state().count,
            "self.parent.path": self.parent.path if self.parent else None,
        }

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 1. Navigate with attribute access"),
            markdown(key="desc")(
                "`self.panel.name` returns a **Ref** — a lightweight cursor that "
                "resolves to the fiber at that path. Use `.state()` to read."
            ),
            text_input(key="name", value="Alice")("Name"),
            CounterCard(key="counter", label="Counter"),
            button(key="read", on_click=self.inspect, type="primary")("Inspect children"),
            json(key="snap")(self.state.snapshot or {"hint": "Click inspect."}),
            code(key="c", language="python")(
                "# Attribute navigation → Ref objects (not Components):\n"
                "self.panel.name.state().output     # widget value\n"
                "self.panel.counter.state().count   # component state\n"
                "self.parent                        # Ref to parent\n"
                "self.root                          # Ref to App"
            ),
        )


# ── 2. Override from callbacks ───────────────────────────────────────────────

class OverrideDemo(stc.Component):

    def fill(self):
        self.panel.target(
            metric(key="a", label="Dynamic A", value=42),
            metric(key="b", label="Dynamic B", value=7),
        )

    def reset(self):
        self.panel.target.reset()

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 2. Override children from a callback"),
            markdown(key="desc")(
                "`self.panel.target(children)` stores overrides on the fiber. "
                "The node renders them on the next rerun. `.reset()` reverts."
            ),
            fragment(key="target")(
                markdown(key="hint")("Initial content — click Fill."),
            ),
            columns(key="btns")(
                button(key="fill", on_click=self.fill, type="primary")("Fill"),
                button(key="reset", on_click=self.reset)("Reset"),
            ),
            code(key="c", language="python")(
                "def fill(self):\n"
                "    self.panel.target(\n"
                "        metric(key=\"a\", label=\"Dynamic\", value=42),\n"
                "    )\n\n"
                "def reset(self):\n"
                "    self.panel.target.reset()"
            ),
        )


# ── 3. Explicit ref= prop (classic style) ───────────────────────────────────

class ExplicitRefDemo(stc.Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.name_ref = stc.Ref()

    class S(stc.State):
        snapshot: str = ""

    def read(self):
        self.state.snapshot = f"name = {self.name_ref.state().output!r}"

    def clear(self):
        self.name_ref.reset_widget()

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 3. Explicit ref= prop (classic style)"),
            markdown(key="desc")(
                "You can still pass `ref=` as a prop to capture a Ref explicitly. "
                "This is useful when you want a named handle stored on the instance."
            ),
            text_input(key="name", ref=self.name_ref, value="Bob")("Name"),
            columns(key="btns")(
                button(key="read", on_click=self.read, type="primary")("Read"),
                button(key="clear", on_click=self.clear)("Clear widget"),
            ),
            markdown(key="snap")(f"`{self.state.snapshot}`" if self.state.snapshot else "Click Read."),
            code(key="c", language="python")(
                "self.name_ref = Ref()\n"
                "text_input(key=\"name\", ref=self.name_ref)\n\n"
                "# Later:\n"
                "self.name_ref.state().output\n"
                "self.name_ref.reset_widget()"
            ),
        )


# ── 4. Tree navigation ──────────────────────────────────────────────────────

class TreeNavDemo(stc.Component):
    class S(stc.State):
        chain: str = ""

    def walk_up(self):
        parts = []
        r = self.ref
        while r is not None:
            parts.append(r.path)
            r = r.parent
        self.state.chain = " → ".join(parts)

    def walk_down(self):
        self.state.chain = (
            f"self.root = {self.root.path}\n"
            f"self.root.page = {self.root.page.path}\n"
            f"self.root.page.nav = {self.root.page.nav.path}"
        )

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 4. Walk the tree"),
            markdown(key="desc")(
                "`.parent` walks up, `.root` jumps to the App. "
                "Attribute access walks down from any point."
            ),
            columns(key="btns")(
                button(key="up", on_click=self.walk_up, type="primary")("Walk up (.parent)"),
                button(key="down", on_click=self.walk_down)("Walk down (.root.x.y)"),
            ),
            markdown(key="chain")(f"```\n{self.state.chain}\n```" if self.state.chain else "Click a button."),
        )


# ── Page ─────────────────────────────────────────────────────────────────────

class RefsDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Refs\n\n"
                "A **Ref** is a lightweight cursor on the fiber tree — it holds "
                "a path string and resolves to the fiber at that path.\n\n"
                "Access children via attributes: `self.panel.name` → `Ref(\"..panel.name\")`. "
                "These are **Ref objects**, not Component instances.\n\n"
                "| Expression | Returns |\n"
                "|---|---|\n"
                "| `self.ref` | Ref to this component |\n"
                "| `self.parent` | Ref to the parent |\n"
                "| `self.root` | Ref to the App |\n"
                "| `self.panel.results` | Ref to a descendant |\n"
                "| `ref.state()` | Read the fiber state |\n"
                "| `ref(*children, **props)` | Override on the fiber |\n"
                "| `ref.reset()` | Clear overrides |\n"
                "| `ref.reset_widget()` | Reset an Element widget |\n"
            ),
            divider(key="d1"),
            RelativeDemo(key="relative"),
            divider(key="d2"),
            OverrideDemo(key="override"),
            divider(key="d3"),
            ExplicitRefDemo(key="explicit"),
            divider(key="d4"),
            TreeNavDemo(key="nav"),
            source_view(__file__),
        )


stc.App(RefsDemo(), page_title="07 - Refs").render()
