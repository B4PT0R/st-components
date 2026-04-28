"""Inline styles for Elements — compile a Python dict into scoped CSS.

The ``style=`` prop on any Element accepts a dict of CSS properties. At
render time the framework wraps the element in ``st.container(key=scope)``
(which Streamlit emits as a ``.st-key-<scope>`` wrapper class) and injects
a ``<style>`` block scoped to that selector — so the rules only affect
that one element instance, not every element of the same type.

**Slots.**  Streamlit elements aren't atomic DOM nodes — they have internal
layout (a button is ``<div><button><p>label</p></button></div>``, an input
is wrapped in BaseWeb divs, etc.).  Each Element class can declare named
*slots* mapping logical names to inner CSS selectors.  Top-level CSS
properties land on the element's *default slot* (the obvious target —
``button`` for a button, ``p`` for markdown, ``[data-baseweb="input"]``
for a text input).  Slot names also act as nested-rule keys.

Supported dict shape::

    {
        "backgroundColor": "lightblue",     # → default slot
        "padding": "10px",                  # → default slot
        "&:hover": {                        # nested CSS selector — & = wrapper scope
            "backgroundColor": "skyblue",
        },
        "label": {                          # slot name (if registered)
            "fontWeight": "bold",
        },
        "& > div": {                        # descendant selector — explicit
            "fontSize": "16px",
        },
    }

For a button with default slot ``button``, that compiles roughly to::

    .st-key-<scope> button { background-color: lightblue; padding: 10px; }
    .st-key-<scope>:hover { background-color: skyblue; }
    .st-key-<scope> label { font-weight: bold; }
    .st-key-<scope> > div { font-size: 16px; }
"""
import re

_CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")
_SELECTOR_CHARS = frozenset("&:>+~ ,[")


def _kebab(name):
    """``backgroundColor`` -> ``background-color``. Pass-through if already kebab."""
    return _CAMEL_RE.sub("-", name).lower()


def style_scope_key(element_path):
    """Derive a CSS-safe scope key from an element's fiber path.

    Element paths contain dots (``app.page.button.raw``); dots in CSS class
    names need backslash-escaping in selectors. We replace them with double
    underscores so the resulting class name is plain alphanumeric and can
    be used as ``.st-key-<scope>`` directly.
    """
    return "stcstyle__" + element_path.replace(".", "__")


def _join(scope, selector):
    """Compose a scope and an inner selector into a CSS selector.

    Empty inner selector → just the scope.  Otherwise descendant combinator.
    """
    return f"{scope} {selector}" if selector else scope


def compile_style(style, scope_selector, *, slots=None, default_slot=None):
    """Compile a style dict to scoped CSS text.

    *style* — top-level dict.  Top-level keys are interpreted as:

    - **slot name** if it matches a key in *slots* and the value is a dict
      → emits a rule at ``<scope> <slot_selector>``.
    - **CSS selector** if the key contains a selector character
      (``&``, ``:``, ``>``, ``+``, ``~``, space, ``,``, ``[``) and the value
      is a dict → ``&`` is substituted with *scope_selector*; otherwise the
      key is treated as a descendant selector relative to *scope_selector*.
    - **CSS property** for any scalar value (camelCase or kebab-case) →
      lands on the default slot.

    *scope_selector* — the wrapper selector (e.g. ``".st-key-foo"``).

    *slots* — ``{name: inner_selector}`` mapping.  Empty inner selector
    means the slot IS the wrapper itself.

    *default_slot* — name of the slot where bare CSS properties land.
    Must be a key in *slots* if both are provided.  ``None`` means CSS
    properties land on the wrapper itself.
    """
    if not isinstance(style, dict):
        raise TypeError(
            f"style= must be a dict, got {type(style).__name__!r}. "
            f"Pass CSS properties as keys (camelCase or kebab-case) and values as strings, "
            f"e.g. style={{'backgroundColor': 'red', 'padding': '10px'}}."
        )

    slots = slots or {}
    if default_slot is not None and default_slot not in slots:
        raise ValueError(
            f"default_slot={default_slot!r} is not a registered slot name. "
            f"Known slots: {sorted(slots)}."
        )
    default_inner = slots.get(default_slot, "") if default_slot else ""

    blocks = []
    flat_props = []
    nested = []

    for key, value in style.items():
        if isinstance(value, dict):
            if key in slots:
                child_scope = _join(scope_selector, slots[key])
            elif any(c in key for c in _SELECTOR_CHARS):
                child_scope = key.replace("&", scope_selector) if "&" in key else _join(scope_selector, key)
            else:
                child_scope = _join(scope_selector, key)
            nested.append((value, child_scope))
        else:
            flat_props.append(f"{_kebab(key)}: {value};")

    if flat_props:
        target = _join(scope_selector, default_inner)
        blocks.append(f"{target} {{ {' '.join(flat_props)} }}")

    for sub_style, child_scope in nested:
        _emit_nested(sub_style, child_scope, blocks)

    return "\n".join(blocks)


def _emit_nested(style, scope, blocks):
    """Inside a nested rule: standard CSS, no slot lookup.

    Flat properties land on *scope* directly; nested keys are CSS selectors
    (``&`` substitution or descendant).
    """
    flat_props = []
    nested = []
    for key, value in style.items():
        if isinstance(value, dict):
            child_scope = key.replace("&", scope) if "&" in key else _join(scope, key)
            nested.append((value, child_scope))
        else:
            flat_props.append(f"{_kebab(key)}: {value};")
    if flat_props:
        blocks.append(f"{scope} {{ {' '.join(flat_props)} }}")
    for sub_style, child_scope in nested:
        _emit_nested(sub_style, child_scope, blocks)
