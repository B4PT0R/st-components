"""
Tests for Component/Element mount/unmount error paths, _default_output_prop,
Value, Anchor, and sync_state.
"""
import pytest

from st_components.core import Component, Element, Props, State, ctx, render, fibers
from st_components.core.base import Anchor, Value, to_tuple
from st_components.core.models import ElementState

from tests._mock import fake_ctx, _mock_st, _session_data


# ---------------------------------------------------------------------------
# mount / unmount error paths
# ---------------------------------------------------------------------------

def test_component_mount_when_already_mounted_raises():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    assert comp.is_mounted
    with pytest.raises(RuntimeError, match="already mounted"):
        comp.mount()


def test_component_unmount_when_not_mounted_raises():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="c")
    assert not comp.is_mounted
    with pytest.raises(RuntimeError, match="not already mounted"):
        comp.unmount()


def test_element_mount_when_already_mounted_raises():
    class Elem(Element):
        def render(self):
            pass

    elem = Elem(key="e")
    ctx.replace("key", [fake_ctx("app")])
    render(elem)
    ctx.replace("key", [])

    assert elem.is_mounted
    with pytest.raises(RuntimeError, match="already mounted"):
        elem.mount()


# ---------------------------------------------------------------------------
# Component.unmount cleans up fiber
# ---------------------------------------------------------------------------

def test_component_unmount_removes_fiber():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    assert "app.c" in fibers()
    comp.unmount()
    assert "app.c" not in fibers()
    assert not comp.is_mounted


# ---------------------------------------------------------------------------
# _default_output_prop
# ---------------------------------------------------------------------------

def test_default_output_prop_returns_prop_value_when_raw_is_none():
    class MyInput(Element):
        _default_output_prop = "value"

        def render(self):
            pass

    elem = MyInput(key="inp", value="hello")
    assert elem.get_output(None) == "hello"


def test_default_output_prop_returns_raw_when_not_none():
    class MyInput(Element):
        _default_output_prop = "value"

        def render(self):
            pass

    elem = MyInput(key="inp", value="default")
    assert elem.get_output("actual") == "actual"


def test_default_output_prop_none_when_no_prop_set():
    class MyInput(Element):
        _default_output_prop = "value"

        def render(self):
            pass

    elem = MyInput(key="inp")
    assert elem.get_output(None) is None


def test_default_output_prop_not_set_returns_none():
    class PlainElem(Element):
        def render(self):
            pass

    elem = PlainElem(key="e")
    assert elem.get_output(None) is None


# ---------------------------------------------------------------------------
# Value element
# ---------------------------------------------------------------------------

def test_value_element_renders_via_st_write():
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    val = Value(key="v", value=42)
    val.render()

    assert writes == [42]


# ---------------------------------------------------------------------------
# Anchor element
# ---------------------------------------------------------------------------

def test_anchor_renders_children():
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    anchor = Anchor(key="a")("hello", "world")
    anchor.render()

    assert writes == ["hello", "world"]


# ---------------------------------------------------------------------------
# to_tuple
# ---------------------------------------------------------------------------

def test_to_tuple_wraps_non_tuples():
    assert to_tuple("x") == ("x",)
    assert to_tuple(42) == (42,)
    assert to_tuple(None) == (None,)


def test_to_tuple_preserves_tuples():
    t = (1, 2)
    assert to_tuple(t) is t


# ---------------------------------------------------------------------------
# sync_state
# ---------------------------------------------------------------------------

def test_sync_state_creates_callback_that_updates_state():
    class Comp(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(name="")

        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    sync = comp.sync_state("name")
    sync("Alice")
    assert comp.state.name == "Alice"


# ---------------------------------------------------------------------------
# key setter raises
# ---------------------------------------------------------------------------

def test_component_key_setter_raises():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="c")
    with pytest.raises(RuntimeError, match="Can't set"):
        comp.key = "other"


# ---------------------------------------------------------------------------
# state setter only works when unmounted
# ---------------------------------------------------------------------------

