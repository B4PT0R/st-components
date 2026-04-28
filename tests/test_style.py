"""
Tests for the inline-style feature on Elements.

Two layers:
1. compile_style() — pure dict → CSS translation.
2. The render-time integration — Element auto-accepts a `style=` kwarg, the
   framework wraps the render in a keyed st.container and injects a scoped
   <style> block; nothing leaks into the underlying st.* call.
"""
import pytest

from st_components.core import App, Component
from st_components.core.style import compile_style, style_scope_key
from st_components.elements import button, container, markdown, text_input

from tests._mock import _mock_st


# ---------------------------------------------------------------------------
# 1. compile_style() — pure
# ---------------------------------------------------------------------------

def test_compile_style_camelcase_to_kebab():
    css = compile_style({"backgroundColor": "red", "fontSize": "16px"}, ".scope")
    assert css == ".scope { background-color: red; font-size: 16px; }"


def test_compile_style_kebab_passes_through():
    css = compile_style({"background-color": "red"}, ".scope")
    assert css == ".scope { background-color: red; }"


def test_compile_style_numeric_values():
    css = compile_style({"opacity": 0.5, "z-index": 100}, ".scope")
    assert "opacity: 0.5" in css
    assert "z-index: 100" in css


def test_compile_style_pseudo_classes_with_ampersand():
    css = compile_style(
        {"color": "black", "&:hover": {"color": "red"}, "&:focus": {"borderColor": "blue"}},
        ".scope",
    )
    assert ".scope { color: black; }" in css
    assert ".scope:hover { color: red; }" in css
    assert ".scope:focus { border-color: blue; }" in css


def test_compile_style_descendant_selectors():
    css = compile_style(
        {"& button": {"color": "red"}, "& > div > p": {"margin": "0"}},
        ".scope",
    )
    assert ".scope button { color: red; }" in css
    assert ".scope > div > p { margin: 0; }" in css


def test_compile_style_bare_descendant_no_ampersand():
    """Keys without `&` are treated as descendant selectors."""
    css = compile_style({"button": {"color": "red"}}, ".scope")
    assert ".scope button { color: red; }" in css


def test_compile_style_deep_nesting():
    css = compile_style(
        {"&:hover": {"& button": {"color": "red"}}},
        ".scope",
    )
    assert ".scope:hover button { color: red; }" in css


def test_compile_style_parent_block_emitted_first():
    """Flat props on the parent must come before nested rules — cascade order."""
    css = compile_style(
        {"&:hover": {"color": "blue"}, "color": "black", "& span": {"color": "green"}},
        ".scope",
    )
    lines = [line for line in css.split("\n") if line]
    assert lines[0].startswith(".scope { ")  # parent first
    assert ".scope:hover" in lines[1] or ".scope:hover" in lines[2]
    assert ".scope span" in lines[1] or ".scope span" in lines[2]


def test_compile_style_rejects_non_dict():
    with pytest.raises(TypeError, match="must be a dict"):
        compile_style("color: red", ".scope")
    with pytest.raises(TypeError, match="must be a dict"):
        compile_style(["color", "red"], ".scope")


def test_style_scope_key_replaces_dots():
    """Scope key must be a CSS-class-safe identifier (no dots that would
    otherwise need backslash-escaping in selectors)."""
    assert style_scope_key("app.page.button.raw") == "stcstyle__app__page__button__raw"
    assert "." not in style_scope_key("a.b.c.d")


# ---------------------------------------------------------------------------
# 2. Render-time integration
# ---------------------------------------------------------------------------

def test_style_kwarg_accepted_by_every_element_subclass():
    """The __init_subclass__ wrap must add `style=` to every Element subclass
    without touching their explicit signatures."""
    # Spot-check a handful of unrelated elements
    button(key="b", style={"color": "red"})
    text_input(key="t", style={"color": "red"})("Label")
    container(key="c", style={"color": "red"})
    markdown(key="m", style={"color": "red"})("body")


