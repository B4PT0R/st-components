"""
Reusable data visualization components.

Demonstrates:
- Typed Props for component interfaces
- _default_output_prop pattern
- Composition of elements into domain-specific widgets
- use_context to read ambient config
- sync_state for concise callbacks
"""
import st_components as stc
from st_components.elements import (
    caption, columns, container, markdown, metric,
)


class StatCard(stc.Component):
    """A bordered card showing a label/value metric with optional delta."""

    class StatCardProps(stc.Props):
        label: str = ""
        value: object = 0
        delta: object = None
        help: str | None = None

    def render(self):
        return metric(
            key="m",
            label=self.props.label,
            value=self.props.value,
            delta=self.props.delta,
            help=self.props.help,
            border=True,
        )


class StatsRow(stc.Component):
    """A horizontal row of StatCards — pass stats as children or via props."""

    class StatsRowProps(stc.Props):
        stats: list = []

    def render(self):
        items = self.props.stats or []
        if not items:
            return None
        return columns(key="row")(
            *[StatCard(key=f"s_{i}", **s) for i, s in enumerate(items)]
        )


class Section(stc.Component):
    """A titled section with description and children."""

    class SectionProps(stc.Props):
        title: str = ""
        description: str = ""

    def render(self):
        return container(key="sec")(
            markdown(key="h")(f"### {self.props.title}"),
            caption(key="d")(self.props.description) if self.props.description else None,
            *self.children,
        )
