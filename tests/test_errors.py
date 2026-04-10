"""
Comprehensive tests for typed error hierarchy, error paths, and error messages.

Validates that:
- Every exception is a subclass of StcError
- Specific typed exceptions are raised (not generic RuntimeError/TypeError)
- Error messages are clear and actionable
- Edge cases and boundary conditions raise properly
"""
import pytest

from st_components.core import (
    App, Component, Element, Props, Ref, State, ctx, render, fibers,
    component, create_context, use_state, use_memo, use_callback, use_effect, use_ref,
    callback, get_state, set_state, reset_element,
)
from st_components.core.errors import (
    AlreadyMountedError, AppError, CallbackError, ComponentDefinitionError,
    ConfigError, ContextError, FiberNotFoundError, HookContextError,
    HookError, HookOrderError, LifecycleError, LocalStoreError,
    NotMountedError, PageError, RefError, RenderDepthError, RenderError,
    RouterError, SharedStateError, StateError, StcError, StcTypeError,
    StcValueError, UnresolvedRefError,
)
from st_components.core.access import _resolve_path, widget_key
from st_components.core.base import render_to_element
from st_components.core.function_component import _validate_function_component_signature
from st_components.core.page import Page
from st_components.core.provider import ContextValue
from st_components.core.refs import bind_ref
from st_components.core.router import Router
from st_components.core.store import declare_shared_state, get_shared_state
from st_components.core.local_storage import get_local_store
from st_components.core.models import ContextData, HookSlot

from tests._mock import fake_ctx, _mock_st, _session_data


# =====================================================================
# Exception hierarchy
# =====================================================================

class TestExceptionHierarchy:
    """All custom exceptions inherit from StcError and from their standard base."""

    def test_stc_error_is_base_for_all(self):
        for exc_cls in (
            StcTypeError, StcValueError,
            LifecycleError, AlreadyMountedError, NotMountedError,
            RenderError, RenderDepthError,
            HookError, HookContextError, HookOrderError,
            StateError, FiberNotFoundError, SharedStateError, LocalStoreError,
            ContextError, RefError, UnresolvedRefError, CallbackError,
            ConfigError, AppError, RouterError, PageError,
            ComponentDefinitionError,
        ):
            assert issubclass(exc_cls, StcError), f"{exc_cls.__name__} not subclass of StcError"

    def test_standard_base_classes_preserved(self):
        """Users catching TypeError/RuntimeError still catch our typed errors."""
        assert issubclass(StcTypeError, TypeError)
        assert issubclass(StcValueError, ValueError)
        assert issubclass(LifecycleError, RuntimeError)
        assert issubclass(AlreadyMountedError, RuntimeError)
        assert issubclass(NotMountedError, RuntimeError)
        assert issubclass(HookError, RuntimeError)
        assert issubclass(StateError, RuntimeError)
        assert issubclass(ContextError, RuntimeError)
        assert issubclass(RenderDepthError, RecursionError)
        assert issubclass(AppError, RuntimeError)
        assert issubclass(RouterError, TypeError)
        assert issubclass(PageError, TypeError)
        assert issubclass(ComponentDefinitionError, TypeError)

    def test_catchable_as_stc_error(self):
        """A single except StcError catches everything."""
        with pytest.raises(StcError):
            raise AlreadyMountedError("test")
        with pytest.raises(StcError):
            raise StcTypeError("test")
        with pytest.raises(StcError):
            raise HookContextError("test")

    def test_hierarchy_chains(self):
        """Intermediate classes catch their subtypes."""
        with pytest.raises(LifecycleError):
            raise AlreadyMountedError("test")
        with pytest.raises(HookError):
            raise HookOrderError("test")
        with pytest.raises(StateError):
            raise FiberNotFoundError("test")
        with pytest.raises(ContextError):
            raise UnresolvedRefError("test")
        with pytest.raises(ConfigError):
            raise RouterError("test")


