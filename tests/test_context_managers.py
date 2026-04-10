"""
Tests for the ContextOrchestrator, set_context, get_context, and derived helpers.
"""
import pytest

from st_components.core._session import get_or_init
from st_components.core.context import (
    KEY,
    CallbackState,
    Context,
    ContextOrchestrator,
    ctx,
    context_value_scope,
    get_active_page_namespace,
    get_context,
    get_context_value,
    get_element_path,
    get_rendering_component,
    set_context,
)
from st_components.core.provider import create_context
from st_components.core.models import ContextData

from tests._mock import _session_data


# ---------------------------------------------------------------------------
# get_or_init
# ---------------------------------------------------------------------------

def test_get_or_init_creates_on_first_access():
    key = "__test_get_or_init__"
    _session_data.pop(key, None)
    result = get_or_init(key, list)
    assert result == []
    assert _session_data[key] is result


def test_get_or_init_returns_existing():
    key = "__test_get_or_init_existing__"
    existing = [1, 2, 3]
    _session_data[key] = existing
    result = get_or_init(key, list)
    assert result is existing


# ---------------------------------------------------------------------------
# set_context: key
# ---------------------------------------------------------------------------

def test_set_context_key_pushes_and_pops():
    with set_context(key="a"):
        assert ctx.stack("key") == ["a"]
        with set_context(key="b"):
            assert ctx.stack("key") == ["a", "b"]
        assert ctx.stack("key") == ["a"]
    assert ctx.stack("key") == []


def test_set_context_key_pops_on_exception():
    with pytest.raises(ValueError):
        with set_context(key="x"):
            raise ValueError("test")
    assert ctx.stack("key") == []


# ---------------------------------------------------------------------------
# set_context: keys (replace entire stack)
# ---------------------------------------------------------------------------

def test_set_context_keys_replaces_and_restores():
    ctx.replace("key", ["original"])
    with set_context(keys=["a", "b", "c"]):
        assert ctx.stack("key") == ["a", "b", "c"]
    assert ctx.stack("key") == ["original"]
    ctx.replace("key", [])


def test_set_context_keys_and_key_compose():
    with set_context(keys=["parent"], key="child"):
        assert ctx.stack("key") == ["parent", "child"]
    assert ctx.stack("key") == []


# ---------------------------------------------------------------------------
# set_context: component
# ---------------------------------------------------------------------------

def test_set_context_component_pushes_and_pops():
    sentinel = object()
    assert get_rendering_component() is None
    with set_context(component=sentinel):
        assert get_rendering_component() is sentinel
    assert get_rendering_component() is None


# ---------------------------------------------------------------------------
# set_context: callback
# ---------------------------------------------------------------------------

def test_set_context_callback_sets_and_restores():
    base = ctx.current("callback")
    assert isinstance(base, CallbackState)
    assert base.element_path is None

    with set_context(callback={"element_path": "a.b", "widget_key": "a.b.raw"}):
        cb = ctx.current("callback")
        assert cb.element_path == "a.b"
        assert cb.widget_key == "a.b.raw"

    after = ctx.current("callback")
    assert after.element_path is None


# ---------------------------------------------------------------------------
# set_context: page
# ---------------------------------------------------------------------------

def test_set_context_page_sets_and_restores():
    assert get_active_page_namespace() is None
    with set_context(page="mypage"):
        assert get_active_page_namespace() == "mypage"
    assert get_active_page_namespace() is None


# ---------------------------------------------------------------------------
# set_context: custom stacks (dynamic)
# ---------------------------------------------------------------------------

def test_set_context_custom_stack():
    with set_context(my_custom="hello"):
        assert ctx.current("my_custom") == "hello"
        with set_context(my_custom="nested"):
            assert ctx.current("my_custom") == "nested"
        assert ctx.current("my_custom") == "hello"
    assert ctx.current("my_custom") is None


def test_set_context_multiple_custom_stacks():
    with set_context(theme="dark", locale="fr"):
        assert ctx.current("theme") == "dark"
        assert ctx.current("locale") == "fr"
    assert ctx.current("theme") is None
    assert ctx.current("locale") is None


