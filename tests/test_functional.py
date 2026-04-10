"""
Tests for the @component decorator, hooks, and fragment support.
"""
from st_components.core import App, Component, ctx, ContextData, Ref, State, component, create_context, render, fibers, use_callback, use_context, use_effect, use_id, use_memo, use_previous, use_ref, use_state
from st_components.core.hooks import _use_hook_slot
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

    ctx.replace("key", [fake_ctx("app")])
    render(instance)
    ctx.replace("key", [])

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
        assert "positional parameter" in str(err)
    else:
        raise AssertionError("Expected invalid function component signature to raise")


def test_use_state_initializes_once():
    seen = []

    @component
    def Counter(props):
        state = use_state(count=props.initial)
        seen.append(state.count)
        return None

    App()(Counter(key="counter", initial=1)).render()
    fibers()["app.counter"].state.count = 5
    App()(Counter(key="counter", initial=999)).render()

    assert seen == [1, 5], f"unexpected state timeline: {seen}"
    assert fibers()["app.counter"].state.count == 5


def test_use_state_with_state_instance():
    class CounterState(State):
        count: int = 0

    seen = []

    @component
    def Counter(props):
        state = use_state(CounterState(count=props.initial))
        seen.append(state.count)
        return None

    App()(Counter(key="counter", initial=3)).render()
    fibers()["app.counter"].state.count = 7
    App()(Counter(key="counter", initial=999)).render()

    assert seen == [3, 7], f"unexpected state timeline: {seen}"
    assert isinstance(fibers()["app.counter"].state, CounterState)


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
        assert "render cycle" in str(err)
    else:
        raise AssertionError("Expected use_state() outside render to raise")


def test_use_context_returns_default_without_provider():
    seen = []

    class ThemeData(ContextData):
        mode: str = "light"

    ThemeContext = create_context(ThemeData(mode="light"))

    @component
    def Demo(props):
        seen.append(use_context(ThemeContext).mode)
        return None

    App()(Demo(key="demo")).render()

    assert seen == ["light"]


def test_use_context_accepts_plain_dict_initial_data():
    seen = []
    ThemeContext = create_context({"mode": "light"})

    @component
    def Demo(props):
        current = use_context(ThemeContext)
        seen.append((current.mode, isinstance(current, ContextData), type(current) is ContextData))
        return None

    App()(
        ThemeContext.Provider(key="theme", data={"mode": "dark"})(
            Demo(key="demo")
        )
    ).render()

    assert seen == [("dark", True, True)]


def test_use_context_provider_accepts_contextdata_data_and_normalizes_to_context_class():
    seen = []

    class ThemeData(ContextData):
        mode: str = "light"
        accent: str = "blue"

    ThemeContext = create_context(ThemeData(mode="light", accent="blue"))

    @component
    def Demo(props):
        current = use_context(ThemeContext)
        seen.append((current.mode, current.accent, isinstance(current, ThemeData)))
        return None

    App()(
        ThemeContext.Provider(key="theme", data=ThemeData(mode="dark"))(
            Demo(key="demo")
        )
    ).render()

    assert seen == [("dark", "blue", True)]


def test_use_context_provider_replaces_current_data_instead_of_merging():
    seen = []

    class WorkspaceData(ContextData):
        mode: str = "view"
        team: str = "core"

    WorkspaceContext = create_context(WorkspaceData(mode="view", team="core"))

    @component
    def Demo(props):
        current = use_context(WorkspaceContext)
        seen.append((current.mode, current.team))
        return None

    App()(
        WorkspaceContext.Provider(key="workspace", data={"mode": "edit"})(
            Demo(key="demo")
        )
    ).render()

    assert seen == [("edit", "core")]


def test_use_context_reads_nearest_provider():
    seen = []

    class ThemeData(ContextData):
        mode: str = "light"

    ThemeContext = create_context(ThemeData(mode="light"))

    @component
    def Demo(props):
        seen.append(use_context(ThemeContext).mode)
        return None

    App()(
        ThemeContext.Provider(key="outer_theme", data={"mode": "dark"})(
            ThemeContext.Provider(key="inner_theme", data={"mode": "contrast"})(
                Demo(key="demo")
            )
        )
    ).render()

    assert seen == ["contrast"]
    assert "app.outer_theme.inner_theme.demo" in fibers()


def test_use_context_works_in_class_component():
    seen = []

    class DensityData(ContextData):
        mode: str = "comfortable"

    DensityContext = create_context(DensityData(mode="comfortable"))

    class Panel(Component):
        def render(self):
            seen.append(use_context(DensityContext).mode)
            return None

    App()(
        DensityContext.Provider(key="density", data={"mode": "compact"})(
            Panel(key="panel")
        )
    ).render()

    assert seen == ["compact"]