# =====================================================================
# Lifecycle errors
# =====================================================================

class TestLifecycleErrors:

    def test_mount_already_mounted_component(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        render(comp)
        ctx.replace("key", [])

        with pytest.raises(AlreadyMountedError, match="already mounted"):
            comp.mount()

    def test_mount_already_mounted_element(self):
        class Elem(Element):
            def render(self):
                pass

        elem = Elem(key="e")
        ctx.replace("key", [fake_ctx("app")])
        render(elem)
        ctx.replace("key", [])

        with pytest.raises(AlreadyMountedError, match="already mounted"):
            elem.mount()

    def test_unmount_not_mounted(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        with pytest.raises(NotMountedError, match="not currently mounted"):
            comp.unmount()

    def test_key_setter_raises_lifecycle_error(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        with pytest.raises(LifecycleError, match="Cannot set key"):
            comp.key = "other"

    def test_key_setter_message_includes_class_name(self):
        class MyWidget(Component):
            def render(self):
                pass

        comp = MyWidget(key="w")
        with pytest.raises(LifecycleError, match="MyWidget"):
            comp.key = "x"

    def test_already_mounted_includes_fiber_key(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        render(comp)
        ctx.replace("key", [])

        with pytest.raises(AlreadyMountedError, match="app.c"):
            comp.mount()


# =====================================================================
# Render errors
# =====================================================================

class TestRenderErrors:

    def test_render_depth_exceeded(self):
        class Infinite(Component):
            _decorate_render = lambda self: None

            def render(self):
                return Infinite(key="x")

        with pytest.raises(RenderDepthError, match="exceeded"):
            render_to_element(Infinite(key="x"))

    def test_render_depth_message_includes_class_name(self):
        class DeepLoop(Component):
            _decorate_render = lambda self: None

            def render(self):
                return DeepLoop(key="x")

        with pytest.raises(RenderDepthError, match="DeepLoop"):
            render_to_element(DeepLoop(key="x"))

    def test_element_render_must_return_none(self):
        class BadElement(Element):
            def render(self):
                return "oops"

        elem = BadElement(key="e")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(RenderError, match="must return None"):
            render(elem)
        ctx.replace("key", [])

    def test_element_render_error_includes_type(self):
        class BadElement(Element):
            def render(self):
                return 42

        elem = BadElement(key="e")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(RenderError, match="int"):
            render(elem)
        ctx.replace("key", [])

    def test_component_missing_render_raises(self):
        class Bare(Component):
            pass

        comp = Bare(key="b")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(ComponentDefinitionError, match="must implement a render"):
            render(comp)
        ctx.replace("key", [])

    def test_element_missing_render_raises(self):
        class BareElement(Element):
            pass

        elem = BareElement(key="b")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(ComponentDefinitionError, match="must implement a render"):
            render(elem)
        ctx.replace("key", [])


# =====================================================================
# Hook errors
# =====================================================================

class TestHookErrors:

    def test_hook_outside_render_raises(self):
        with pytest.raises(HookContextError, match="render cycle"):
            use_state(count=0)

    def test_use_memo_outside_render_raises(self):
        with pytest.raises(HookContextError, match="render cycle"):
            use_memo(lambda: 42)

    def test_use_effect_outside_render_raises(self):
        with pytest.raises(HookContextError, match="render cycle"):
            use_effect(lambda: None)

    def test_use_ref_outside_render_raises(self):
        with pytest.raises(HookContextError, match="render cycle"):
            use_ref()

    def test_use_callback_outside_render_raises(self):
        with pytest.raises(HookContextError, match="render cycle"):
            use_callback(lambda: None)

    def test_use_state_in_element_raises(self):
        class Elem(Element):
            def render(self):
                use_state(count=0)

        elem = Elem(key="e")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(HookContextError, match="Element.render"):
            render(elem)
        ctx.replace("key", [])

    def test_use_memo_not_callable_raises(self):
        class Comp(Component):
            def render(self):
                use_memo("not a callable")

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(StcTypeError, match="callable factory"):
            render(comp)
        ctx.replace("key", [])

    def test_use_callback_not_callable_raises(self):
        class Comp(Component):
            def render(self):
                use_callback("not callable")

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(StcTypeError, match="callable"):
            render(comp)
        ctx.replace("key", [])

    def test_use_effect_not_callable_raises(self):
        class Comp(Component):
            def render(self):
                use_effect("not callable")

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(StcTypeError, match="callable effect"):
            render(comp)
        ctx.replace("key", [])

    def test_hook_order_change_raises(self):
        call_count = [0]

        class Comp(Component):
            def render(self):
                call_count[0] += 1
                if call_count[0] == 1:
                    use_memo(lambda: 1)
                    use_ref()
                else:
                    use_ref()
                    use_memo(lambda: 1)

        ctx.replace("key", [fake_ctx("app")])
        render(Comp(key="c"))
        with pytest.raises(HookOrderError, match="Hook order changed"):
            render(Comp(key="c"))
        ctx.replace("key", [])

    def test_hook_count_decrease_raises(self):
        """Calling fewer hooks on a rerender raises HookOrderError."""
        call_count = [0]

        class Comp(Component):
            def render(self):
                call_count[0] += 1
                use_ref()
                if call_count[0] == 1:
                    use_ref()  # only on first render

        App()(Comp(key="c")).render()
        with pytest.raises(HookOrderError, match="Hook count changed"):
            App()(Comp(key="c")).render()

    def test_effect_cleanup_not_callable_raises(self):
        """Effect returning non-callable cleanup raises StcTypeError."""

        class Elem(Element):
            def render(self):
                use_effect(lambda: "not_callable", deps=[])

        # Element effects flush inline during render
        elem = Elem(key="e")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(StcTypeError, match="cleanup must be callable"):
            render(elem)
        ctx.replace("key", [])


# =====================================================================
# State errors
# =====================================================================

class TestStateErrors:

    def test_set_state_no_context_raises(self):
        with pytest.raises(ContextError, match="requires a path"):
            set_state(count=1)

    def test_set_state_missing_fiber_raises(self):
        with pytest.raises(FiberNotFoundError, match="no live fiber"):
            set_state("nonexistent.path", count=1)

    def test_set_state_on_element_raises(self):
        class Elem(Element):
            def render(self):
                pass

        elem = Elem(key="e")
        ctx.replace("key", [fake_ctx("app")])
        render(elem)
        ctx.replace("key", [])

        with pytest.raises(StateError, match="cannot target an Element"):
            set_state("app.e", count=1)

    def test_set_state_wrong_type_raises(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        render(comp)
        ctx.replace("key", [])

        with pytest.raises(StcTypeError, match="expected a dict"):
            set_state("app.c", 12345)

    def test_component_make_state_bad_type_raises(self):
        class Comp(Component):
            class S(State):
                x: int = 0

            def render(self):
                pass

        comp = Comp(key="c")
        with pytest.raises(StcTypeError, match="Cannot assign"):
            comp._make_state([1, 2, 3])

    def test_make_state_message_includes_types(self):
        class Comp(Component):
            class MyState(State):
                x: int = 0

            def render(self):
                pass

        comp = Comp(key="c")
        with pytest.raises(StcTypeError, match="MyState"):
            comp._make_state("wrong")


# =====================================================================
# Shared state / Local store errors
# =====================================================================

class TestSharedStateErrors:

    def test_get_undeclared_shared_state(self):
        with pytest.raises(SharedStateError, match="not declared"):
            get_shared_state("nonexistent_namespace")

    def test_shared_state_invalid_spec(self):
        with pytest.raises(StcTypeError, match="State instance or a State subclass"):
            declare_shared_state("bad", "not a state")

    def test_shared_state_invalid_spec_message_includes_type(self):
        with pytest.raises(StcTypeError, match="str"):
            declare_shared_state("bad", "not a state")

    def test_get_undeclared_local_store(self):
        with pytest.raises(LocalStoreError, match="not declared"):
            get_local_store("nonexistent_store")


# =====================================================================
# Context / Ref errors
# =====================================================================

class TestContextRefErrors:

    def test_widget_key_no_context_raises(self):
        ctx.replace("key", [])
        with pytest.raises(ContextError, match="requires an element path"):
            widget_key()

    def test_reset_element_no_context_raises(self):
        ctx.replace("key", [])
        with pytest.raises(ContextError, match="requires an element path"):
            reset_element()

    def test_unresolved_ref_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError, match="unresolved"):
            ref._require_path()

    def test_unresolved_ref_getitem_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError):
            ref["child"]

    def test_unresolved_ref_state_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError):
            ref.state()

    def test_unresolved_ref_parent_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError):
            _ = ref.parent

    def test_unresolved_ref_reset_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError):
            ref.reset()

    def test_unresolved_ref_reset_widget_raises(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError):
            ref.reset_widget()

    def test_resolve_path_unresolved_ref(self):
        ref = Ref()
        with pytest.raises(UnresolvedRefError, match="resolved Ref"):
            _resolve_path(ref, fn_name="test_op")

    def test_resolve_path_wrong_kind(self):
        ref = Ref()
        ref._resolve("app.comp", "component")
        with pytest.raises(RefError, match="expected a element"):
            _resolve_path(ref, expected_kind="element", fn_name="test_op")

    def test_reset_widget_on_component_ref_raises(self):
        ref = Ref._from_path("app.comp")
        with pytest.raises(RefError, match="Element refs"):
            ref.reset_widget()

    def test_bind_ref_wrong_type_raises(self):
        class FakeTarget:
            props = Props(ref="not a ref")

        with pytest.raises(StcTypeError, match="Ref instance"):
            bind_ref(FakeTarget(), "some.path", "component")

    def test_callback_outside_element_raises(self):
        with pytest.raises(CallbackError, match="Element.render"):
            callback(lambda v: v)

    def test_callback_in_component_render_raises(self):
        class Comp(Component):
            def render(self):
                callback(lambda v: v)

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        with pytest.raises(CallbackError, match="Element.render"):
            render(comp)
        ctx.replace("key", [])


