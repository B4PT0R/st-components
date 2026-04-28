"""
05 - Styles

Inline styles via the `style=` prop on any Element. The dict is compiled to
scoped CSS targeting only that element instance — not every element of the
same type. Lets you build a real design system on top of Streamlit widgets.

Introduces: style= dict, slots, camelCase / kebab-case props, &:pseudo,
& descendant selectors.
"""
import st_components as stc
from st_components.elements import (
    button, caption, columns, container, divider, markdown, text_input,
)

from examples._source import source_view


# ---------------------------------------------------------------------------
# Pattern 1: Simple style props
# ---------------------------------------------------------------------------

class SimplePropsDemo(stc.Component):
    def render(self):
        return container(key="sec", border=True)(
            markdown(key="title")("### 1. Simple style props"),
            caption(key="desc")(
                "Pass a dict of CSS properties via `style=`. Keys can be camelCase "
                "(`backgroundColor`) or kebab-case (`background-color`)."
            ),
            container(
                key="card",
                style={
                    "backgroundColor": "#f0f9ff",
                    "padding": "1rem",
                    "borderRadius": "12px",
                    "border": "1px solid #93c5fd",
                },
            )(
                markdown(key="body")(
                    "**This card** is a `container` styled inline.\n\n"
                    "No global CSS, no class names to manage — the framework scopes "
                    "the rules to this instance only."
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Pattern 2: Pseudo-classes via &
# ---------------------------------------------------------------------------

class PseudoClassesDemo(stc.Component):
    def render(self):
        return container(key="sec", border=True)(
            markdown(key="title")("### 2. Pseudo-classes — `&:hover`, `&:focus`, …"),
            caption(key="desc")(
                "A nested key with `&` substitutes the element's scope selector. "
                "Use it for `:hover`, `:focus`, `:disabled`, or any pseudo-class."
            ),
            columns(key="row")(
                button(
                    key="primary",
                    type="primary",
                    style={
                        # Apply the hover effect on the `button` slot — the
                        # actual <button> element, not the wrapper around it.
                        "button": {
                            "&:hover": {
                                "transform": "scale(1.05)",
                                "transition": "transform 0.15s ease-in-out",
                            },
                        },
                    },
                )("Hover me — I scale"),
                text_input(
                    key="search",
                    placeholder="Focus me — I glow",
                    style={
                        # `input` is a registered slot on text_input pointing
                        # to the actual field wrapper — no need to know
                        # Streamlit's BaseWeb DOM structure.
                        "input": {
                            "&:focus-within": {
                                "boxShadow": "0 0 0 3px rgba(59, 130, 246, 0.4)",
                                "borderRadius": "8px",
                                "transition": "box-shadow 0.15s ease-in-out",
                            },
                        },
                    },
                )("Search"),
            ),
        )


# ---------------------------------------------------------------------------
# Pattern 3: Descendant selectors — style children of a container
# ---------------------------------------------------------------------------

class DescendantsDemo(stc.Component):
    def render(self):
        return container(key="sec", border=True)(
            markdown(key="title")("### 3. Descendant selectors"),
            caption(key="desc")(
                "Nested keys without `&` are treated as descendants. "
                "Useful when a Streamlit widget has a deep DOM and you need to "
                "reach a specific inner element."
            ),
            container(
                key="callout",
                style={
                    "backgroundColor": "#fef3c7",
                    "borderLeft": "4px solid #f59e0b",
                    "padding": "1rem 1.25rem",
                    "borderRadius": "6px",
                    # Style descendants — `& p` and `& strong`
                    "& p": {"color": "#78350f", "marginBottom": "0.25rem"},
                    "& strong": {"color": "#92400e"},
                },
            )(
                markdown(key="body")(
                    "**Heads up:** descendants of this container inherit the styled "
                    "context. Markdown text, inputs, anything — all reachable with "
                    "ordinary CSS selectors."
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Pattern 4: Reusable styled component — your own design system
# ---------------------------------------------------------------------------

class Tag(stc.Component):
    """A styled pill — encapsulates the look behind a clean API.

    Usage::

        Tag(key="t", color="green")("Stable")
    """

    PALETTE = {
        "blue":   {"bg": "#dbeafe", "fg": "#1e40af"},
        "green":  {"bg": "#dcfce7", "fg": "#166534"},
        "red":    {"bg": "#fee2e2", "fg": "#991b1b"},
        "amber":  {"bg": "#fef3c7", "fg": "#92400e"},
        "violet": {"bg": "#ede9fe", "fg": "#5b21b6"},
    }

    def render(self):
        color = self.props.get("color", "blue")
        palette = self.PALETTE.get(color, self.PALETTE["blue"])
        label = self.children[0] if self.children else ""
        # The pill background goes on the `body` slot — Streamlit's
        # `[data-testid="stMarkdownContainer"]`, the tight wrapper around the
        # rendered <p>. Putting it there (not on `root`) makes the bg hug the
        # text instead of stretching the full row width through Streamlit's
        # outer block wrappers.
        return markdown(
            key="tag",
            style={
                "body": {
                    "display": "inline-block",
                    "backgroundColor": palette["bg"],
                    "padding": "0.25rem 0.75rem",
                    "borderRadius": "999px",
                },
                # Top-level props → default slot `text` (the <p>).
                "color": palette["fg"],
                "fontSize": "0.8rem",
                "fontWeight": "600",
                "lineHeight": "1.4",
                "margin": "0",
            },
        )(label)


class ReusableDemo(stc.Component):
    def render(self):
        return container(key="sec", border=True)(
            markdown(key="title")("### 4. Reusable styled component"),
            caption(key="desc")(
                "Wrap a styled Element inside your own `Component` class to expose "
                "a clean, prop-driven API. Same idea as building a design system "
                "in React with styled-components."
            ),
            columns(key="row")(
                Tag(key="t1", color="green")("Stable"),
                Tag(key="t2", color="amber")("Preview"),
                Tag(key="t3", color="red")("Deprecated"),
                Tag(key="t4", color="violet")("Experimental"),
                Tag(key="t5", color="blue")("New"),
            ),
            markdown(key="body")(
                "The `Tag` class above takes a `color=` prop and renders an inline "
                "pill. The styling is completely encapsulated — callers don't see "
                "the CSS, just `Tag(color=\"green\")(\"Stable\")`."
            ),
        )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

class StylesDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Inline Styles\n\n"
                "Every Element accepts a `style=` dict. Rules are scoped to "
                "**this instance only** — never leaking to other elements of "
                "the same type.\n\n"
                "**Slots.** Streamlit elements aren't atomic DOM nodes — a "
                "button is `<div><button><p>label</p></button></div>`, an input "
                "is wrapped in BaseWeb divs, etc. Each Element class declares "
                "named *slots* mapping logical names to inner CSS selectors:\n\n"
                "| Element | Default slot | Other slots |\n"
                "|---|---|---|\n"
                "| `markdown`, `caption`, `latex` | `text` (the `<p>`) | `root` |\n"
                "| `button`, `download_button`, `form_submit_button` | `button` | `root`, `label` |\n"
                "| `text_input`, `number_input`, `date_input` | `input` (BaseWeb wrapper) | `root`, `label` |\n"
                "| `text_area`, `chat_input` | `input` (the `<textarea>` wrapper) | `root`, `label` |\n"
                "| `selectbox`, `multiselect` | `select` | `root`, `label` |\n"
                "| `metric` | `root` | `label`, `value`, `delta` |\n"
                "| `container`, `columns` | `root` | — |\n\n"
                "**Three forms of dict keys:**\n\n"
                "| Form | Effect |\n"
                "|---|---|\n"
                "| `\"backgroundColor\": \"red\"` | CSS property → applied to the **default slot** |\n"
                "| `\"label\": {...}` | matches a slot name → rule on that slot |\n"
                "| `\"&:hover\": {...}` | CSS selector with `&` (= wrapper of scope) |\n"
                "| `\"& > div\": {...}` | descendant selector for advanced cases |\n\n"
                "Build reusable styled components by wrapping a styled Element in "
                "your own `Component` class — see `Tag` below."
            ),
            divider(key="d1"),
            SimplePropsDemo(key="simple"),
            PseudoClassesDemo(key="pseudo"),
            DescendantsDemo(key="descendants"),
            ReusableDemo(key="reusable"),
            source_view(__file__),
        )


stc.App(StylesDemo(), page_title="05 - Styles").render()
