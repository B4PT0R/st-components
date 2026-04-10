"""
Baseline benchmarks for st-components render pipeline.

Run with:  python -m benchmarks.bench_render
"""
import sys
import time
from pathlib import Path

# ── Bootstrap mock ───────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tests._mock import _mock_st, _session_data
sys.modules["streamlit"] = _mock_st

from st_components.core import (
    App, Component, ContextData, Element, State,
    component, create_context, fibers, render, use_effect, use_memo, use_state,
)
from st_components.core.context import Context
from st_components.elements.input.textual import text_input
from tests._mock import fake_ctx


# ── Helpers ──────────────────────────────────────────────────────────────────

def bench(name, fn, iterations=1000, warmup=50):
    _session_data.clear()
    _mock_st.reset_mock()
    for _ in range(warmup):
        _session_data.clear()
        _mock_st.reset_mock()
        fn()

    times = []
    for _ in range(iterations):
        _session_data.clear()
        _mock_st.reset_mock()
        t0 = time.perf_counter_ns()
        fn()
        times.append(time.perf_counter_ns() - t0)

    times.sort()
    p50 = times[len(times) // 2]
    p95 = times[int(len(times) * 0.95)]
    p99 = times[int(len(times) * 0.99)]
    avg = sum(times) // len(times)
    print(f"  {name:.<50s} avg={avg//1000:>6}µs  p50={p50//1000:>6}µs  p95={p95//1000:>6}µs  p99={p99//1000:>6}µs")
    return avg


# ── Benchmarks ───────────────────────────────────────────────────────────────

def bench_minimal_component():
    """Single component, no children, no hooks."""
    class Leaf(Component):
        def render(self):
            return None
    def run():
        App()(Leaf(key="leaf")).render()
    return bench("minimal_component", run)


def bench_nested_10():
    """10-level deep component tree."""
    class Node(Component):
        def render(self):
            depth = self.props.get("depth", 0)
            if depth <= 0:
                return None
            return Node(key=f"n{depth}", depth=depth - 1)
    def run():
        App()(Node(key="root", depth=10)).render()
    return bench("nested_10_deep", run)


def bench_wide_20():
    """Component with 20 children."""
    class Leaf(Component):
        def render(self):
            return None
    class Wide(Component):
        def render(self):
            return tuple(Leaf(key=f"c{i}") for i in range(20))
    def run():
        App()(Wide(key="wide")).render()
    return bench("wide_20_children", run)


def bench_hooks_combo():
    """Component using use_state + use_memo + use_effect."""
    @component
    def HookHeavy(props):
        state = use_state(count=0)
        doubled = use_memo(lambda: state.count * 2, deps=[state.count])
        use_effect(lambda: None, deps=[doubled])
        return None
    def run():
        App()(HookHeavy(key="hh")).render()
    return bench("hooks_combo", run)


def bench_rerender_state_persist():
    """Two consecutive renders — measures state persistence cost."""
    class Counter(Component):
        class S(State):
            count: int = 0
        def render(self):
            return None
    def run():
        App()(Counter(key="c")).render()
        fibers()["app.c"].state.count += 1
        App()(Counter(key="c")).render()
    return bench("rerender_state_persist", run)


def bench_context_provider():
    """Context provider with a consumer."""
    class ThemeData(ContextData):
        mode: str = "light"
    ThemeCtx = create_context(ThemeData())

    @component
    def Consumer(props):
        from st_components.core import use_context
        use_context(ThemeCtx)
        return None

    def run():
        App()(
            ThemeCtx.Provider(key="theme", data={"mode": "dark"})(
                Consumer(key="consumer")
            )
        ).render()
    return bench("context_provider", run)


def bench_element_text_input():
    """Single text_input element with callback."""
    _mock_st.text_input.side_effect = lambda *a, **kw: kw.get("value", "")

    class Form(Component):
        def on_change(self, value):
            pass
        def render(self):
            return text_input(key="name", value="Alice", on_change=self.on_change)("Name")
    def run():
        App()(Form(key="form")).render()
    return bench("element_text_input", run)


def bench_unmount_cycle():
    """Render then unmount a child — measures cleanup cost."""
    class Child(Component):
        def render(self):
            use_effect(lambda: (lambda: None), deps=[])
            return None
    class Root(Component):
        def render(self):
            if self.props.get("show"):
                return Child(key="child")
            return None
    def run():
        App()(Root(key="root", show=True)).render()
        App()(Root(key="root", show=False)).render()
    return bench("unmount_cycle", run)


def bench_functional_component():
    """@component decorator overhead."""
    @component
    def Greeting(props):
        return None
    def run():
        App()(Greeting(key="g")).render()
    return bench("functional_component", run)


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("st-components render benchmarks")
    print("=" * 80)
    results = {}
    results["minimal"] = bench_minimal_component()
    results["nested_10"] = bench_nested_10()
    results["wide_20"] = bench_wide_20()
    results["hooks"] = bench_hooks_combo()
    results["rerender"] = bench_rerender_state_persist()
    results["context"] = bench_context_provider()
    results["element"] = bench_element_text_input()
    results["unmount"] = bench_unmount_cycle()
    results["functional"] = bench_functional_component()
    print("=" * 80)
