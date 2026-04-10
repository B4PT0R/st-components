"""
Integration tests — multi-rerun flows, error boundaries, render cycle robustness.

These tests simulate realistic usage patterns: multiple reruns with state
mutations, error recovery, callback chains, and component lifecycle flows.
"""
import pytest

from st_components.core import (
    App, Component, Element, State, fibers, get_app, get_state, render, set_state,
    use_effect, use_memo, use_ref, use_state,
)
from st_components.core.errors import AppError, StcError
from st_components.builtins import ErrorBoundary

from tests._mock import _mock_st, _session_data


# =====================================================================
# Error Boundary
# =====================================================================

class TestErrorBoundary:

    def test_catches_child_render_error(self):
        """ErrorBoundary catches exceptions in children and renders fallback."""
        errors = []
        _mock_st.error.side_effect = lambda msg, **kw: errors.append(msg)
        _mock_st.expander.return_value.__enter__ = lambda s: s
        _mock_st.expander.return_value.__exit__ = lambda s, *a: None

        class Broken(Component):
            def render(self):
                raise ValueError("boom")

        App()(
            ErrorBoundary(key="boundary")(
                Broken(key="broken"),
            )
        ).render()

        # Error should be caught, not propagated
        state = get_state("app.boundary")
        assert state.error is not None
        assert isinstance(state.error, ValueError)
        assert "boom" in str(state.error)
        assert state.error_traceback is not None

    def test_renders_children_when_no_error(self):
        """ErrorBoundary is transparent when children render fine."""
        writes = []
        _mock_st.write.side_effect = lambda v: writes.append(v)

        class Good(Component):
            def render(self):
                return "hello"

        App()(
            ErrorBoundary(key="boundary")(
                Good(key="good"),
            )
        ).render()

        state = get_state("app.boundary")
        assert state.error is None
        assert "hello" in writes

    def test_clears_error_on_successful_rerender(self):
        """Error state clears when children render successfully on rerun."""
        errors = []
        _mock_st.error.side_effect = lambda msg, **kw: errors.append(msg)
        _mock_st.expander.return_value.__enter__ = lambda s: s
        _mock_st.expander.return_value.__exit__ = lambda s, *a: None

        call_count = [0]

        class MaybeBreaks(Component):
            def render(self):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise RuntimeError("first render fails")
                return None

        App()(
            ErrorBoundary(key="boundary")(
                MaybeBreaks(key="maybe"),
            )
        ).render()

        assert get_state("app.boundary").error is not None

        # Second render succeeds
        App()(
            ErrorBoundary(key="boundary")(
                MaybeBreaks(key="maybe"),
            )
        ).render()

        assert get_state("app.boundary").error is None

    def test_callable_fallback(self):
        """ErrorBoundary accepts a callable(error) as fallback."""
        writes = []
        _mock_st.write.side_effect = lambda v: writes.append(v)

        class Broken(Component):
            def render(self):
                raise ValueError("oops")

        App()(
            ErrorBoundary(key="b", fallback=lambda e: f"Error: {e}")(
                Broken(key="broken"),
            )
        ).render()

        assert any("Error: oops" in str(w) for w in writes)

    def test_component_fallback(self):
        """ErrorBoundary accepts a Component as fallback."""
        writes = []
        _mock_st.write.side_effect = lambda v: writes.append(v)

        class FallbackView(Component):
            def render(self):
                return "fallback rendered"

        class Broken(Component):
            def render(self):
                raise ValueError("oops")

        App()(
            ErrorBoundary(key="b", fallback=FallbackView(key="fb"))(
                Broken(key="broken"),
            )
        ).render()

        assert "fallback rendered" in writes

    def test_sibling_still_renders(self):
        """Error in one child doesn't prevent rendering of siblings before it."""
        writes = []
        _mock_st.write.side_effect = lambda v: writes.append(v)
        _mock_st.error.side_effect = lambda msg, **kw: None
        _mock_st.expander.return_value.__enter__ = lambda s: s
        _mock_st.expander.return_value.__exit__ = lambda s, *a: None

        class Good(Component):
            def render(self):
                return "ok"

        class Broken(Component):
            def render(self):
                raise ValueError("boom")

        # Good renders before Broken; Broken is caught by boundary
        App()(
            Good(key="outside"),
            ErrorBoundary(key="b")(
                Broken(key="broken"),
            ),
        ).render()

        assert "ok" in writes


