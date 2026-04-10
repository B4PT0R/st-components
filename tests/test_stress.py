"""
Stress tests — realistic large app scenarios.

Simulates the scale of a real production app: multi-page dashboard
with 50+ components, shared state, hooks, dynamic trees, rapid reruns.
"""
import time

from st_components.core import (
    App, Component, Element, State, fibers, render,
    use_effect, use_memo, use_ref, use_state,
)
from st_components.core.store import declare_shared_state, clear_shared_state, get_shared_state
from st_components.builtins import ErrorBoundary

from tests._mock import _mock_st, _session_data


# =====================================================================
# Realistic dashboard: 50+ components, shared state, hooks
# =====================================================================

class TestRealisticDashboard:

    def test_dashboard_with_sidebar_and_tabs(self):
        """A dashboard with sidebar filters, tabs, and data cards renders correctly."""

        class FilterState(State):
            category: str = "all"
            date_range: str = "7d"

        class SidebarFilters(Component):
            def render(self):
                state = use_state(category="all", date_range="7d")
                return None

        class MetricCard(Component):
            def render(self):
                return None

        class DataTable(Component):
            def render(self):
                memo = use_memo(lambda: list(range(100)), deps=[])
                return None

        class ChartPanel(Component):
            def render(self):
                ref = use_ref(None)
                return None

        class TabOverview(Component):
            def render(self):
                return (
                    MetricCard(key="revenue"),
                    MetricCard(key="users"),
                    MetricCard(key="orders"),
                    ChartPanel(key="chart"),
                    DataTable(key="table"),
                )

        class TabDetails(Component):
            def render(self):
                return (
                    DataTable(key="detail_table"),
                    ChartPanel(key="detail_chart"),
                )

        class Dashboard(Component):
            def render(self):
                return (
                    SidebarFilters(key="filters"),
                    TabOverview(key="overview"),
                    TabDetails(key="details"),
                )

        app = App()
        app.create_shared_state("filters", FilterState)
        app(Dashboard(key="dash")).render()

        # Verify structure
        assert "app.dash.filters" in fibers()
        assert "app.dash.overview.revenue" in fibers()
        assert "app.dash.overview.table" in fibers()
        assert "app.dash.details.detail_chart" in fibers()

        # Verify shared state
        fs = get_shared_state("filters")
        assert fs.category == "all"

        clear_shared_state()

    def test_dashboard_survives_10_reruns(self):
        """Dashboard state persists correctly across 10 reruns."""

        class Counter(Component):
            class S(State):
                views: int = 0

            def render(self):
                self.state.views += 1
                return None

        class Page(Component):
            def render(self):
                return tuple(Counter(key=f"card_{i}") for i in range(10))

        for _ in range(10):
            App()(Page(key="page")).render()

        # Each counter should have been incremented 10 times
        for i in range(10):
            assert fibers()[f"app.page.card_{i}"].state.views == 10


# =====================================================================
# Dynamic tree: components added/removed over time
# =====================================================================

class TestDynamicTree:

    def test_progressive_tree_growth(self):
        """Adding children one at a time over 20 reruns works correctly."""

        class Leaf(Component):
            def render(self):
                return None

        class Root(Component):
            def render(self):
                n = self.props.get("n", 1)
                return tuple(Leaf(key=f"item_{i}") for i in range(n))

        for n in range(1, 21):
            App()(Root(key="r", n=n)).render()

        # After 20 reruns, should have exactly 20 leaves
        from st_components.core.models import ElementFiber
        leaf_fibers = [
            k for k, f in fibers().items()
            if "item_" in k and not isinstance(f, ElementFiber)
        ]
        assert len(leaf_fibers) == 20

    def test_tree_shrink_cleans_up(self):
        """Shrinking the tree cleans up removed fibers."""
        unmounted = []

        class Leaf(Component):
            def component_did_unmount(self):
                unmounted.append(self.key)

            def render(self):
                return None

        class Root(Component):
            def render(self):
                n = self.props.get("n", 0)
                return tuple(Leaf(key=f"item_{i}") for i in range(n))

        App()(Root(key="r", n=20)).render()
        App()(Root(key="r", n=5)).render()

        assert len(unmounted) == 15
        remaining = [k for k in fibers() if "item_" in k]
        # 5 leaves x 2 (component fiber + anchor element fiber)
        assert len(remaining) == 10


