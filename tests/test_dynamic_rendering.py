"""
Serious end-to-end tests for the two cornerstone features of st-components:

1. Scoped attribute access for refs by key (Component.__getattr__ / Ref.__getattr__).
2. Dynamic rendering via fiber overrides (callbacks mutating any node in the tree).

These tests go beyond the unit checks in test_local_refs.py — they exercise the
full callback → override → rerun cycle in scenarios closer to how a real app
would use these features (sibling-to-sibling overrides, deep paths, key collisions
across different branches, repeated overrides, props vs children semantics, etc.).
"""
import pytest

from st_components.core import App, Component, Ref, State, fibers
from st_components.elements import button, container, markdown, metric
from st_components.elements.layout.containers import column, columns
from st_components.elements.layout.fragment import fragment

from tests._mock import _mock_st, _session_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_writes():
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)
    return writes


def _capture_markdowns():
    md = []
    _mock_st.markdown.side_effect = lambda body, **_kw: md.append(body)
    return md


def _capture_metrics():
    calls = []
    _mock_st.metric.side_effect = lambda label, **kw: calls.append((label, kw))
    return calls


def _capture_columns(n):
    """Make st.columns(n) return n trivial slot context managers."""
    class slot:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    _mock_st.columns.side_effect = lambda *a, **kw: [slot() for _ in range(n)]


# ===========================================================================
# 1. Scoped attribute access via __getattr__
# ===========================================================================

def test_same_key_in_two_branches_resolves_to_distinct_paths():
    """A common bug class: two siblings with the same inner key collide."""
    seen = []

    class Leaf(Component):
        def render(self):
            seen.append(self._fiber_key)
            return None

    class Branch(Component):
        def render(self):
            return container(key="inner")(Leaf(key="leaf"))

    class Root(Component):
        def render(self):
            return container(key="page")(
                Branch(key="left"),
                Branch(key="right"),
            )

    App()(Root(key="root")).render()
    assert "app.root.page.left.inner.leaf" in seen
    assert "app.root.page.right.inner.leaf" in seen


def test_attribute_chain_builds_correct_absolute_path():
    """self.a.b.c must resolve to "<self>.a.b.c" — the whole point of scoped access."""
    captured = {}

    class Page(Component):
        def render(self):
            captured["self_ref"] = self.ref.path
            captured["one"] = self.a.path
            captured["two"] = self.a.b.path
            captured["three"] = self.a.b.c.path
            return None

    App()(Page(key="page")).render()
    assert captured["self_ref"] == "app.page"
    assert captured["one"] == "app.page.a"
    assert captured["two"] == "app.page.a.b"
    assert captured["three"] == "app.page.a.b.c"


def test_root_navigation_is_absolute():
    """self.root reaches the App regardless of nesting depth."""
    captured = {}

    class Leaf(Component):
        def render(self):
            captured["root"] = self.root.path
            captured["abs"] = self.root.foo.bar.path
            return None

    class Mid(Component):
        def render(self):
            return Leaf(key="leaf")

    class Top(Component):
        def render(self):
            return container(key="x")(container(key="y")(Mid(key="mid")))

    App()(Top(key="top")).render()
    assert captured["root"] == "app"
    assert captured["abs"] == "app.foo.bar"


def test_parent_chain_walks_up_to_none():
    ref = Ref._from_path("app.page.panel.results")
    chain = []
    cur = ref
    while cur is not None:
        chain.append(cur.path)
        cur = cur.parent
    assert chain == ["app.page.panel.results", "app.page.panel", "app.page", "app"]


def test_underscore_attributes_raise_attribute_error_on_ref():
    """Internal/dunder names must not silently produce refs — that would mask
    typos and break introspection (hasattr, __reduce__, etc.)."""
    ref = Ref._from_path("app.page")
    with pytest.raises(AttributeError):
        ref._private  # noqa: B018
    with pytest.raises(AttributeError):
        ref.__custom__  # noqa: B018


def test_underscore_attributes_raise_on_component():
    class Page(Component):
        def render(self):
            return None

    page = Page(key="page")
    App()(page).render()
    with pytest.raises(AttributeError):
        page._not_a_real_thing  # noqa: B018


def test_normal_attributes_are_not_shadowed_by_getattr():
    """state, props, methods, instance attrs must take precedence over the
    ref-navigation fallback. Otherwise self.state would become a Ref."""
    captured = {}

    class Page(Component):
        class S(State):
            label: str = "hello"

        def my_method(self):
            return "method-result"

        def render(self):
            captured["state_label"] = self.state.label
            captured["state_is_state"] = isinstance(self.state, State)
            captured["method"] = self.my_method()
            captured["key_attr"] = self.key
            # And ref nav still works alongside:
            captured["nav"] = self.some_child.path
            return None

    App()(Page(key="page")).render()
    assert captured["state_label"] == "hello"
    assert captured["state_is_state"] is True
    assert captured["method"] == "method-result"
    assert captured["key_attr"] == "page"
    assert captured["nav"] == "app.page.some_child"