# =====================================================================
# App / Config errors
# =====================================================================

class TestAppErrors:

    def test_get_app_before_creation(self):
        from st_components.core.app import get_app
        from st_components.core import _session as ss
        old = _session_data.pop(ss.CURRENT_APP, None)
        try:
            with pytest.raises(AppError, match="No current App"):
                get_app()
        finally:
            if old is not None:
                _session_data[ss.CURRENT_APP] = old

    def test_app_render_no_children_raises(self):
        with pytest.raises(AppError, match="must return a root"):
            App().render()

    def test_set_theme_wrong_type_raises(self):
        app = App()
        with pytest.raises(StcTypeError, match="dict or Theme"):
            app.set_theme(42)

    def test_set_config_wrong_type_raises(self):
        app = App()
        with pytest.raises(StcTypeError, match="dict or Config"):
            app.set_config(42)

    def test_css_source_wrong_type_raises(self):
        with pytest.raises(StcTypeError, match="CSS source type"):
            App._read_css_source(12345)


# =====================================================================
# Router / Page errors
# =====================================================================

class TestRouterPageErrors:

    def test_router_unsupported_props_raises(self):
        with pytest.raises(RouterError, match="page_title"):
            Router(page_title="Bad")

    def test_router_non_page_child_raises(self):
        router = Router(key="r")
        with pytest.raises(RouterError, match="Page children"):
            router("not a page")

    def test_router_render_raises(self):
        router = Router(key="r")
        with pytest.raises(RouterError, match="sole direct child"):
            router.render()

    def test_page_multiple_children_raises(self):
        with pytest.raises(PageError, match="exactly one child"):
            Page(key="p")("a", "b")

    def test_page_zero_children_raises(self):
        with pytest.raises(PageError, match="exactly one child"):
            Page(key="p")()

    def test_page_source_without_child_raises(self):
        page = Page(key="p")
        with pytest.raises(PageError, match="exactly one child source"):
            _ = page.source