def test_use_memo_reuses_value_when_deps_are_unchanged():
    calls = []
    seen = []

    @component
    def Demo(props):
        value = use_memo(lambda: calls.append(props.value) or props.value * 10, deps=[props.value])
        seen.append(value)
        return None

    App()(Demo(key="demo", value=2)).render()
    App()(Demo(key="demo", value=2)).render()

    assert calls == [2]
    assert seen == [20, 20]


def test_use_memo_recomputes_when_deps_change():
    calls = []
    seen = []

    @component
    def Demo(props):
        value = use_memo(lambda: calls.append(props.value) or props.value * 10, deps=[props.value])
        seen.append(value)
        return None

    App()(Demo(key="demo", value=2)).render()
    App()(Demo(key="demo", value=3)).render()

    assert calls == [2, 3]
    assert seen == [20, 30]


def test_use_memo_without_deps_recomputes_every_render():
    calls = []
    seen = []

    @component
    def Demo(props):
        value = use_memo(lambda: calls.append(props.value) or props.value * 10)
        seen.append(value)
        return None

    App()(Demo(key="demo", value=2)).render()
    App()(Demo(key="demo", value=2)).render()

    assert calls == [2, 2]
    assert seen == [20, 20]


def test_use_memo_with_empty_deps_initializes_once():
    calls = []
    seen = []

    @component
    def Demo(props):
        value = use_memo(lambda: calls.append(props.value) or props.value * 10, deps=[])
        seen.append(value)
        return None

    App()(Demo(key="demo", value=2)).render()
    App()(Demo(key="demo", value=999)).render()

    assert calls == [2]
    assert seen == [20, 20]


def test_use_effect_runs_after_render_on_mount():
    events = []

    @component
    def Demo(props):
        events.append("render")
        use_effect(lambda: events.append("effect"), deps=[])
        return None

    App()(Demo(key="demo")).render()

    assert events == ["render", "effect"]


def test_use_effect_skips_when_deps_are_unchanged():
    events = []

    @component
    def Demo(props):
        use_effect(lambda: events.append(props.value), deps=[props.value])
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=1)).render()

    assert events == [1]


def test_use_effect_reruns_and_cleans_up_when_deps_change():
    events = []

    @component
    def Demo(props):
        def effect():
            events.append(f"effect:{props.value}")

            def cleanup():
                events.append(f"cleanup:{props.value}")

            return cleanup

        use_effect(effect, deps=[props.value])
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=2)).render()

    assert events == ["effect:1", "cleanup:1", "effect:2"]


def test_use_effect_cleanup_runs_on_unmount():
    events = []

    @component
    def Child(props):
        def effect():
            events.append("effect")

            def cleanup():
                events.append("cleanup")

            return cleanup

        use_effect(effect, deps=[])
        return None

    @component
    def Root(props):
        if props.show:
            return Child(key="child")
        return None

    App()(Root(key="root", show=True)).render()
    App()(Root(key="root", show=False)).render()

    assert events == ["effect", "cleanup"]


def test_use_effect_without_deps_runs_every_render():
    events = []

    @component
    def Demo(props):
        use_effect(lambda: events.append(props.value))
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=1)).render()

    assert events == [1, 1]


def test_use_effect_rejects_non_callable_cleanup():
    @component
    def Demo(props):
        use_effect(lambda: "not-callable-cleanup", deps=[])
        return None

    try:
        App()(Demo(key="demo")).render()
    except TypeError as err:
        assert "cleanup must be callable or None" in str(err)
    else:
        raise AssertionError("Expected invalid use_effect cleanup to raise")


def test_use_ref_persists_same_object_across_renders():
    seen = []

    @component
    def Demo(props):
        ref = use_ref(props.initial)
        seen.append(ref)
        return None

    App()(Demo(key="demo", initial=1)).render()
    seen[0].current = 7
    App()(Demo(key="demo", initial=999)).render()

    assert seen[0] is seen[1]
    assert seen[1].current == 7


def test_use_ref_initial_value_is_used_only_once():
    seen = []

    @component
    def Demo(props):
        ref = use_ref(props.initial)
        seen.append(ref.current)
        return None

    App()(Demo(key="demo", initial=1)).render()
    App()(Demo(key="demo", initial=999)).render()

    assert seen == [1, 1]


def test_use_callback_reuses_function_when_deps_are_unchanged():
    seen = []

    @component
    def Demo(props):
        callback = use_callback(lambda: props.value, deps=[props.value])
        seen.append(callback)
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=1)).render()

    assert seen[0] is seen[1]


def test_use_callback_recomputes_function_when_deps_change():
    seen = []

    @component
    def Demo(props):
        callback = use_callback(lambda: props.value, deps=[props.value])
        seen.append(callback)
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=2)).render()

    assert seen[0] is not seen[1]
    assert seen[0]() == 1
    assert seen[1]() == 2


def test_use_previous_returns_previous_render_value():
    seen = []

    @component
    def Demo(props):
        seen.append(use_previous(props.value))
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=2)).render()
    App()(Demo(key="demo", value=3)).render()

    assert seen == [None, 1, 2]