def test_style_does_not_leak_into_st_call():
    """The style kwarg must be popped before render_func runs — st.* must
    never receive it (Streamlit raises on unknown kwargs)."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    captured_kw = {}
    def fake_button(*a, **kw):
        captured_kw.update(kw)
        return False
    _mock_st.button.side_effect = fake_button

    class Page(Component):
        def render(self):
            return button(key="b", style={"color": "red"})("Click")

    App()(Page(key="page")).render()

    assert "style" not in captured_kw, (
        "style= must not leak into the underlying st.button call — "
        f"got kwargs: {sorted(captured_kw)}"
    )


def test_styled_element_emits_scoped_style_block():
    """When style= is set, a <style>.st-key-<scope>{...}</style> block must
    be injected via st.html scoped to a container key derived from the
    element path."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return button(key="b", style={"backgroundColor": "red", "padding": "10px"})(
                "Click"
            )

    App()(Page(key="page")).render()

    style_blocks = [c for c in html_calls if "<style>" in c]
    assert style_blocks, f"expected a <style> block in st.html calls, got {html_calls}"
    block = style_blocks[0]
    expected_scope = "stcstyle__app__page__b"
    assert f".st-key-{expected_scope}" in block
    assert "background-color: red" in block
    assert "padding: 10px" in block


def test_styled_element_wraps_in_scoped_container():
    """The framework must call st.container(key=<scope>) so Streamlit emits
    the .st-key-<scope> wrapper class the CSS rules target."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    container_calls = []
    def fake_container(*a, **kw):
        container_calls.append(kw)
        return slot()
    _mock_st.container.side_effect = fake_container

    class Page(Component):
        def render(self):
            return button(key="b", style={"color": "red"})("Click")

    App()(Page(key="page")).render()

    scope_calls = [c for c in container_calls if str(c.get("key", "")).startswith("stcstyle__")]
    assert scope_calls, (
        f"expected a st.container(key='stcstyle__...') call, got {container_calls}"
    )
    assert scope_calls[0]["key"] == "stcstyle__app__page__b"


def test_no_style_no_wrapper_no_style_block():
    """Without style=, the framework must NOT add an extra container wrap or
    inject a style block — zero overhead for unstyled elements."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    container_calls = []
    def fake_container(*a, **kw):
        container_calls.append(kw)
        return slot()
    _mock_st.container.side_effect = fake_container

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return button(key="b")("Click")  # no style

    App()(Page(key="page")).render()

    scope_calls = [c for c in container_calls if str(c.get("key", "")).startswith("stcstyle__")]
    assert not scope_calls, "no style → no wrapping container should be added"
    style_blocks = [c for c in html_calls if "<style>" in c]
    assert not style_blocks, "no style → no <style> block should be injected"