# =====================================================================
# Component definition errors
# =====================================================================

class TestComponentDefinitionErrors:

    def test_component_decorator_not_callable(self):
        with pytest.raises(ComponentDefinitionError, match="callable"):
            component("not a function")

    def test_component_decorator_no_params(self):
        with pytest.raises(ComponentDefinitionError, match="positional parameter"):
            @component
            def NoArgs():
                pass

    def test_component_decorator_too_many_params(self):
        with pytest.raises(ComponentDefinitionError, match="positional parameter"):
            @component
            def TwoArgs(a, b):
                pass

    def test_component_decorator_kwargs_only(self):
        with pytest.raises(ComponentDefinitionError, match="positional parameter"):
            @component
            def KwargsOnly(**props):
                pass

    def test_component_decorator_error_includes_function_name(self):
        with pytest.raises(ComponentDefinitionError, match="NoArgs"):
            @component
            def NoArgs():
                pass

    def test_component_decorator_error_includes_param_count(self):
        with pytest.raises(ComponentDefinitionError, match="2"):
            @component
            def TwoArgs(a, b):
                pass


# =====================================================================
# Context provider errors
# =====================================================================

class TestContextProviderErrors:

    def test_create_context_wrong_type_raises(self):
        with pytest.raises(StcTypeError, match="ContextData"):
            create_context(42)

    def test_create_context_wrong_type_includes_actual_type(self):
        with pytest.raises(StcTypeError, match="int"):
            create_context(42)

    def test_create_context_accepts_dict(self):
        ctx_val = create_context({"key": "value"})
        assert ctx_val is not None

    def test_create_context_accepts_context_data(self):
        ctx_val = create_context(ContextData(key="value"))
        assert ctx_val is not None