def test_use_previous_accepts_custom_initial_value():
    seen = []

    @component
    def Demo(props):
        seen.append(use_previous(props.value, initial="init"))
        return None

    App()(Demo(key="demo", value=1)).render()
    App()(Demo(key="demo", value=2)).render()

    assert seen == ["init", 1]


def test_use_id_is_stable_across_renders():
    seen = []

    @component
    def Demo(props):
        seen.append(use_id())
        return None

    App()(Demo(key="demo")).render()
    App()(Demo(key="demo")).render()

    assert seen[0] == seen[1]


def test_use_id_is_distinct_per_hook_call():
    seen = []

    @component
    def Demo(props):
        seen.append((use_id(), use_id()))
        return None

    App()(Demo(key="demo")).render()

    first, second = seen[0]
    assert first != second


def test_hook_slots_persist_by_call_order():
    seen = []

    @component
    def Demo(props):
        first = _use_hook_slot("memo")
        if not first.initialized:
            first.value = props.first
            first.initialized = True

        second = _use_hook_slot("memo")
        if not second.initialized:
            second.value = props.second
            second.initialized = True

        seen.append((first.value, second.value))
        return None

    App()(Demo(key="demo", first="a", second="b")).render()
    fiber = fibers()["app.demo"]
    fiber.hooks[0].value = "persisted-a"
    fiber.hooks[1].value = "persisted-b"
    App()(Demo(key="demo", first="x", second="y")).render()

    assert seen == [("a", "b"), ("persisted-a", "persisted-b")]


def test_hook_kind_order_change_raises():
    @component
    def Demo(props):
        if props.flip:
            _use_hook_slot("second")
            _use_hook_slot("first")
        else:
            _use_hook_slot("first")
            _use_hook_slot("second")
        return None

    App()(Demo(key="demo", flip=False)).render()

    try:
        App()(Demo(key="demo", flip=True)).render()
    except RuntimeError as err:
        assert "Hook order changed" in str(err)
    else:
        raise AssertionError("Expected hook order change to raise")


def test_hook_count_change_raises():
    @component
    def Demo(props):
        _use_hook_slot("first")
        if props.extra:
            _use_hook_slot("second")
        return None

    App()(Demo(key="demo", extra=True)).render()

    try:
        App()(Demo(key="demo", extra=False)).render()
    except RuntimeError as err:
        assert "Hook count changed" in str(err)
    else:
        raise AssertionError("Expected hook count change to raise")


def test_fragment_transparent_renders_children():
    """fragment(scoped=False) renders children in sequence — no st.fragment call."""
    writes = []
    _mock_st.write.side_effect = lambda v: writes.append(v)

    from st_components.elements.layout.fragment import fragment

    class Root(Component):
        def render(self):
            return fragment(key="grp")(
                "hello",
                "world",
            )

    ctx.replace("key", [fake_ctx("app")])
    render(Root(key="root"))
    ctx.replace("key", [])

    assert writes == ["hello", "world"]
    _mock_st.fragment.assert_not_called()


def test_fragment_scoped_wraps_in_st_fragment():
    """fragment(scoped=True) wraps children in st.fragment()."""
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

    from st_components.elements.layout.fragment import fragment

    class Profile(Component):
        def render(self):
            return fragment(key="frag", scoped=True, run_every="10s")(
                text_input(key="name", value="Alice")("Name")
            )

    ctx.replace("key", [fake_ctx("app")])
    render(Profile(key="profile"))
    ctx.replace("key", [])

    # st.fragment was called with run_every during the first render
    assert fragment_calls == ["10s"], f"unexpected fragment calls: {fragment_calls}"
    assert seen_keys == ["app.profile.frag.name.raw"], f"got keys: {seen_keys}"

    # Simulate a fragment re-run (Streamlit calls the wrapped function again)
    fragment_wrappers[-1]()
    assert fragment_calls == ["10s", "10s"]
    assert seen_keys == ["app.profile.frag.name.raw", "app.profile.frag.name.raw"]


def test_fragment_scoped_without_run_every():
    """fragment(scoped=True) without run_every uses None."""
    fragment_calls = []

    def fake_fragment(func=None, *, run_every=None):
        def decorator(inner):
            def wrapped(*args, **kwargs):
                fragment_calls.append(run_every)
                return inner(*args, **kwargs)
            return wrapped
        return decorator if func is None else decorator(func)

    _mock_st.fragment.side_effect = fake_fragment
    _mock_st.write.side_effect = lambda v: None

    from st_components.elements.layout.fragment import fragment

    class Root(Component):
        def render(self):
            return fragment(key="f", scoped=True)("child")

    ctx.replace("key", [fake_ctx("app")])
    render(Root(key="root"))
    ctx.replace("key", [])

    assert fragment_calls == [None]