def test_style_works_on_layout_container():
    """Style on a container element scopes correctly — important because
    layout containers nest children."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    container_calls = []
    def fake_container(*a, **kw):
        container_calls.append(kw)
        return slot()
    _mock_st.container.side_effect = fake_container

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return container(key="card", style={"backgroundColor": "lightblue"})

    App()(Page(key="page")).render()

    scope_calls = [c for c in container_calls if str(c.get("key", "")).startswith("stcstyle__")]
    assert scope_calls, "container with style= must trigger the scoped wrapper"
    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    assert "background-color: lightblue" in block


def test_style_invalid_type_raises_at_render():
    """Passing a non-dict style raises a clear TypeError when the element
    actually renders."""
    class Page(Component):
        def render(self):
            return button(key="b", style="color: red")("Click")  # str, not dict

    with pytest.raises(TypeError, match="must be a dict"):
        App()(Page(key="page")).render()


def test_compile_style_with_slots_routes_top_level_to_default_slot():
    """Top-level CSS props land on the default slot, not the wrapper."""
    css = compile_style(
        {"backgroundColor": "red"},
        ".scope",
        slots={"root": "", "input": '[data-baseweb="input"]'},
        default_slot="input",
    )
    assert '.scope [data-baseweb="input"] { background-color: red; }' in css
    assert ".scope { background-color: red; }" not in css


def test_compile_style_with_slots_named_slot_keys_resolve():
    """Top-level keys matching a slot name produce rules at that slot."""
    css = compile_style(
        {"label": {"fontWeight": "bold"}, "input": {"borderColor": "blue"}},
        ".scope",
        slots={"root": "", "input": '[data-baseweb="input"]', "label": "label"},
        default_slot="input",
    )
    assert ".scope label { font-weight: bold; }" in css
    assert '.scope [data-baseweb="input"] { border-color: blue; }' in css


def test_compile_style_root_slot_means_wrapper():
    """The 'root' slot conventionally maps to the wrapper itself."""
    css = compile_style(
        {"root": {"padding": "1rem"}},
        ".scope",
        slots={"root": "", "input": '[data-baseweb="input"]'},
        default_slot="input",
    )
    assert ".scope { padding: 1rem; }" in css


def test_compile_style_ampersand_still_relative_to_wrapper():
    """`&` selectors stay anchored to the scope wrapper, not the default slot.
    (Useful for `:focus-within`, `:has()`, container hover effects.)"""
    css = compile_style(
        {"&:focus-within": {"boxShadow": "0 0 3px blue"}},
        ".scope",
        slots={"root": "", "input": '[data-baseweb="input"]'},
        default_slot="input",
    )
    assert ".scope:focus-within { box-shadow: 0 0 3px blue; }" in css


def test_compile_style_nested_inside_slot_no_slot_lookup():
    """Inside a slot rule, nested keys are plain CSS selectors (no further
    slot lookup) — keeps the model simple."""
    css = compile_style(
        {"input": {"& p": {"color": "red"}}},
        ".scope",
        slots={"root": "", "input": '[data-baseweb="input"]', "p": "WRONG"},
        default_slot="input",
    )
    # `p` inside the input slot is a CSS selector, not a recursive slot lookup
    assert '.scope [data-baseweb="input"] p { color: red; }' in css
    assert "WRONG" not in css


def test_compile_style_invalid_default_slot_raises():
    with pytest.raises(ValueError, match="not a registered slot"):
        compile_style({"color": "red"}, ".scope", slots={"root": ""}, default_slot="missing")


def test_button_style_lands_on_button_slot_end_to_end():
    """End-to-end: style={"backgroundColor": "red"} on a button colors the
    actual <button>, not the wrapper."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return button(key="cta", style={"backgroundColor": "red"})("Click")

    App()(Page(key="page")).render()

    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    expected = ".st-key-stcstyle__app__page__cta"
    assert f"{expected} button {{ background-color: red;" in block
    # And NOT on the bare wrapper
    assert f"{expected} {{ background-color: red;" not in block


def test_markdown_text_slot_is_default():
    """style={"color": "red"} on markdown colors the <p>, not the wrapper."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return markdown(key="msg", style={"color": "red"})("hello")

    App()(Page(key="page")).render()

    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    assert ".st-key-stcstyle__app__page__msg p { color: red;" in block


def test_text_input_slot_keys_target_inner_dom():
    """style={"input": {...}, "label": {...}} on text_input scope to the
    BaseWeb input wrapper and the <label> respectively."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return text_input(
                key="search",
                style={
                    "input": {"borderColor": "blue"},
                    "label": {"fontWeight": "bold"},
                },
            )("Search")

    App()(Page(key="page")).render()

    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    scope = ".st-key-stcstyle__app__page__search"
    assert f'{scope} [data-baseweb="input"] {{ border-color: blue;' in block
    assert f"{scope} label {{ font-weight: bold;" in block


def test_container_no_default_slot_uses_root():
    """Container has only a root slot — top-level props apply to the wrapper."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return container(key="card", style={"backgroundColor": "lightblue"})

    App()(Page(key="page")).render()

    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    # Container has _slots = {} (default) → top-level on wrapper
    assert ".st-key-stcstyle__app__page__card { background-color: lightblue;" in block


def test_style_with_nested_selectors_renders_full_block():
    """End-to-end: nested selectors produce multiple rule blocks scoped to
    the same wrapper class."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.container.return_value = slot()

    html_calls = []
    _mock_st.html.side_effect = lambda content, **kw: html_calls.append(content)

    class Page(Component):
        def render(self):
            return button(
                key="cta",
                style={
                    "backgroundColor": "tomato",
                    "&:hover": {"backgroundColor": "darkred"},
                    "& p": {"fontWeight": "bold"},
                },
            )("Buy")

    App()(Page(key="page")).render()

    block = next((c for c in html_calls if "<style>" in c), None)
    assert block is not None
    expected = ".st-key-stcstyle__app__page__cta"
    # Top-level CSS props on a `button` element land on the `button` slot
    # (the actual <button>), not the wrapper.
    assert f"{expected} button {{ background-color: tomato;" in block
    assert f"{expected}:hover {{ background-color: darkred;" in block
    assert f"{expected} p {{ font-weight: bold;" in block