def test_state_setter_works_when_unmounted():
    class Comp(Component):
        class S(State):
            x: int = 0

        def render(self):
            pass

    comp = Comp(key="c")
    comp.state = {"x": 5}
    assert comp.state.x == 5


def test_state_setter_noop_when_mounted():
    class Comp(Component):
        class S(State):
            x: int = 0

        def render(self):
            pass

    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])

    comp.state = {"x": 99}
    # mounted: setter is a no-op, state should still be 0
    assert comp.state.x == 0


# ---------------------------------------------------------------------------
# render_to_element recursion guard
# ---------------------------------------------------------------------------

def test_render_to_element_detects_deep_chain():
    from st_components.core.base import render_to_element, _MAX_RENDER_DEPTH

    class Deep(Component):
        _decorate_render = lambda self: None  # bypass decorator

        def render(self):
            return Deep(key="d")

    with pytest.raises(RecursionError, match="infinite loop"):
        render_to_element(Deep(key="d"))


# ---------------------------------------------------------------------------
# _cleanup_effect_slots runs all cleanups even if one raises
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

def test_component_repr_unmounted():
    class Comp(Component):
        def render(self):
            pass
    comp = Comp(key="c")
    r = repr(comp)
    assert "Comp" in r
    assert "unmounted" in r
    assert "'c'" in r


def test_component_repr_mounted():
    class Comp(Component):
        def render(self):
            pass
    comp = Comp(key="c")
    ctx.replace("key", [fake_ctx("app")])
    render(comp)
    ctx.replace("key", [])
    r = repr(comp)
    assert "mounted" in r
    assert "app.c" in r


def test_ref_repr():
    from st_components.core import Ref
    ref = Ref()
    assert "unresolved" in repr(ref)
    ref._resolve("app.widget", "element")
    assert "app.widget" in repr(ref)


# ---------------------------------------------------------------------------
# auto-key
# ---------------------------------------------------------------------------

def test_auto_key_assigned_by_parent_call():
    from st_components.core import App

    class Child(Component):
        def render(self):
            return None

    class Parent(Component):
        def render(self):
            return (Child(), Child())

    App()(Parent(key="p")).render()

    assert "app.p.Child_0" in fibers()
    assert "app.p.Child_1" in fibers()


def test_auto_key_explicit_takes_priority():
    from st_components.core import App

    class Child(Component):
        def render(self):
            return None

    class Parent(Component):
        def render(self):
            return (Child(key="explicit"), Child())

    App()(Parent(key="p")).render()

    assert "app.p.explicit" in fibers()
    assert "app.p.Child_1" in fibers()


def test_auto_key_standalone_component():
    from st_components.core import App

    class Solo(Component):
        def render(self):
            return None

    App()(Solo()).render()
    # root gets class name as key
    assert "app.Solo" in fibers()


def test_auto_key_children_via_call():
    """Children passed via __call__ get auto-keyed."""
    class Child(Component):
        def render(self):
            return None

    parent = Component.__new__(Component)
    parent.props = Props(key="p")
    parent(Child(), Child(key="explicit"), Child())

    keys = [c.props.key for c in parent.children]
    assert keys == ["Child_0", "explicit", "Child_2"]


# ---------------------------------------------------------------------------
# cleanup effects error propagation
# ---------------------------------------------------------------------------

def test_cleanup_effect_slots_runs_all_even_on_error():
    from st_components.core.store import _cleanup_effect_slots
    from st_components.core.models import HookSlot

    called = []
    hooks = [
        HookSlot(kind="effect", initialized=True, cleanup=lambda: (_ for _ in ()).throw(ValueError("boom"))),
        HookSlot(kind="effect", initialized=True, cleanup=lambda: called.append("second")),
    ]

    # First cleanup raises, but second should still run
    with pytest.raises(ValueError, match="boom"):
        _cleanup_effect_slots(hooks)

    assert called == ["second"]
    assert hooks[0].cleanup is None
    assert hooks[1].cleanup is None
