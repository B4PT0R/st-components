"""
12 - Dynamic Rendering

Every node in the tree is pilotable from callbacks via fiber overrides.
Navigate the tree with attribute access (self.panel.results) and override
props/children with __call__. .reset() reverts to parent-passed values.

Introduces: self.ref, self.parent, self.root, attribute navigation, fiber overrides.
"""
import datetime

import st_components as stc
from st_components.elements import (
    badge, button, caption, code, column, columns, container, divider,
    fragment, markdown, metric,
)

from examples._source import source_view


# ── 1. Override children ─────────────────────────────────────────────────────

class ChildrenDemo(stc.Component):

    def fill(self):
        self.panel.target(
            metric(key="rows", label="Rows loaded", value=1234),
            metric(key="cols", label="Columns", value=42),
            caption(key="ts")(f"Filled at {datetime.datetime.now():%H:%M:%S}"),
        )

    def reset(self):
        self.panel.target.reset()

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 1. Override children from a callback"),
            caption(key="desc")(
                "`self.panel.target(children)` stores children on the fiber. "
                "On the next rerun, the node renders them. `.reset()` restores initial content."
            ),
            fragment(key="target")(
                caption(key="hint")("Initial content — click Fill to replace."),
            ),
            columns(key="btns")(
                button(key="fill", on_click=self.fill, type="primary")("Fill"),
                button(key="reset", on_click=self.reset)("Reset"),
            ),
            code(key="c", language="python")(
                "def fill(self):\n"
                "    self.panel.target(\n"
                "        metric(key=\"n\", label=\"Rows\", value=1234),\n"
                "    )\n\n"
                "def reset(self):\n"
                "    self.panel.target.reset()"
            ),
        )


# ── 2. Override props ────────────────────────────────────────────────────────

class PropsDemo(stc.Component):

    def set_success(self):
        self.panel.status(label="Status", value="OK", delta=1)

    def set_error(self):
        self.panel.status(label="Status", value="ERROR", delta=-1)

    def reset(self):
        self.panel.status.reset()

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 2. Override props"),
            caption(key="desc")(
                "`self.panel.status(label=..., value=...)` overrides props. "
                "The node re-renders with the new props."
            ),
            metric(key="status", label="Status", value="—"),
            columns(key="btns")(
                button(key="ok", on_click=self.set_success)("Set OK"),
                button(key="err", on_click=self.set_error)("Set ERROR"),
                button(key="reset", on_click=self.reset)("Reset"),
            ),
            code(key="c", language="python")(
                "self.panel.status(label=\"Status\", value=\"OK\")"
            ),
        )


# ── 3. Chain props + children ────────────────────────────────────────────────

class ChainDemo(stc.Component):

    def style_and_fill(self):
        self.panel.card(border=True)(
            metric(key="a", label="Alpha", value=42),
            metric(key="b", label="Beta", value=7),
        )

    def reset(self):
        self.panel.card.reset()

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 3. Chain: props then children"),
            caption(key="desc")(
                "`self.panel.card(border=True)(children)` — chainable."
            ),
            container(key="card")(
                caption(key="hint")("Default card content."),
            ),
            columns(key="btns")(
                button(key="style", on_click=self.style_and_fill, type="primary")("Style + fill"),
                button(key="reset", on_click=self.reset)("Reset"),
            ),
            code(key="c", language="python")(
                "self.panel.card(border=True)(\n"
                "    metric(key=\"a\", label=\"Alpha\", value=42),\n"
                ")"
            ),
        )


# ── 4. Named columns ────────────────────────────────────────────────────────

class ColumnDemo(stc.Component):

    def fill_left(self):
        self.panel.grid.left.data(
            metric(key="n", label="Left", value=datetime.datetime.now().second),
        )

    def fill_right(self):
        self.panel.grid.right.data(
            metric(key="n", label="Right", value=datetime.datetime.now().microsecond),
        )

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 4. Named columns"),
            caption(key="desc")(
                "`self.panel.grid.left.data` vs `self.panel.grid.right.data` — "
                "same key, different paths."
            ),
            columns(key="grid")(
                column(key="left")(
                    caption(key="lbl")("Left:"),
                    fragment(key="data")(caption(key="hint")("Empty")),
                    button(key="fill", on_click=self.fill_left)("Fill left"),
                ),
                column(key="right")(
                    caption(key="lbl")("Right:"),
                    fragment(key="data")(caption(key="hint")("Empty")),
                    button(key="fill", on_click=self.fill_right)("Fill right"),
                ),
            ),
        )


# ── 5. Tree navigation ──────────────────────────────────────────────────────

class NavigationDemo(stc.Component):
    class S(stc.State):
        info: str = ""

    def inspect(self):
        chain = []
        r = self.ref.panel.target
        while r is not None:
            chain.append(r.path)
            r = r.parent
        self.state.info = " → ".join(chain)

    def render(self):
        return container(key="panel", border=True)(
            markdown(key="h")("### 5. Tree navigation"),
            caption(key="desc")(
                "`self.ref` → this component. `.parent` → up. `.root` → the App. "
                "Chain attributes to navigate anywhere."
            ),
            fragment(key="target")(
                caption(key="leaf")("Target node"),
            ),
            button(key="inspect", on_click=self.inspect, type="primary")("Inspect parent chain"),
            markdown(key="info")(f"`{self.state.info}`" if self.state.info else "Click inspect."),
            code(key="c", language="python")(
                "self.ref           # Ref to this component\n"
                "self.parent        # Ref to parent\n"
                "self.root          # Ref to App\n"
                "self.panel.target  # Ref to a child\n"
                "self.root.page.dashboard.panel  # absolute navigation"
            ),
        )


# ── Page ─────────────────────────────────────────────────────────────────────

class DynamicRenderingDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Dynamic Rendering\n\n"
                "The component IS a cursor on the tree. Navigate with attributes, "
                "override with `__call__`, reset with `.reset()`.\n\n"
                "| Expression | What it does |\n"
                "|---|---|\n"
                "| `self.ref` | Ref to this component |\n"
                "| `self.parent` | Ref to the parent |\n"
                "| `self.root` | Ref to the App |\n"
                "| `self.panel.results` | Navigate to a child |\n"
                "| `self.panel.results(*children)` | Override children |\n"
                "| `self.panel.results(**props)` | Override props |\n"
                "| `self.panel.results(**props)(*children)` | Chain both |\n"
                "| `self.panel.results.reset()` | Revert to parent values |\n"
            ),
            divider(key="d1"),
            ChildrenDemo(key="children"),
            divider(key="d2"),
            PropsDemo(key="props"),
            divider(key="d3"),
            ChainDemo(key="chain"),
            divider(key="d4"),
            ColumnDemo(key="columns"),
            divider(key="d5"),
            NavigationDemo(key="nav"),
            source_view(__file__),
        )


stc.App(DynamicRenderingDemo(), page_title="12 - Dynamic Rendering", layout="wide").render()
