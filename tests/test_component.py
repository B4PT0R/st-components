"""
Tests for Component fiber resolution, state persistence, and lifecycle hooks.
"""
import pickle

from st_components.core import App, Component, State, render, fibers, ctx
from st_components.core.models import Fiber, Fibers, Props, SharedStates

from tests._mock import fake_ctx


def test_fiber_key_from_context():
    class Comp(Component):
        def render(self):
            pass

    comp = Comp(key="comp")
    ctx.replace("key", [fake_ctx("parent")])
    render(comp)
    ctx.replace("key", [])

    assert comp._fiber_key == "parent.comp", f"got: {comp._fiber_key}"
    assert "parent.comp" in fibers()


def test_same_key_different_paths():
    class Comp(Component):
        def render(self):
            pass

    comp1 = Comp(key="comp")
    comp2 = Comp(key="comp")

    ctx.replace("key", [fake_ctx("branch1")])
    render(comp1)
    ctx.replace("key", [])

    ctx.replace("key", [fake_ctx("branch2")])
    render(comp2)
    ctx.replace("key", [])

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
    ctx.replace("key", [fake_ctx("app")])
    render(c1)
    ctx.replace("key", [])

    assert c1.state.count == 0
    c1.increment()
    assert c1.state.count == 1

    c2 = Counter(key="counter")
    ctx.replace("key", [fake_ctx("app")])
    render(c2)
    ctx.replace("key", [])

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

    ctx.replace("key", [fake_ctx("col1")])
    render(c1)
    ctx.replace("key", [])

    ctx.replace("key", [fake_ctx("col2")])
    render(c2)
    ctx.replace("key", [])

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
    ctx.replace("key", [fake_ctx("root")])
    render(leaf)
    ctx.replace("key", [])

    assert leaf._fiber_key == "root.leaf"
    assert leaf.state.rendered is True


def test_component_did_mount():
    mount_count = [0]

    class Comp(Component):
        def component_did_mount(self):
            mount_count[0] += 1

        def render(self):
            pass

    ctx.replace("key", [fake_ctx("root")])
    render(Comp(key="c"))
    render(Comp(key="c"))
    ctx.replace("key", [])

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
    ctx.replace("key", [fake_ctx("app")])
    render(c1)
    ctx.replace("key", [])

    c1.state.count = 7

    c2 = Counter(key="counter")
    ctx.replace("key", [fake_ctx("app")])
    render(c2)
    ctx.replace("key", [])

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

    App()(Counter(key="counter")).render()
    fibers()["app.counter"].state.count = 5
    App()(Counter(key="counter")).render()

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

    App()(Counter(key="counter")).render()
    App()(Counter(key="counter")).render()

    assert updates[0] == 0, f"component_did_update fired {updates[0]} times"


def test_nested_state_class_initializes_state():
    class Counter(Component):
        class CounterState(State):
            count: int = 0
            label: str = "clicks"

        def render(self):
            pass

    comp = Counter(key="counter")
    assert comp.state.count == 0
    assert comp.state.label == "clicks"


def test_fibers_coerces_dict_values_to_fiber_instances():
    storage = Fibers(
        {
            "counter": {
                "state": {"count": 3},
                "component_id": "component:123",
                "previous_state": {"count": 2},
                "keep_alive": True,
            }
        }
    )

    assert isinstance(storage["counter"], Fiber)
    assert isinstance(storage["counter"].state, State)
    assert storage["counter"].component_id == "component:123"
    assert isinstance(storage["counter"].previous_state, State)
    assert storage["counter"].state.count == 3
    assert storage["counter"].previous_state.count == 2
    assert storage["counter"].keep_alive is True


def test_fiber_is_pickle_serializable():
    fiber = Fiber(
        state={"count": 1},
        component_id="component:123",
        previous_state={"count": 0},
        keep_alive=True,
    )

    restored = pickle.loads(pickle.dumps(fiber))

    assert restored.component_id == "component:123"
    assert restored.state.count == 1
    assert restored.previous_state.count == 0
    assert restored.keep_alive is True


def test_shared_states_coerces_dict_values_to_state_instances():
    storage = SharedStates(
        {
            "workspace": {"team": "Core"},
            "auth": {"user": "baptiste"},
        }
    )

    assert isinstance(storage["workspace"], State)
    assert isinstance(storage["auth"], State)
    assert storage["workspace"].team == "Core"
    assert storage["auth"].user == "baptiste"


def test_nested_state_class_persists_across_reruns():
    class Counter(Component):
        class CounterState(State):
            count: int = 0

        def increment(self):
            self.state.count += 1

        def render(self):
            pass

    c1 = Counter(key="counter")
    ctx.replace("key", [fake_ctx("app")])
    render(c1)
    ctx.replace("key", [])

    c1.increment()
    assert c1.state.count == 1

    c2 = Counter(key="counter")
    ctx.replace("key", [fake_ctx("app")])
    render(c2)
    ctx.replace("key", [])

    assert c2.state.count == 1


def test_nested_state_class_coexists_with_manual_init():
    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=99)

        def render(self):
            pass

    comp = Counter(key="counter")
    assert comp.state.count == 99


def test_nested_props_class_used_for_props():
    class Greeting(Component):
        class GreetingProps(Props):
            name: str = "world"

        def render(self):
            pass

    comp = Greeting(key="greeting", name="Baptiste")
    assert comp.props.name == "Baptiste"


def test_nested_props_class_default_values():
    class Greeting(Component):
        class GreetingProps(Props):
            name: str = "world"

        def render(self):
            pass

    comp = Greeting(key="greeting")
    assert comp.props.name == "world"


def test_nested_state_instance_preserved_if_already_correct_class():
    class Counter(Component):
        class CounterState(State):
            count: int = 0

        def render(self):
            pass

    comp = Counter(key="counter")
    original = Counter.CounterState(count=3)
    comp.state = original
    assert comp._state is original


def test_nested_state_class_preserved_by_set_state():
    class Counter(Component):
        class CounterState(State):
            count: int = 0

        def render(self):
            pass

    comp = Counter(key="counter")
    comp.set_state(dict(count=5))
    assert isinstance(comp._state, Counter.CounterState)
    assert comp.state.count == 5


def test_nested_props_and_state_together():
    class Card(Component):
        class CardProps(Props):
            title: str = "Untitled"

        class CardState(State):
            open: bool = False

        def render(self):
            pass

    comp = Card(key="card", title="Hello")
    assert comp.props.title == "Hello"
    assert comp.state.open is False
