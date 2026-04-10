"""
Tests for local refs: fiber overrides, self.ref, get_ref, Ref navigation and overrides.
"""
import pytest

from st_components.core import App, Component, Element, Ref, State, render, fibers, ctx
from st_components.core.context import set_context, get_context
from st_components.elements.factory import get_render_target, render_handle
from st_components.elements.layout.containers import column, columns, tab, tabs, container
from st_components.elements.layout.fragment import fragment
from st_components.core.models import ElementFiber, Fiber

from tests._mock import fake_ctx, _mock_st, _session_data


# ---------------------------------------------------------------------------
# Fiber overrides basics
# ---------------------------------------------------------------------------

def test_fiber_overrides_default_none():
    fiber = Fiber()
    assert fiber.overrides is None


def test_ref_call_stores_children_override():
    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    App()(Page(key="page")).render()

    ref = Ref()
    ref._resolve("app.page.target", "component")
    ref("new_child_a", "new_child_b")

    fiber = fibers().get("app.page.target")
    assert fiber.overrides is not None
    assert fiber.overrides["children"] == ["new_child_a", "new_child_b"]


def test_ref_call_stores_props_override():
    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    App()(Page(key="page")).render()

    ref = Ref()
    ref._resolve("app.page.target", "component")
    ref(color="blue", size=42)

    fiber = fibers().get("app.page.target")
    assert fiber.overrides["props"]["color"] == "blue"
    assert fiber.overrides["props"]["size"] == 42


def test_ref_call_is_chainable():
    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    App()(Page(key="page")).render()

    ref = Ref()
    ref._resolve("app.page.target", "component")
    result = ref(color="blue")("child_a", "child_b")

    assert result is ref
    fiber = fibers().get("app.page.target")
    assert fiber.overrides["props"]["color"] == "blue"
    assert fiber.overrides["children"] == ["child_a", "child_b"]


def test_ref_reset_clears_overrides():
    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    App()(Page(key="page")).render()

    ref = Ref()
    ref._resolve("app.page.target", "component")
    ref("overridden")
    assert fibers()["app.page.target"].overrides is not None

    ref.reset()
    assert fibers()["app.page.target"].overrides is None


# ---------------------------------------------------------------------------
# Overrides applied at render time
# ---------------------------------------------------------------------------

def test_override_children_renders_on_rerun():
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    # First render
    App()(Page(key="page")).render()
    assert "initial" in writes

    # Store override
    ref = Ref()
    ref._resolve("app.page.target", "component")
    ref("overridden")

    # Second render — overridden children should render
    writes.clear()
    App()(Page(key="page")).render()
    assert "overridden" in writes
    assert "initial" not in writes


def test_reset_restores_initial_children():
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    App()(Page(key="page")).render()

    ref = Ref()
    ref._resolve("app.page.target", "component")
    ref("overridden")

    # Render with override
    writes.clear()
    App()(Page(key="page")).render()
    assert "overridden" in writes

    # Reset and render again
    ref.reset()
    writes.clear()
    App()(Page(key="page")).render()
    assert "initial" in writes


# ---------------------------------------------------------------------------
# Component.ref()
# ---------------------------------------------------------------------------

def test_component_ref_self():
    """self.ref() returns a ref to the component itself."""
    class Page(Component):
        def render(self):
            return None

    page = Page(key="page")
    ctx.replace("key", ["app"])
    render(page)
    ctx.replace("key", [])

    ref = page.ref
    assert isinstance(ref, Ref)
    assert ref.path == "app.page"


def test_ref_parent_navigates_up():
    child = Ref._from_path("app.page.panel.results")
    assert child.parent.path == "app.page.panel"
    assert child.parent.parent.path == "app.page"
    assert child.parent.parent.parent.path == "app"
    assert child.parent.parent.parent.parent is None


def test_component_access_returns_ref():
    class Page(Component):
        def render(self):
            return fragment(key="target")("initial")

    page = Page(key="page")
    ctx.replace("key", ["app"])
    render(page)
    ctx.replace("key", [])

    ref = page.get_ref("target")
    assert isinstance(ref, Ref)
    assert ref.path == "app.page.target"


def test_component_access_nested_path():
    class Page(Component):
        def render(self):
            return container(key="panel")(
                fragment(key="results")("initial"),
            )

    page = Page(key="page")
    ctx.replace("key", ["app"])
    render(page)
    ctx.replace("key", [])

    ref = page.get_ref("panel.results")
    assert ref.path == "app.page.panel.results"


# ---------------------------------------------------------------------------
# column scoping still works
# ---------------------------------------------------------------------------

def test_columns_auto_wraps_with_col_keys():
    class slot_ctx:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    col_slots = [slot_ctx(), slot_ctx()]
    _mock_st.columns.side_effect = lambda *a, **kw: col_slots

    paths_seen = []

    class Leaf(Component):
        def render(self):
            paths_seen.append(self._fiber_key)
            return None

    class Root(Component):
        def render(self):
            return columns(key="grid")(
                Leaf(key="a"),
                Leaf(key="b"),
            )

    App()(Root(key="root")).render()
    assert "app.root.grid.col_0.a" in paths_seen
    assert "app.root.grid.col_1.b" in paths_seen


def test_columns_explicit_column_children():
    class slot_ctx:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    col_slots = [slot_ctx(), slot_ctx()]
    _mock_st.columns.side_effect = lambda *a, **kw: col_slots

    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    class Root(Component):
        def render(self):
            return columns(key="grid")(
                column(key="filters")("filter content"),
                column(key="data")("data content"),
            )

    App()(Root(key="root")).render()
    assert writes == ["filter content", "data content"]