# =====================================================================
# Error message quality
# =====================================================================

class TestErrorMessageQuality:
    """Verify that error messages contain actionable guidance."""

    def test_mount_error_includes_key_and_path(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="mykey")
        ctx.replace("key", [fake_ctx("app")])
        render(comp)
        ctx.replace("key", [])

        try:
            comp.mount()
        except AlreadyMountedError as e:
            msg = str(e)
            assert "mykey" in msg
            assert "app.mykey" in msg

    def test_hook_order_includes_slot_info(self):
        call_count = [0]

        class Comp(Component):
            def render(self):
                call_count[0] += 1
                if call_count[0] == 1:
                    use_memo(lambda: 1)
                else:
                    use_ref()

        ctx.replace("key", [fake_ctx("app")])
        render(Comp(key="c"))
        try:
            render(Comp(key="c"))
        except HookOrderError as e:
            msg = str(e)
            assert "slot" in msg
            assert "memo" in msg
            assert "ref" in msg
        ctx.replace("key", [])

    def test_fiber_not_found_includes_path(self):
        try:
            set_state("app.missing.widget", count=1)
        except FiberNotFoundError as e:
            assert "app.missing.widget" in str(e)

    def test_render_depth_suggests_fix(self):
        class Loop(Component):
            _decorate_render = lambda self: None

            def render(self):
                return Loop(key="x")

        try:
            render_to_element(Loop(key="x"))
        except RenderDepthError as e:
            assert "return" in str(e).lower() or "Check" in str(e)

    def test_shared_state_error_suggests_declaration(self):
        try:
            get_shared_state("missing_ns")
        except SharedStateError as e:
            assert "create_shared_state" in str(e)

    def test_local_store_error_suggests_declaration(self):
        try:
            get_local_store("missing_store")
        except LocalStoreError as e:
            assert "create_local_store" in str(e)


