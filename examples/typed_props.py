"""
Typed props schema with nested Props subclasses.

Demonstrates three patterns:
- default prop values declared on the class
- extra="ignore" for permissive pass-through components
- extra="forbid" for strict interface enforcement
"""
from modict import modict

from st_components import App, Component, State
from st_components.core.models import Props
from st_components.elements import (
    code, container, divider, error, markdown, metric, subheader, success,
)

from examples._source import source_view


# --- 1. Default prop values ---
# Declaring Props as a typed subclass gives you documented defaults
# without defensive get() calls inside render().

class Badge(Component):

    class BadgeProps(Props):
        label: str = "badge"
        color: str = "blue"

    def render(self):
        return markdown(key="body")(
            f":{self.props.color}[**{self.props.label}**]"
        )


# --- 2. extra="ignore" ---
# Useful for wrapper or layout components that forward a subset of props
# and should silently drop anything they don't own.

class Card(Component):

    class CardProps(Props):
        _config = modict.config(extra="ignore")
        title: str = "Untitled"
        border: bool = True

    def render(self):
        return container(key="box", border=self.props.border)(
            markdown(key="title")(f"**{self.props.title}**"),
            *self.children,
        )


# --- 3. extra="forbid" ---
# Useful when you want to lock down a component's public interface
# and catch typos or wrong prop names at call time.

class StrictMetric(Component):

    class StrictMetricProps(Props):
        _config = modict.config(extra="forbid")
        label: str
        value: int = 0
        delta: int = 0

    def render(self):
        return metric(
            key="metric",
            label=self.props.label,
            value=self.props.value,
            delta=self.props.delta,
        )


class Demo(Component):

    def render(self):
        # Default props
        badge_default = Badge(key="badge_default")
        badge_custom = Badge(key="badge_custom", label="success", color="green")

        # extra="ignore": the unknown prop `tooltip` is silently dropped
        card = Card(key="card", title="My card", border=True, tooltip="ignored")(
            markdown(key="body")("This card received a `tooltip` prop that was silently ignored."),
        )

        # extra="forbid": good call
        good_metric = StrictMetric(key="good_metric", label="Score", value=42, delta=3)

        # extra="forbid": unknown prop, caught at instantiation
        try:
            bad_metric = StrictMetric(key="bad_metric", label="Score", typo_prop=99)
            unknown_prop_display = error(key="miss")("Expected an error but got none.")
        except Exception as e:
            unknown_prop_display = error(key="err_extra")(f"Unknown prop — {e}")

        # type error: caught regardless of extra mode
        try:
            bad_type = StrictMetric(key="bad_type", label="Score", value="not_an_int")
            type_error_display = error(key="miss2")("Expected an error but got none.")
        except Exception as e:
            type_error_display = error(key="err_type")(f"Type error — {e}")

        return container(key="page")(
            subheader(key="h1")("1. Default prop values"),
            markdown(key="desc1")(
                "Props declared in the nested class get typed defaults. "
                "No defensive `props.get()` needed inside `render()`."
            ),
            container(key="badges")(badge_default, badge_custom),
            code(key="code1", language="python")(
                "class Badge(Component):\n"
                "    class BadgeProps(Props):\n"
                "        label: str = \"badge\"\n"
                "        color: str = \"blue\"\n\n"
                "Badge(key=\"b1\")                          # label=\"badge\", color=\"blue\"\n"
                "Badge(key=\"b2\", label=\"ok\", color=\"green\") # label=\"ok\",   color=\"green\""
            ),
            divider(key="d1"),
            subheader(key="h2")("2. extra=\"ignore\""),
            markdown(key="desc2")(
                "Unknown props are silently dropped. "
                "Useful for wrapper components that only consume a subset of what they receive."
            ),
            card,
            code(key="code2", language="python")(
                "class CardProps(Props):\n"
                "    _config = modict.config(extra=\"ignore\")\n"
                "    title: str = \"Untitled\"\n\n"
                "Card(key=\"c\", title=\"My card\", tooltip=\"ignored\")  # tooltip is dropped"
            ),
            divider(key="d2"),
            subheader(key="h3")("3. extra=\"forbid\""),
            markdown(key="desc3")(
                "Unknown props raise immediately at call time. "
                "Useful to catch typos and enforce a documented interface."
            ),
            good_metric,
            unknown_prop_display,
            type_error_display,
            code(key="code3", language="python")(
                "class StrictMetricProps(Props):\n"
                "    _config = modict.config(extra=\"forbid\")\n"
                "    label: str\n"
                "    value: int = 0\n\n"
                "StrictMetric(key=\"m\", label=\"Score\", value=42)        # ok\n"
                "StrictMetric(key=\"m\", label=\"Score\", typo=99)         # unknown prop → raises\n"
                "StrictMetric(key=\"m\", label=\"Score\", value=\"oops\")   # wrong type  → raises"
            ),
            source_view(__file__),
        )


App()(Demo(key="demo")).render()