# ---------------------------------------------------------------------------
# get_context snapshot
# ---------------------------------------------------------------------------

def test_get_context_returns_snapshot():
    with set_context(key="app", component="comp_obj", page="home"):
        snap = get_context()
        assert snap.key == "app"
        assert snap.component == "comp_obj"
        assert snap.page == "home"
        assert snap.key_stack == ["app"]
        assert snap.element_path == "app"


def test_get_context_includes_custom_stacks():
    with set_context(key="x", my_data="value"):
        snap = get_context()
        assert snap.my_data == "value"
        assert snap.key == "x"


# ---------------------------------------------------------------------------
# get_element_path
# ---------------------------------------------------------------------------

def test_get_element_path_from_key_stack():
    ctx.replace("key", ["app", "form", "name"])
    assert get_element_path() == "app.form.name"
    ctx.replace("key", [])


def test_get_element_path_falls_back_to_callback():
    with set_context(callback={"element_path": "app.btn"}):
        assert get_element_path() == "app.btn"


def test_get_element_path_returns_none_when_empty():
    assert get_element_path() is None


# ---------------------------------------------------------------------------
# KEY
# ---------------------------------------------------------------------------

def test_key_builds_path():
    ctx.replace("key", ["a", "b"])
    assert KEY("c") == "a.b.c"
    ctx.replace("key", [])


def test_key_with_empty_stack():
    assert KEY("root") == "root"


# ---------------------------------------------------------------------------
# context_value_scope (ContextData providers)
# ---------------------------------------------------------------------------

def test_context_value_scope_push_and_pop():
    context = create_context(ContextData())
    assert get_context_value(context) == context.default

    with context_value_scope(context, "override"):
        assert get_context_value(context) == "override"

    assert get_context_value(context) == context.default


def test_context_value_scope_nesting():
    context = create_context(ContextData())

    with context_value_scope(context, "outer"):
        assert get_context_value(context) == "outer"
        with context_value_scope(context, "inner"):
            assert get_context_value(context) == "inner"
        assert get_context_value(context) == "outer"

    assert get_context_value(context) == context.default


# ---------------------------------------------------------------------------
# ContextSchema
# ---------------------------------------------------------------------------

def test_schema_initializes_defaults_on_reset():
    """Fields with list defaults get their initial values on reset."""
    from modict import modict

    class MyContext(Context):
        greeting: list = modict.factory(lambda: ["hello"])
        counter: list = modict.factory(lambda: [0])
        empty: list = modict.factory(list)

    orch = ContextOrchestrator(context_class=MyContext)
    _session_data["_stc.runtime"] = {}
    orch._invalidate()
    orch.reset()

    assert orch.current("greeting") == "hello"
    assert orch.current("counter") == 0
    assert orch.current("empty") is None
    assert orch.stack("empty") == []


def test_schema_dynamic_stacks_still_work():
    """Stacks not in the schema can still be created on the fly."""
    from modict import modict

    class MinimalContext(Context):
        known: list = modict.factory(lambda: ["yes"])

    orch = ContextOrchestrator(context_class=MinimalContext)
    _session_data["_stc.runtime"] = {}
    orch._invalidate()
    orch.reset()

    orch.push("unknown_stack", "dynamic")
    assert orch.current("known") == "yes"
    assert orch.current("unknown_stack") == "dynamic"


def test_schema_reset_restores_defaults():
    """After push + reset, defaults are restored."""
    from modict import modict

    class ModeContext(Context):
        mode: list = modict.factory(lambda: ["default"])

    orch = ContextOrchestrator(context_class=ModeContext)
    _session_data["_stc.runtime"] = {}
    orch._invalidate()
    orch.reset()

    orch.push("mode", "custom")
    assert orch.current("mode") == "custom"

    orch.reset()
    assert orch.current("mode") == "default"


def test_render_schema_has_callback_default():
    """The built-in RenderSchema initializes callback with a CallbackState."""
    ctx.reset()
    cb = ctx.current("callback")
    assert isinstance(cb, CallbackState)
    assert cb.element_path is None
    assert cb.widget_key is None