# =====================================================================
# Production hardening: session scoping, validation, defensive copies
# =====================================================================

class TestSessionScoping:

    def test_get_app_is_session_scoped(self):
        """App instance stored in session_state, not module global."""
        from st_components.core import _session as ss
        app = App()
        assert _session_data.get(ss.CURRENT_APP) is app

    def test_get_app_returns_session_instance(self):
        from st_components.core.app import get_app
        app = App()
        assert get_app() is app

    def test_app_stable_component_id(self):
        """App always gets a stable component_id, not an incrementing counter."""
        app1 = App()
        app2 = App()
        assert app1._component_id == app2._component_id == "App:0"

    def test_app_reinstantiation_replaces_current(self):
        """Re-creating App() replaces the current instance in session_state (Streamlit rerun pattern)."""
        from st_components.core import _session as ss
        app1 = App()
        app2 = App()
        assert _session_data.get(ss.CURRENT_APP) is app2
        assert app1 is not app2


class TestInputValidation:

    def test_declare_shared_state_namespace_must_be_str(self):
        with pytest.raises(StcTypeError, match="namespace must be a str"):
            declare_shared_state(123, State)

    def test_declare_shared_state_namespace_none_raises(self):
        with pytest.raises(StcTypeError, match="namespace must be a str"):
            declare_shared_state(None, State)

    def test_local_storage_namespace_must_be_str(self):
        from st_components.core.local_storage import local_storage
        with pytest.raises(StcTypeError, match="namespace must be a str"):
            local_storage(123)

    def test_local_storage_schema_must_be_localstore(self):
        from st_components.core.local_storage import local_storage, LocalStore
        with pytest.raises(StcTypeError, match="LocalStore subclass"):
            local_storage("test", schema=dict)

    def test_app_invalid_layout_raises(self):
        with pytest.raises(StcTypeError, match="centered.*wide"):
            App(layout="invalid")

    def test_app_invalid_sidebar_state_raises(self):
        with pytest.raises(StcTypeError, match="auto.*expanded.*collapsed"):
            App(initial_sidebar_state="invalid")

    def test_app_valid_layout_accepted(self):
        app = App(layout="wide")
        assert app.layout == "wide"

    def test_app_valid_sidebar_state_accepted(self):
        app = App(initial_sidebar_state="collapsed")
        assert app.initial_sidebar_state == "collapsed"


class TestDefensiveCopies:

    def test_ref_override_does_not_mutate_existing_dict(self):
        """Fiber overrides are copied before modification."""
        from st_components.core.models import Fiber
        from st_components.core.store import fibers as get_fibers

        get_fibers()["app.target"] = Fiber(overrides={"props": {"color": "red"}})
        original_overrides = get_fibers()["app.target"].overrides

        ref = Ref._from_path("app.target")
        ref(size=42)

        # The original dict should not have been mutated
        assert "size" not in original_overrides.get("props", {})
        # But the fiber should have the new value
        assert get_fibers()["app.target"].overrides["props"]["size"] == 42


class TestGetStateConsistency:

    def test_get_state_without_context_raises(self):
        """get_state() without args and no context raises ContextError, like set_state()."""
        ctx.replace("key", [])
        with pytest.raises(ContextError, match="requires a path"):
            get_state()

    def test_get_state_with_explicit_path_returns_none_for_missing(self):
        """get_state with explicit path returns None if fiber doesn't exist."""
        assert get_state("nonexistent.path") is None

    def test_get_state_with_ref_returns_state(self):
        class Comp(Component):
            def render(self):
                pass

        comp = Comp(key="c")
        ctx.replace("key", [fake_ctx("app")])
        render(comp)
        ctx.replace("key", [])

        ref = Ref._from_path("app.c")
        state = get_state(ref)
        assert state is not None
