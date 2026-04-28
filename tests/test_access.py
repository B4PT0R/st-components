"""
Tests for access.py: _resolve_path, widget_key, callback, set_state, reset_element.
"""
import pytest

from st_components.core import (
    App, Component, ctx, Element, Ref, State,
    callback, get_state, render, reset_element, set_state, fibers,
)
from st_components.core.access import _resolve_path, widget_key
from st_components.core.models import ElementFiber

from tests._mock import fake_ctx, _mock_st, _session_data


# ---------------------------------------------------------------------------
# _resolve_path
# ---------------------------------------------------------------------------

def test_resolve_path_with_none_returns_element_path():
    ctx.replace("key", [fake_ctx("app"), fake_ctx("form")])
    path = _resolve_path(None)
    ctx.replace("key", [])
    assert path == "app.form"


def test_resolve_path_with_string_returns_string():
    assert _resolve_path("some.path") == "some.path"


def test_resolve_path_with_ref():
    ref = Ref()
    ref._resolve("app.widget", "element")
    assert _resolve_path(ref) == "app.widget"


def test_resolve_path_with_unresolved_ref_raises():
    ref = Ref()
    with pytest.raises(RuntimeError, match="resolved Ref"):
        _resolve_path(ref, fn_name="test_op")


def test_resolve_path_with_wrong_kind_ref_raises():
    ref = Ref()
    ref._resolve("app.comp", "component")
    with pytest.raises(RuntimeError, match="expected a element"):
        _resolve_path(ref, expected_kind="element", fn_name="test_op")


# ---------------------------------------------------------------------------
# widget_key
# ---------------------------------------------------------------------------

def test_widget_key_with_path():
    key = widget_key("app.form.name")
    assert key == "app.form.name.raw"


def test_widget_key_from_context():
    ctx.replace("key", [fake_ctx("app"), fake_ctx("form"), fake_ctx("name")])
    key = widget_key()
    ctx.replace("key", [])
    assert key == "app.form.name.raw"


def test_widget_key_raises_with_no_context():
    ctx.replace("key", [])
    with pytest.raises(RuntimeError, match="requires an element path"):
        widget_key()


def test_widget_key_increments_after_reset():
    path = "app.form.name"
    key1 = widget_key(path)
    reset_element(path)
    key2 = widget_key(path)
    assert key1 != key2
    assert key2.endswith("#1")


# ---------------------------------------------------------------------------
# set_state
# ---------------------------------------------------------------------------

def test_set_state_on_element_raises():
    class Elem(Element):
        def render(self):
            pass

    elem = Elem(key="e")
    ctx.replace("key", [fake_ctx("app")])
    render(elem)
    ctx.replace("key", [])

    with pytest.raises(RuntimeError, match="cannot target an Element"):
        set_state("app.e", count=1)


def test_set_state_on_missing_fiber_raises():
    with pytest.raises(RuntimeError, match="no live fiber"):
        set_state("nonexistent.path", count=1)


def test_set_state_with_invalid_type_raises():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    with pytest.raises(TypeError, match="expected a dict"):
        set_state("app.c", 12345)


def test_set_state_updates_kwargs():
    class Comp(Component):
        class S(State):
            x: int = 0

        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    set_state("app.c", x=42)
    assert get_state("app.c").x == 42


# ---------------------------------------------------------------------------
# callback wrapping
# ---------------------------------------------------------------------------

def test_callback_returns_none_for_none_fn():
    assert callback(None) is None


def test_callback_raises_outside_element_render():
    # No active render context
    with pytest.raises(RuntimeError, match="Element.render"):
        callback(lambda v: v)


# ---------------------------------------------------------------------------
# callback with and without value argument
# ---------------------------------------------------------------------------

def _make_button_runner():
    """Helper: set up a fake button that fires on_click immediately."""
    from st_components.elements.input.buttons import button as btn

    def fake_button(label, key=None, on_click=None, **kw):
        if on_click:
            on_click()

    _mock_st.button.side_effect = fake_button
    return btn


def _make_text_input_runner():
    """Helper: set up a fake text_input that fires on_change immediately."""
    from st_components.elements.input.textual import text_input

    def fake_text_input(label, key=None, on_change=None, value=None, **kw):
        if on_change:
            on_change()

    _mock_st.text_input.side_effect = fake_text_input
    return text_input


# -- method with value arg (on_change) --

def test_callback_method_with_value():
    seen = []
    text_input = _make_text_input_runner()

    class Form(Component):
        def on_name(self, value):
            seen.append(("with_value", value))
        def render(self):
            return text_input(key="name", value="Alice", on_change=self.on_name)("Name")

    _session_data["app.form.name.raw"] = "Alice"
    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == [("with_value", "Alice")]


# -- method without value arg (on_click) --

def test_callback_method_without_value():
    seen = []
    btn = _make_button_runner()

    class Form(Component):
        def on_click(self):
            seen.append("clicked")
        def render(self):
            return btn(key="b", on_click=self.on_click)("Go")

    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == ["clicked"]


# -- lambda with value arg --

