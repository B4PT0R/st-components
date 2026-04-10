"""
Tests for store internals: _cleanup_effect_slots, mark_subtree_keep_alive,
shared state management, and render cycle mechanics.
"""
import pytest

from st_components.core import App, Component, State, render, fibers
from st_components.core.models import HookSlot, Fiber, ElementFiber
from st_components.core.store import (
    _cleanup_effect_slots,
    begin_render_cycle,
    clear_shared_state,
    declare_shared_state,
    end_render_cycle,
    get_shared_state,
    mark_subtree_keep_alive,
    register_component,
    resolve_component,
    shared_states,
    track_rendered_fiber,
    unregister_component,
)

from tests._mock import _session_data


# ---------------------------------------------------------------------------
# _cleanup_effect_slots
# ---------------------------------------------------------------------------

def test_cleanup_effect_slots_runs_and_clears_effect_cleanups():
    cleanups = []
    hooks = [
        HookSlot(kind="memo", initialized=True, value=42),
        HookSlot(kind="effect", initialized=True, cleanup=lambda: cleanups.append("a")),
        HookSlot(kind="effect", initialized=True, cleanup=lambda: cleanups.append("b")),
        HookSlot(kind="effect", initialized=True, cleanup=None),
    ]

    _cleanup_effect_slots(hooks)

    assert cleanups == ["a", "b"]
    assert hooks[1].cleanup is None
    assert hooks[2].cleanup is None


def test_cleanup_effect_slots_skips_non_effect_hooks():
    hooks = [
        HookSlot(kind="memo", initialized=True, cleanup=lambda: None),
        HookSlot(kind="ref", initialized=True),
    ]
    _cleanup_effect_slots(hooks)  # should not raise


# ---------------------------------------------------------------------------
# mark_subtree_keep_alive
# ---------------------------------------------------------------------------

def test_mark_subtree_keep_alive_marks_prefix_and_descendants():
    fibers()["app.panel"] = Fiber()
    fibers()["app.panel.child"] = Fiber()
    fibers()["app.panel.child.leaf"] = Fiber()
    fibers()["app.other"] = Fiber()

    mark_subtree_keep_alive("app.panel")

    assert fibers()["app.panel"].keep_alive is True
    assert fibers()["app.panel.child"].keep_alive is True
    assert fibers()["app.panel.child.leaf"].keep_alive is True
    assert fibers()["app.other"].keep_alive is False


def test_mark_subtree_keep_alive_does_not_match_partial_prefix():
    fibers()["app.panel"] = Fiber()
    fibers()["app.panelx"] = Fiber()

    mark_subtree_keep_alive("app.panel")

    assert fibers()["app.panel"].keep_alive is True
    assert fibers()["app.panelx"].keep_alive is False


# ---------------------------------------------------------------------------
# Component registry
# ---------------------------------------------------------------------------

def test_register_resolve_unregister():
    sentinel = object()
    register_component("test:abc", sentinel)
    assert resolve_component("test:abc") is sentinel

    unregister_component("test:abc")
    assert resolve_component("test:abc") is None


def test_resolve_component_returns_none_for_none():
    assert resolve_component(None) is None


def test_unregister_component_ignores_none():
    unregister_component(None)  # should not raise


def test_unregister_component_ignores_missing():
    unregister_component("nonexistent:xyz")  # should not raise


# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

def test_declare_shared_state_with_class():
    class WorkspaceState(State):
        team: str = "core"

    ws = declare_shared_state("workspace", WorkspaceState)
    assert isinstance(ws, WorkspaceState)
    assert ws.team == "core"

    # Second call returns same instance
    ws2 = declare_shared_state("workspace", WorkspaceState)
    assert ws2 is ws


def test_declare_shared_state_with_instance():
    class AuthState(State):
        user: str = ""

    instance = AuthState(user="alice")
    auth = declare_shared_state("auth", instance)
    assert auth is instance
    assert auth.user == "alice"


def test_get_shared_state_raises_when_undeclared():
    with pytest.raises(RuntimeError, match="not declared"):
        get_shared_state("nonexistent")


def test_clear_shared_state_specific():
    declare_shared_state("a", State())
    declare_shared_state("b", State())

    clear_shared_state("a")
    assert "a" not in shared_states()
    assert "b" in shared_states()


def test_clear_shared_state_all():
    declare_shared_state("x", State())
    declare_shared_state("y", State())

    clear_shared_state()
    assert len(shared_states()) == 0


def test_shared_state_invalid_spec_raises():
    with pytest.raises(TypeError, match="State instance or a State subclass"):
        declare_shared_state("bad", "not a state")


# ---------------------------------------------------------------------------
# Render cycle: stale fibers are cleaned up
# ---------------------------------------------------------------------------

def test_stale_component_unmounted_after_render_cycle():
    unmounted = []

    class Child(Component):
        def component_did_unmount(self):
            unmounted.append(self.key)

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if self.props.get("show"):
                return Child(key="child")
            return None

    App()(Root(key="root", show=True)).render()
    assert "app.root.child" in fibers()

    App()(Root(key="root", show=False)).render()
    assert "app.root.child" not in fibers()
    assert unmounted == ["child"]


def test_stale_element_effect_cleaned_up():
    cleanups = []

    class Leaf(Component):
        def render(self):
            from st_components.core.hooks import use_effect
            use_effect(lambda: (lambda: cleanups.append("cleaned")), deps=[])
            return None

    class Root(Component):
        def render(self):
            if self.props.get("show"):
                return Leaf(key="leaf")
            return None

    App()(Root(key="root", show=True)).render()
    App()(Root(key="root", show=False)).render()

    assert cleanups == ["cleaned"]