# ===========================================================================
# 2. Dynamic rendering — full callback → override → rerun cycles
# ===========================================================================

def test_sibling_to_sibling_override_via_callback():
    """The flagship use case: a button in one branch overrides a fragment in
    another branch, accessed via the common parent's scoped path."""
    writes = _capture_writes()

    class Page(Component):
        def fill(self):
            # Navigate from self through an intermediate container to the
            # sibling fragment — exactly what the example uses in practice.
            self.box.results("row 1", "row 2", "row 3")

        def render(self):
            return container(key="box")(
                fragment(key="results")("empty"),
                button(key="load", on_click=self.fill)("Load"),
            )

    page = Page(key="page")
    App()(page).render()
    assert "empty" in writes

    # Simulate the on_click callback firing on the rendered instance
    page.fill()

    # Re-render — overridden children must replace the initial ones
    writes.clear()
    App()(Page(key="page")).render()
    assert "row 1" in writes
    assert "row 2" in writes
    assert "row 3" in writes
    assert "empty" not in writes


def test_deep_nested_override_resolves_correctly():
    """Override a fiber 4 levels deep via chained attribute access."""
    writes = _capture_writes()

    class Page(Component):
        def render(self):
            return container(key="lvl1")(
                container(key="lvl2")(
                    container(key="lvl3")(
                        fragment(key="target")("initial-deep"),
                    ),
                ),
            )

    page = Page(key="page")
    App()(page).render()
    assert "initial-deep" in writes

    # Override deep child via attribute chain
    page.lvl1.lvl2.lvl3.target("DEEP-OVERRIDE")
    fiber = fibers().get("app.page.lvl1.lvl2.lvl3.target")
    assert fiber is not None, "deep path must have a fiber after first render"
    assert fiber.overrides["children"] == ["DEEP-OVERRIDE"]

    writes.clear()
    App()(Page(key="page")).render()
    assert "DEEP-OVERRIDE" in writes
    assert "initial-deep" not in writes


def test_repeated_children_override_replaces_does_not_accumulate():
    """Calling ref(*children) twice must replace, not append. Otherwise lists
    would grow unbounded across reruns."""
    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()

    page.t("a", "b")
    page.t("x", "y", "z")

    fiber = fibers().get("app.page.t")
    assert fiber.overrides["children"] == ["x", "y", "z"]


def test_props_override_persists_across_children_only_re_call():
    """ref(border=True)('a'); ref('b')  →  border still True, children=['b']."""
    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()

    page.t(border=True, color="red")("a")
    page.t("b", "c")  # children-only update

    fiber = fibers().get("app.page.t")
    assert fiber.overrides["props"] == {"border": True, "color": "red"}
    assert fiber.overrides["children"] == ["b", "c"]


def test_props_override_merges_on_repeated_calls():
    """ref(a=1); ref(b=2)  →  both props present (merge, not replace)."""
    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()

    page.t(a=1, shared="first")
    page.t(b=2, shared="second")

    fiber = fibers().get("app.page.t")
    assert fiber.overrides["props"] == {"a": 1, "b": 2, "shared": "second"}


def test_reset_clears_both_props_and_children():
    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()

    page.t(border=True)("override")
    assert fibers()["app.page.t"].overrides is not None

    page.t.reset()
    assert fibers()["app.page.t"].overrides is None


def test_override_persists_across_multiple_reruns_until_reset():
    writes = _capture_writes()

    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()
    page.t("OVERRIDDEN")

    # Three consecutive reruns — override survives all
    for _ in range(3):
        writes.clear()
        App()(Page(key="page")).render()
        assert "OVERRIDDEN" in writes
        assert "initial" not in writes

    # Reset and rerun — original content returns
    page.t.reset()
    writes.clear()
    App()(Page(key="page")).render()
    assert "initial" in writes
    assert "OVERRIDDEN" not in writes


def test_element_props_override_changes_widget_call():
    """Override props on an Element node — the underlying st.metric call must
    see the new props on the next render."""
    metric_calls = _capture_metrics()

    class Page(Component):
        def render(self):
            return metric(key="m", label="Status", value="OFF")

    page = Page(key="page")
    App()(page).render()
    assert metric_calls[-1][0] == "Status"
    assert metric_calls[-1][1]["value"] == "OFF"

    # Override the element's props from a "callback"
    page.m(label="Status", value="OK", delta=42)

    metric_calls.clear()
    App()(Page(key="page")).render()
    assert metric_calls[-1][0] == "Status"
    assert metric_calls[-1][1]["value"] == "OK"
    assert metric_calls[-1][1]["delta"] == 42