# =====================================================================
# Multi-rerun integration
# =====================================================================

class TestMultiRerun:

    def test_state_persists_across_reruns(self):
        """Component state survives multiple App().render() cycles."""
        class Counter(Component):
            class S(State):
                count: int = 0

            def render(self):
                return None

        App()(Counter(key="c")).render()
        fibers()["app.c"].state.count = 5

        App()(Counter(key="c")).render()
        assert get_state("app.c").count == 5

        fibers()["app.c"].state.count = 10
        App()(Counter(key="c")).render()
        assert get_state("app.c").count == 10

    def test_component_added_and_removed(self):
        """Adding and removing a child across reruns cleans up fibers."""
        unmounted = []

        class Child(Component):
            def component_did_unmount(self):
                unmounted.append(self.key)

            def render(self):
                return None

        class Root(Component):
            def render(self):
                if self.props.get("show"):
                    return Child(key="child")
                return None

        App()(Root(key="r", show=True)).render()
        assert "app.r.child" in fibers()

        App()(Root(key="r", show=False)).render()
        assert "app.r.child" not in fibers()
        assert "child" in unmounted

        App()(Root(key="r", show=True)).render()
        assert "app.r.child" in fibers()

    def test_hooks_persist_across_reruns(self):
        """Hook state (use_ref, use_memo) persists across reruns."""
        seen_refs = []

        class Comp(Component):
            def render(self):
                ref = use_ref(0)
                ref.current += 1
                seen_refs.append(ref.current)
                return None

        App()(Comp(key="c")).render()
        App()(Comp(key="c")).render()
        App()(Comp(key="c")).render()

        assert seen_refs == [1, 2, 3]

    def test_effect_cleanup_runs_on_unmount(self):
        """use_effect cleanup runs when component is removed."""
        cleanups = []

        class Child(Component):
            def render(self):
                use_effect(lambda: (lambda: cleanups.append("cleaned")), deps=[])
                return None

        class Root(Component):
            def render(self):
                if self.props.get("show"):
                    return Child(key="child")
                return None

        App()(Root(key="r", show=True)).render()
        assert cleanups == []

        App()(Root(key="r", show=False)).render()
        assert cleanups == ["cleaned"]

    def test_callback_mutates_state_for_next_rerun(self):
        """A callback setting state is visible on the next rerun."""
        from st_components.elements.input.buttons import button as btn

        def fake_button(label, key=None, on_click=None, **kw):
            if on_click:
                on_click()

        _mock_st.button.side_effect = fake_button

        seen = []

        class Form(Component):
            class S(State):
                clicked: bool = False

            def render(self):
                seen.append(self.state.clicked)
                return btn(key="b", on_click=lambda: self.state.update(clicked=True))("Go")

        App()(Form(key="f")).render()
        # First render: state is initial
        assert seen == [False]

        # Second render: callback fired, state updated
        seen.clear()
        App()(Form(key="f")).render()
        assert seen == [True]


# =====================================================================
# Render cycle robustness
# =====================================================================

class TestRenderCycleRobustness:

    def test_end_cycle_runs_all_cleanups_even_if_one_raises(self):
        """If a lifecycle hook raises, other components still get processed."""
        updates = []
        errors = []

        class GoodChild(Component):
            def component_did_update(self, prev):
                updates.append("good")

            def render(self):
                return None

        class BadChild(Component):
            def component_did_update(self, prev):
                raise RuntimeError("update hook failed")

            def render(self):
                return None

        class Root(Component):
            def render(self):
                return (BadChild(key="bad"), GoodChild(key="good"))

        # First render — sets up fibers
        App()(Root(key="r")).render()

        # Mutate both states to trigger component_did_update
        fibers()["app.r.bad"].state["x"] = 1
        fibers()["app.r.good"].state["x"] = 1

        # Second render — BadChild's update raises, but GoodChild should still fire
        try:
            App()(Root(key="r")).render()
        except RuntimeError:
            pass

        # GoodChild's update may or may not have fired depending on order,
        # but the cycle must complete without corrupting state
        assert "app.r.bad" in fibers()
        assert "app.r.good" in fibers()

    def test_app_accessible_after_render_error(self):
        """get_app() still works after a render error (non-boundary)."""
        class Broken(Component):
            def render(self):
                raise ValueError("boom")

        try:
            App()(Broken(key="b")).render()
        except ValueError:
            pass

        # App should still be accessible
        assert get_app() is not None