# =====================================================================
# Hook-heavy components
# =====================================================================

class TestHookHeavy:

    def test_component_with_many_hooks(self):
        """A component using 20 hooks renders and persists correctly."""
        ref_values = []

        class HookHeavy(Component):
            def render(self):
                refs = [use_ref(i) for i in range(20)]
                memos = [use_memo(lambda i=i: i * 2, deps=[]) for i in range(5)]
                ref_values.clear()
                ref_values.extend([r.current for r in refs])
                return None

        App()(HookHeavy(key="h")).render()
        assert ref_values == list(range(20))

        # Second render — refs should be stable
        App()(HookHeavy(key="h")).render()
        assert ref_values == list(range(20))

    def test_effect_cleanup_chain(self):
        """Multiple effects with cleanup all fire correctly on unmount."""
        cleanups = []

        class Comp(Component):
            def render(self):
                for i in range(5):
                    use_effect(lambda i=i: (lambda i=i: cleanups.append(i)), deps=[])
                return None

        class Root(Component):
            def render(self):
                if self.props.get("show"):
                    return Comp(key="c")
                return None

        App()(Root(key="r", show=True)).render()
        assert cleanups == []

        App()(Root(key="r", show=False)).render()
        assert sorted(cleanups) == [0, 1, 2, 3, 4]


# =====================================================================
# Error boundary under load
# =====================================================================

class TestErrorBoundaryScale:

    def test_boundary_with_many_children_one_fails(self):
        """One broken child among 20 doesn't prevent the boundary from working."""
        _mock_st.error.side_effect = lambda msg, **kw: None
        _mock_st.expander.return_value.__enter__ = lambda s: s
        _mock_st.expander.return_value.__exit__ = lambda s, *a: None

        writes = []
        _mock_st.write.side_effect = lambda v: writes.append(v)

        class Good(Component):
            def render(self):
                return f"ok_{self.key}"

        class Bad(Component):
            def render(self):
                raise ValueError("broken")

        children = [Good(key=f"g{i}") for i in range(10)]
        children.append(Bad(key="bad"))
        children.extend(Good(key=f"g{10+i}") for i in range(9))

        App()(ErrorBoundary(key="eb")(*children)).render()

        # The 10 good children before Bad should have rendered
        good_writes = [w for w in writes if str(w).startswith("ok_")]
        assert len(good_writes) == 10  # first 10 rendered before error


# =====================================================================
# Performance: realistic app scale
# =====================================================================

class TestPerformance:

    def test_50_component_render_under_200ms(self):
        """Rendering a 50-component tree should be fast."""

        class Card(Component):
            def render(self):
                use_ref(None)
                use_memo(lambda: 42, deps=[])
                return None

        class Dashboard(Component):
            def render(self):
                return tuple(Card(key=f"c{i}") for i in range(50))

        start = time.monotonic()
        App()(Dashboard(key="d")).render()
        elapsed = time.monotonic() - start

        assert elapsed < 0.2, f"50 components took {elapsed:.3f}s"

    def test_5_reruns_under_500ms(self):
        """5 reruns of a 30-component tree with hooks should be fast."""

        class Card(Component):
            class S(State):
                count: int = 0

            def render(self):
                self.state.count += 1
                use_memo(lambda: "cached", deps=[])
                return None

        class Page(Component):
            def render(self):
                return tuple(Card(key=f"c{i}") for i in range(30))

        start = time.monotonic()
        for _ in range(5):
            App()(Page(key="p")).render()
        elapsed = time.monotonic() - start

        assert elapsed < 0.5, f"5 reruns took {elapsed:.3f}s"
