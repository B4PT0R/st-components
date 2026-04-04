"""
Tests for Component fiber resolution, state persistence, and lifecycle hooks.
"""
from st_components.core import App, Component, render, fibers, Context

from tests._mock import fake_ctx


def test_fiber_key_from_context():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="comp")
    Context.stack[:] = [fake_ctx("parent")]
    render(comp)
    Context.stack.clear()

    assert comp._fiber_key == "parent.comp", f"got: {comp._fiber_key}"
    assert "parent.comp" in fibers()


def test_same_key_different_paths():
    class Comp(Component):
        def render(self):
            pass

    comp1 = Comp(key="comp")
    comp2 = Comp(key="comp")

    Context.stack[:] = [fake_ctx("branch1")]
    render(comp1)
    Context.stack.clear()

    Context.stack[:] = [fake_ctx("branch2")]
    render(comp2)
    Context.stack.clear()

    assert comp1._fiber_key == "branch1.comp"
    assert comp2._fiber_key == "branch2.comp"
    assert "branch1.comp" in fibers()
    assert "branch2.comp" in fibers()
    assert fibers()["branch1.comp"] is not fibers()["branch2.comp"]


def test_state_persists():
    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=0)

        def increment(self):
            self.state.count += 1

        def render(self):
            pass

    c1 = Counter(key="counter")
    Context.stack[:] = [fake_ctx("app")]
    render(c1)
    Context.stack.clear()

    assert c1.state.count == 0
    c1.increment()
    assert c1.state.count == 1

    c2 = Counter(key="counter")
    Context.stack[:] = [fake_ctx("app")]
    render(c2)
    Context.stack.clear()

    assert c2.state.count == 1, f"State not persisted: got {c2.state.count}"


def test_state_isolation():
    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=0)

        def increment(self):
            self.state.count += 1

        def render(self):
            pass

    c1 = Counter(key="counter")
    c2 = Counter(key="counter")

    Context.stack[:] = [fake_ctx("col1")]
    render(c1)
    Context.stack.clear()

    Context.stack[:] = [fake_ctx("col2")]
    render(c2)
    Context.stack.clear()

    c1.increment()
    c1.increment()

    assert c1.state.count == 2
    assert c2.state.count == 0, f"Isolation broken: c2.count = {c2.state.count}"


def test_full_render_pipeline():
    class Leaf(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(rendered=False)

        def render(self):
            self.state.rendered = True

    leaf = Leaf(key="leaf")
    Context.stack[:] = [fake_ctx("root")]
    render(leaf)
    Context.stack.clear()

    assert leaf._fiber_key == "root.leaf"
    assert leaf.state.rendered is True


def test_component_did_mount():
    mount_count = [0]

    class Comp(Component):
        def component_did_mount(self):
            mount_count[0] += 1

        def render(self):
            pass

    Context.stack[:] = [fake_ctx("root")]
    render(Comp(key="c"))
    render(Comp(key="c"))
    Context.stack.clear()

    assert mount_count[0] == 1, f"component_did_mount called {mount_count[0]} times"


def test_state_accessible_in_render():
    state_seen = [None]

    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=0)

        def render(self):
            state_seen[0] = self.state.count

    c1 = Counter(key="counter")
    Context.stack[:] = [fake_ctx("app")]
    render(c1)
    Context.stack.clear()

    c1.state.count = 7

    c2 = Counter(key="counter")
    Context.stack[:] = [fake_ctx("app")]
    render(c2)
    Context.stack.clear()

    assert state_seen[0] == 7, f"render_func saw stale state: {state_seen[0]}"


def test_component_did_update_on_state_change():
    updates = []

    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=0)

        def component_did_update(self, prev_state):
            updates.append((prev_state.count, self.state.count))

        def render(self):
            pass

    App(root=Counter(key="counter")).render()
    fibers()["counter"].state.count = 5
    App(root=Counter(key="counter")).render()

    assert updates == [(0, 5)], f"unexpected updates: {updates}"


def test_component_did_update_only_when_state_changes():
    updates = [0]

    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=0)

        def component_did_update(self, prev_state):
            updates[0] += 1

        def render(self):
            pass

    App(root=Counter(key="counter")).render()
    App(root=Counter(key="counter")).render()

    assert updates[0] == 0, f"component_did_update fired {updates[0]} times"