def test_callback_lambda_with_value():
    seen = []
    text_input = _make_text_input_runner()

    class Form(Component):
        def render(self):
            return text_input(key="name", value="Bob",
                              on_change=lambda v: seen.append(v))("Name")

    _session_data["app.form.name.raw"] = "Bob"
    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == ["Bob"]


# -- lambda without value arg --

def test_callback_lambda_without_value():
    seen = []
    btn = _make_button_runner()

    class Form(Component):
        def render(self):
            return btn(key="b", on_click=lambda: seen.append("fire"))("Go")

    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == ["fire"]


# -- free function with value --

def test_callback_free_function_with_value():
    seen = []
    text_input = _make_text_input_runner()

    def handler(value):
        seen.append(value)

    class Form(Component):
        def render(self):
            return text_input(key="name", value="Eve", on_change=handler)("Name")

    _session_data["app.form.name.raw"] = "Eve"
    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == ["Eve"]


# -- free function without value --

def test_callback_free_function_without_value():
    seen = []
    btn = _make_button_runner()

    def handler():
        seen.append("ok")

    class Form(Component):
        def render(self):
            return btn(key="b", on_click=handler)("Go")

    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    assert seen == ["ok"]


# -- lambda with default-arg closure (on_click=lambda i=i: ...) --

def test_callback_lambda_default_arg_only():
    """lambda i=i: ... has one param but it's keyword-with-default, not positional for the value."""
    seen = []
    btn = _make_button_runner()

    class Form(Component):
        def render(self):
            return btn(key="b", on_click=lambda i=42: seen.append(i))("Go")

    ctx.replace("key", [fake_ctx("app")])
    render(Form(key="form"))
    ctx.replace("key", [])
    # The lambda has one positional param (i), so the framework passes the value into it.
    # This is fine — the user chose to shadow it with a default. The value wins.
    assert len(seen) == 1


# ---------------------------------------------------------------------------
# reset_element on non-existent fiber is safe
# ---------------------------------------------------------------------------

def test_reset_element_on_missing_fiber_does_not_raise():
    # Just verify no crash — the fiber doesn't exist, but the revision still advances
    reset_element("nonexistent.element")
    key = widget_key("nonexistent.element")
    assert "#1" in key


# ---------------------------------------------------------------------------
# callback captures rerun_scope at wrap time (regression test)
# ---------------------------------------------------------------------------

def test_callback_captures_rerun_scope_at_wrap_time():
    """When a callback is wrapped inside a scoped fragment's render, it must
    remember that fragment's ``rerun_scope`` so that ``rerun()`` / ``wait()``
    calls fired by Streamlit later (outside the fragment's context) still
    target the correct scope.

    Otherwise rerun(wait=...) inside a fragment-scoped callback would silently
    fall back to the ``"app"`` scope and either block the whole app or never
    reach the fragment's ``check_rerun()``.
    """
    captured_in_callback = []

    # Build the wrapped callback while a fragment scope is active in context
    btn = _make_button_runner()

    class Form(Component):
        def on_click(self):
            # When the callback fires, the rerun_scope from wrap time must
            # still be visible in context — even if we're no longer inside
            # the fragment's set_context block at fire time.
            captured_in_callback.append(ctx.current("rerun_scope", "app"))

        def render(self):
            return btn(key="b", on_click=self.on_click)("Go")

    # Simulate fragment context during render
    ctx.replace("key", [fake_ctx("app")])
    ctx.push("rerun_scope", "app.frag.scoped")
    try:
        render(Form(key="form"))
    finally:
        ctx.pop("rerun_scope")
        ctx.replace("key", [])

    # The fake button runner fired the callback during render, while
    # rerun_scope was still on the stack. To test the wrap-time capture
    # specifically, we'd need to fire after pop — but the helper fires
    # immediately. Confirm at least that the scope was visible at fire time
    # (which is what the captured-at-wrap-time mechanism guarantees).
    assert captured_in_callback == ["app.frag.scoped"]


def test_callback_preserves_scope_when_fired_outside_render_context():
    """Direct test of the wrap-time capture: build the callback inside a
    fragment-scope context, then fire it outside that context — the scope
    must still be reachable inside the callback body."""
    captured = []

    class Probe(Element):
        def render(self):
            return None  # not used here

    # Manually wrap a callback while inside a rerun_scope context
    def cb():
        captured.append(ctx.current("rerun_scope", "app"))

    ctx.replace("key", [fake_ctx("app"), fake_ctx("frag")])
    elem = Probe(key="frag")
    elem._fiber_key = "app.frag"
    fibers()["app.frag"] = ElementFiber(path="app.frag", widget_key="app.frag.raw")

    # Push rerun_scope and wrap the callback while it's active
    ctx.push("rerun_scope", "app.frag.scope_id")
    ctx.push("component", elem)
    try:
        wrapped = callback(cb)
    finally:
        ctx.pop("component")
        ctx.pop("rerun_scope")
        ctx.replace("key", [])

    # Now fire the wrapped callback OUTSIDE the fragment's render context
    assert ctx.current("rerun_scope", "app") == "app", "fragment scope must be popped"
    wrapped()
    # The callback body saw the captured scope, not the bare default
    assert captured == ["app.frag.scope_id"]