def test_reset_on_unknown_path_is_noop():
    """Calling .reset() on a ref to a non-existent fiber must not crash —
    common when refs outlive the node they pointed to."""
    class Page(Component):
        def render(self):
            return None

    page = Page(key="page")
    App()(page).render()

    # Path has no fiber — should be silent no-op, not an exception
    page.does_not_exist.reset()
    page.does_not_exist.further.deeper.reset()


def test_override_call_on_unknown_path_is_noop():
    class Page(Component):
        def render(self):
            return None

    page = Page(key="page")
    App()(page).render()

    # Should not raise even though no such fiber exists
    result = page.ghost(color="red")("orphan")
    assert isinstance(result, Ref)


def test_named_columns_same_key_no_collision():
    """The ColumnDemo case from example 11: two columns each with key='data'
    must produce distinct paths and accept independent overrides."""
    _capture_columns(2)
    writes = _capture_writes()

    class Page(Component):
        def render(self):
            return columns(key="grid")(
                column(key="left")(
                    fragment(key="data")("left-init"),
                ),
                column(key="right")(
                    fragment(key="data")("right-init"),
                ),
            )

    page = Page(key="page")
    App()(page).render()
    assert "left-init" in writes and "right-init" in writes

    # Override only the right column's "data" fragment
    page.grid.right.data("right-FILLED")

    # Sanity: the left fiber is untouched
    left_fiber = fibers().get("app.page.grid.left.data")
    right_fiber = fibers().get("app.page.grid.right.data")
    assert left_fiber.overrides is None
    assert right_fiber.overrides is not None
    assert right_fiber.overrides["children"] == ["right-FILLED"]

    _capture_columns(2)
    writes.clear()
    App()(Page(key="page")).render()
    assert "left-init" in writes  # unchanged
    assert "right-FILLED" in writes
    assert "right-init" not in writes


def test_chain_props_then_children_in_one_expression():
    """ref(border=True)('child') — the chained call must persist BOTH parts."""
    class Page(Component):
        def render(self):
            return fragment(key="t")("initial")

    page = Page(key="page")
    App()(page).render()

    result = page.t(border=True, color="blue")("kid_a", "kid_b")
    assert isinstance(result, Ref)

    fiber = fibers().get("app.page.t")
    assert fiber.overrides["props"] == {"border": True, "color": "blue"}
    assert fiber.overrides["children"] == ["kid_a", "kid_b"]


def test_dynamic_rendering_realistic_workflow():
    """End-to-end: a Dashboard component with Load / Refine / Reset actions —
    each callback uses scoped ref access to mutate a results panel.

    Models the real Streamlit flow: callbacks fire on the most recently
    rendered instance (captured here via a registry list), and each rerun
    creates a fresh instance which picks up state and overrides from the
    persistent fiber."""
    writes = _capture_writes()
    metric_calls = _capture_metrics()

    rendered = []

    class Dashboard(Component):
        class S(State):
            row_count: int = 0

        def __init__(self, **props):
            super().__init__(**props)
            rendered.append(self)

        def load(self):
            self.state.row_count = 100
            self.panel.body(
                metric(key="rows", label="Rows", value=self.state.row_count),
            )

        def refine(self):
            self.state.row_count = 25
            self.panel.body(
                metric(key="rows", label="Rows", value=self.state.row_count),
                metric(key="filtered", label="Filtered", value=True),
            )

        def clear(self):
            self.state.row_count = 0
            self.panel.body.reset()

        def render(self):
            return container(key="panel")(
                fragment(key="body")("nothing-loaded"),
            )

    def rerender():
        """Rerun: build a fresh instance and render it. Returns the rendered
        instance (the one whose callbacks would fire next)."""
        rendered.clear()
        App()(Dashboard(key="dash")).render()
        assert rendered, "Dashboard should have been instantiated and rendered"
        return rendered[-1]

    # Initial render — empty state
    dash = rerender()
    assert "nothing-loaded" in writes
    assert metric_calls == []
    assert dash.state.row_count == 0

    # Click Load → callback on the rendered instance → rerun
    dash.load()
    writes.clear(); metric_calls.clear()
    dash = rerender()
    assert "nothing-loaded" not in writes
    assert any(c[1].get("value") == 100 for c in metric_calls)
    assert dash.state.row_count == 100  # state survived through the fiber

    # Click Refine — children override is replaced (not merged)
    dash.refine()
    writes.clear(); metric_calls.clear()
    dash = rerender()
    labels = [c[0] for c in metric_calls]
    assert "Rows" in labels
    assert "Filtered" in labels
    assert any(c[1].get("value") == 25 for c in metric_calls)
    assert dash.state.row_count == 25

    # Click Reset — fragment reverts to its initial children
    dash.clear()
    writes.clear(); metric_calls.clear()
    dash = rerender()
    assert "nothing-loaded" in writes
    assert metric_calls == []
    assert dash.state.row_count == 0
