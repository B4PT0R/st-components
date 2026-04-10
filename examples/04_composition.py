"""
04 - Composition

Shows how to nest components, pass children, and build reusable pieces.
Introduces: children, props, columns/tabs/expander layouts, component reuse.
"""
import st_components as stc
from st_components.elements import (
    button, caption, columns, container, divider, expander, markdown,
    metric, success, tabs, text_area, warning,
)

from examples._source import source_view


# ---------------------------------------------------------------------------
# Reusable building blocks
# ---------------------------------------------------------------------------

class Section(stc.Component):
    """A titled, bordered section — accepts children via __call__."""

    class SectionProps(stc.Props):
        title: str = ""
        description: str = ""

    def render(self):
        return container(key="box", border=True)(
            markdown(key="title")(f"### {self.props.title}"),
            caption(key="desc")(self.props.description) if self.props.description else None,
            *self.children,
        )


class CounterCard(stc.Component):
    """Compact counter reused in several layouts below."""

    class CounterCardState(stc.State):
        count: int = 0

    def increment(self):
        self.state.count += 1

    def render(self):
        return container(key="card", border=True)(
            metric(key="val", label=self.props.get("label", "Count"), value=self.state.count),
            button(key="inc", on_click=self.increment, width="stretch")("+1"),
        )


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

class ChildrenDemo(stc.Component):
    def render(self):
        return Section(key="sec", title="Children",
                       description="Components accept children via parentheses — just like HTML tags.")(
            markdown(key="body")(
                "The `Section` component above wraps any content you pass:\n\n"
                "```python\n"
                "Section(key=\"s\", title=\"My title\")(\n"
                "    markdown(key=\"a\")(\"First child\"),\n"
                "    markdown(key=\"b\")(\"Second child\"),\n"
                ")\n"
                "```"
            ),
            columns(key="cols")(
                CounterCard(key="a", label="Card A"),
                CounterCard(key="b", label="Card B"),
            ),
        )


class LayoutDemo(stc.Component):
    class LayoutDemoState(stc.State):
        saved: bool = False

    def mark_dirty(self):
        self.state.saved = False

    def mark_saved(self):
        self.state.saved = True

    def render(self):
        return Section(key="sec", title="Layout composition",
                       description="Rich interfaces emerge from combining simple elements.")(
            markdown(key="body")(
                "This mini editor is not a special widget — it is just `text_area` + `button` "
                "+ feedback elements + a `Component` holding two booleans."
            ),
            expander(key="editor", label="Mini editor", expanded=True)(
                text_area(key="draft", height=120, placeholder="Write something, then save.",
                          on_change=self.mark_dirty)("Draft"),
                columns(key="bar")(
                    button(key="save", on_click=self.mark_saved, type="primary")("Save"),
                    success(key="ok")("Saved") if self.state.saved else warning(key="dirty")("Unsaved"),
                ),
            ),
        )


class ReuseDemo(stc.Component):
    def render(self):
        return Section(key="sec", title="Reuse",
                       description="The same CounterCard class powers all the cards on this page.")(
            markdown(key="body")(
                "Components are plain Python classes — reuse them freely. "
                "Each instance has its own state through the fiber system."
            ),
            tabs(key="groups", tabs=["Team A", "Team B"])(
                columns(key="a")(
                    CounterCard(key="a1", label="Alice"),
                    CounterCard(key="a2", label="Bob"),
                ),
                columns(key="b")(
                    CounterCard(key="b1", label="Carol"),
                    CounterCard(key="b2", label="Dave"),
                ),
            ),
        )


class CompositionDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Composition\n\n"
                "Components accept **children** via parentheses, just like function calls. "
                "Nest them freely to build rich interfaces from simple pieces.\n\n"
                "This page itself is composed from a few small, reusable components: "
                "`Section`, `CounterCard`, and standard layout elements."
            ),
            divider(key="d1"),
            ChildrenDemo(key="children"),
            LayoutDemo(key="layout"),
            ReuseDemo(key="reuse"),
            source_view(__file__),
        )


stc.App(page_title="04 - Composition")(CompositionDemo()).render()
