"""
Tests for the @component decorator, use_state hook, and fragment support.
"""
from st_components.core import App, Component, Ref, State, component, render, fibers, Context, use_state
from st_components.core.models import Props
from st_components.elements import text_input

from tests._mock import fake_ctx, _mock_st, _session_data


def test_function_component_decorator():
    seen = []
    title_ref = Ref()

    @component
    def Title(props):
        seen.append(
            {
                "label": props.label,
                "children": props.children,
                "without_children": dict(props.exclude("children")),
            }
        )
        return props.label

    instance = Title(key="title", ref=title_ref, label="Hello")("child")

    assert instance.__class__.__name__ == "Title"
    assert Title.component_class is instance.__class__

    Context.key_stack[:] = [fake_ctx("app")]
    render(instance)
    Context.key_stack.clear()

    assert title_ref.path == "app.title"
    assert seen == [{
        "label": "Hello",
        "children": ["child"],
        "without_children": {"label": "Hello"},
    }], f"got props: {seen}"


def test_function_component_class_is_cached():
    def Greeting(props):
        return props.get("label")

    GreetingA = component(Greeting)
    GreetingB = component(Greeting)

    assert GreetingA.component_class is GreetingB.component_class
    assert GreetingA(key="a").__class__ is GreetingB(key="b").__class__


def test_function_component_signature_validation():
    try:
        @component
        def Invalid(**props):
            return props
    except TypeError as err:
        assert "func(props)" in str(err)
    else:
        raise AssertionError("Expected invalid function component signature to raise")


def test_use_state_initializes_once():
    seen = []

    @component
    def Counter(props):
        state = use_state(count=props.initial)
        seen.append(state.count)
        return None

    App(root=Counter(key="counter", initial=1)).render()
    fibers()["counter"].state.count = 5
    App(root=Counter(key="counter", initial=999)).render()

    assert seen == [1, 5], f"unexpected state timeline: {seen}"
    assert fibers()["counter"].state.count == 5


def test_use_state_with_state_instance():
    class CounterState(State):
        count: int = 0

    seen = []

    @component
    def Counter(props):
        state = use_state(CounterState(count=props.initial))
        seen.append(state.count)
        return None

    App(root=Counter(key="counter", initial=3)).render()
    fibers()["counter"].state.count = 7
    App(root=Counter(key="counter", initial=999)).render()

    assert seen == [3, 7], f"unexpected state timeline: {seen}"
    assert isinstance(fibers()["counter"].state, CounterState)


def test_function_component_typed_props():
    class BadgeProps(Props):
        label: str = "badge"
        color: str = "blue"

    @component
    def Badge(props: BadgeProps):
        return None

    inst = Badge(key="b", label="ok")
    assert inst.props.label == "ok"
    assert inst.props.color == "blue"
    assert isinstance(inst.props, BadgeProps)


def test_function_component_typed_props_coercion():
    class BadgeProps(Props):
        label: str = "badge"

    @component
    def Badge(props: BadgeProps):
        return None

    # modict coerces by default: int 42 becomes str "42"
    inst = Badge(key="b", label=42)
    assert inst.props.label == "42"


def test_use_state_outside_component_raises():
    try:
        use_state(count=0)
    except RuntimeError as err:
        assert "while rendering a Component" in str(err)
    else:
        raise AssertionError("Expected use_state() outside render to raise")


def test_class_component_fragment():
    fragment_calls = []
    fragment_wrappers = []
    seen_keys = []

    def fake_fragment(func=None, *, run_every=None):
        def decorator(inner):
            def wrapped(*args, **kwargs):
                fragment_calls.append(run_every)
                return inner(*args, **kwargs)
            fragment_wrappers.append(wrapped)
            return wrapped
        return decorator if func is None else decorator(func)

    def fake_text_input(label, key=None, value=None, **kwargs):
        seen_keys.append(key)
        _session_data[key] = value
        return value

    _mock_st.fragment.side_effect = fake_fragment
    _mock_st.text_input.side_effect = fake_text_input

    class Profile(Component, fragment=True, run_every="10s"):
        def render(self):
            return text_input(key="name", value="Alice")("Name")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Profile(key="profile"))
    Context.key_stack.clear()

    fragment_wrappers[-1]()

    assert fragment_calls == ["10s", "10s"], f"unexpected fragment calls: {fragment_calls}"
    assert seen_keys == ["app.profile.name.value", "app.profile.name.value"], f"got keys: {seen_keys}"


def test_function_component_fragment():
    fragment_calls = []
    fragment_wrappers = []
    seen_keys = []

    def fake_fragment(func=None, *, run_every=None):
        def decorator(inner):
            def wrapped(*args, **kwargs):
                fragment_calls.append(run_every)
                return inner(*args, **kwargs)
            fragment_wrappers.append(wrapped)
            return wrapped
        return decorator if func is None else decorator(func)

    def fake_text_input(label, key=None, value=None, **kwargs):
        seen_keys.append(key)
        _session_data[key] = value
        return value

    _mock_st.fragment.side_effect = fake_fragment
    _mock_st.text_input.side_effect = fake_text_input

    @component(fragment=True, run_every="5s")
    def FragmentName(props):
        return text_input(key="name", value="Alice")("Name")

    Context.key_stack[:] = [fake_ctx("app")]
    render(FragmentName(key="profile"))
    Context.key_stack.clear()

    fragment_wrappers[-1]()

    assert fragment_calls == ["5s", "5s"], f"unexpected fragment calls: {fragment_calls}"
    assert seen_keys == ["app.profile.name.value", "app.profile.name.value"], f"got keys: {seen_keys}"
