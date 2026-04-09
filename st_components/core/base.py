import random
import string
from copy import deepcopy
from uuid import uuid4

import streamlit as st

from .context import KEY, component_context, get_key_stack, key_context, path_context
from .models import ElementFiber, ElementState, Fiber, HookSlot, Props, State
from .refs import bind_ref
from .store import fibers, register_component, track_rendered_fiber, unregister_component


def unique_id(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def to_tuple(value):
    if isinstance(value, tuple):
        return value
    return (value,)


def render_to_element(obj, index=0):
    if isinstance(obj, Element):
        return obj
    if isinstance(obj, Component):
        return render_to_element(obj.render(), index)
    return Value(key=f"value_{index}", value=obj)


def render(obj):
    if isinstance(obj, Element):
        return obj.render()
    if isinstance(obj, Component):
        return render_to_element(obj).render()
    if obj is not None:
        try:
            st.write(obj)
        except Exception:
            st.error(f"Object of type {type(obj)} can't be rendered.")


class Component:

    __fragment__ = False
    __fragment_run_every__ = None

    def __init_subclass__(cls, *, fragment=None, run_every=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if fragment is not None:
            cls.__fragment__ = fragment
        if run_every is not None:
            cls.__fragment_run_every__ = run_every
        for attr in list(vars(cls).values()):
            if isinstance(attr, type) and issubclass(attr, State) and attr is not State:
                cls.__initial_state_class__ = attr
            if isinstance(attr, type) and issubclass(attr, Props) and attr is not Props:
                cls.__props_class__ = attr

    def __init__(self, **props):
        props_cls = getattr(type(self), "__props_class__", Props)
        self.props = props_cls(props)
        initial_cls = getattr(type(self), "__initial_state_class__", None)
        self._state = initial_cls() if initial_cls is not None else State()
        self._component_id = f"{type(self).__name__}:{uuid4().hex}"
        self._fiber_key = None
        self._hook_index = 0
        self._pending_hook_effects = {}
        self._decorate_render()

    @property
    def is_mounted(self):
        return self._fiber_key is not None and self._fiber_key in fibers()

    def component_did_mount(self):
        pass

    def component_did_unmount(self):
        pass

    def component_did_update(self, prev_state):
        pass

    def mount(self):
        if not self.is_mounted:
            register_component(self._component_id, self)
            fibers()[self._fiber_key] = Fiber(state=self._state, component_id=self._component_id, previous_state=None)
            self.component_did_mount()
        else:
            raise RuntimeError("Can't mount a component that's already mounted")

    def unmount(self):
        if self.is_mounted:
            unregister_component(self.fiber.component_id)
            del fibers()[self._fiber_key]
            self.component_did_unmount()
        else:
            raise RuntimeError("Can't unmount a component that's not already mounted")

    @property
    def fiber(self):
        if self._fiber_key is None:
            return None
        return fibers().get(self._fiber_key)

    @property
    def key(self):
        return self.props.key

    @key.setter
    def key(self, value):
        raise RuntimeError("Can't set a component key on a living instance, it must be passed as a prop during init.")

    @property
    def children(self):
        return self.props.children

    @children.setter
    def children(self, value):
        self.props.children = list(value)

    def _make_state(self, data):
        cls = getattr(type(self), "__initial_state_class__", State)
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise TypeError(f"Can only assign a dict to state, got {type(data)}")

    @property
    def state(self):
        if not self.is_mounted:
            return self._state
        return self.fiber.state

    @state.setter
    def state(self, value):
        if not self.is_mounted:
            self._state = self._make_state(value)

    def set_state(self, other=None, /, **kwargs):
        if not self.is_mounted:
            if other is not None:
                self._state = self._make_state(other)
            self._state.update(**kwargs)
        else:
            if other is not None:
                self.fiber.state = self._make_state(other)
            self.fiber.state.update(**kwargs)

    def sync_state(self, state_key):
        def sync(value):
            self.state.update(**{state_key: value})
        return sync

    def _begin_hook_cycle(self):
        self._hook_index = 0
        self._pending_hook_effects = {}

    def _claim_hook_slot(self, kind):
        if not self.is_mounted:
            raise RuntimeError("Hooks require a mounted Component or Element.")

        hooks = self.fiber.hooks
        index = self._hook_index
        self._hook_index += 1

        if index == len(hooks):
            slot = HookSlot(kind=kind)
            hooks.append(slot)
            return index, slot

        slot = hooks[index]
        if slot.kind != kind:
            raise RuntimeError(
                f"Hook order changed for {type(self).__name__}: "
                f"expected {slot.kind!r} at slot {index}, got {kind!r}."
            )
        return index, slot

    def _use_hook_slot(self, kind):
        _, slot = self._claim_hook_slot(kind)
        return slot

    def _queue_hook_effect(self, index, effect):
        self._pending_hook_effects[index] = effect

    def _flush_hook_effects(self):
        if not self.is_mounted:
            return

        for index, effect in list(self._pending_hook_effects.items()):
            slot = self.fiber.hooks[index]
            if slot.cleanup is not None:
                slot.cleanup()
                slot.cleanup = None

            cleanup = effect()
            if cleanup is not None and not callable(cleanup):
                raise TypeError(
                    f"use_effect() cleanup must be callable or None, got {type(cleanup)}."
                )
            slot.cleanup = cleanup

        self._pending_hook_effects = {}

    def _cleanup_hook_effects(self):
        if self.fiber is None:
            return
        for slot in self.fiber.hooks:
            if slot.kind == "effect" and slot.cleanup is not None:
                slot.cleanup()
                slot.cleanup = None

    def _end_hook_cycle(self):
        if self.is_mounted and self._hook_index != len(self.fiber.hooks):
            raise RuntimeError(
                f"Hook count changed for {type(self).__name__}: "
                f"expected {len(self.fiber.hooks)}, got {self._hook_index}."
            )

    def __call__(self, *children):
        self.props.children = list(children)
        return self

    def _decorate_render(self):
        if not hasattr(self.render, "_decorated"):
            self.render = self._render_decorator(self.render)

    @classmethod
    def _uses_fragment(cls):
        return bool(getattr(cls, "__fragment__", getattr(cls, "fragment", False)))

    @classmethod
    def _fragment_run_every(cls):
        return getattr(cls, "__fragment_run_every__", getattr(cls, "run_every", None))

    def _render_component_body(self, render_func):
        self._fiber_key = KEY(self.key)
        bind_ref(self, self._fiber_key, "component")
        if not self.is_mounted:
            self.mount()
        if self.fiber.component_id != self._component_id:
            unregister_component(self.fiber.component_id)
            self.fiber.component_id = self._component_id
        register_component(self._component_id, self)
        track_rendered_fiber(self._fiber_key)
        with key_context(self.key), component_context(self):
            self._begin_hook_cycle()
            children = [render_to_element(child, i) for i, child in enumerate(to_tuple(render_func()))]
            self._end_hook_cycle()
            return Anchor(key=self.key)(*children)

    def _render_in_fragment(self, render_func):
        parent_keys = get_key_stack()

        def run_fragment():
            with path_context(parent_keys):
                return render(self._render_component_body(render_func))

        return st.fragment(run_every=self._fragment_run_every())(run_fragment)()

    def _render_decorator(self, render_func):
        def decorated():
            if self._uses_fragment():
                return self._render_in_fragment(render_func)
            return self._render_component_body(render_func)

        decorated._decorated = True
        return decorated

    def render(self):
        raise NotImplementedError("Component subclasses must implement a render method")


class Element(Component):
    """Terminal node in the component tree.

    Elements render Streamlit widgets imperatively and return None from render().
    Their state is read-only from outside their own render context.
    """

    # Default initial state class for elements (overridable via inner class)
    __initial_state_class__ = ElementState

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__initial_state_class__" not in vars(cls):
            cls.__initial_state_class__ = getattr(cls.__bases__[0], "__initial_state_class__", ElementState)

    def __init__(self, **props):
        super().__init__(**props)
        self._state = ElementState()

    @property
    def is_mounted(self):
        return (
            self._fiber_key is not None
            and isinstance(fibers().get(self._fiber_key), ElementFiber)
        )

    def get_output(self, raw):
        """Transform the raw session_state value before exposing it as state.output.

        *raw* is ``None`` when the widget has not yet been registered in session_state.
        Override to return a prop value as the initial default, or to apply
        post-processing to the raw value.
        """
        return raw

    def mount(self):
        if not self.is_mounted:
            from .access import widget_key
            fiber = ElementFiber(
                path=self._fiber_key,
                widget_key=widget_key(self._fiber_key),
                state=self._state,
            )
            fibers()[self._fiber_key] = fiber
        else:
            raise RuntimeError("Can't mount an element that's already mounted")

    def _current_output(self):
        """Read the current widget value from session_state and apply get_output()."""
        wk = self.fiber.widget_key if self.fiber else None
        raw = st.session_state.get(wk) if wk else None
        return self.get_output(raw)

    def _render_decorator(self, render_func):
        def decorated():
            from .access import widget_key
            element_path = KEY(self.key)
            self._fiber_key = element_path
            bind_ref(self, element_path, "element")

            if not self.is_mounted:
                self.mount()
            else:
                self.fiber.widget_key = widget_key(element_path)

            track_rendered_fiber(element_path)

            with key_context(self.key), component_context(self):
                with self.state._writable():
                    self._begin_hook_cycle()
                    result = render_func()
                    if result is not None:
                        raise TypeError(
                            f"Element.render() must return None, got {type(result).__name__!r} "
                            f"from {type(self).__name__}. Elements should render imperatively via st.* calls or recursively by calling render(child)."
                        )
                    self._end_hook_cycle()
                    self._flush_hook_effects()
                    self.state.output = self._current_output()

        decorated._decorated = True
        return decorated

    def render(self):
        raise NotImplementedError("Element subclasses must implement a render method")


class Anchor(Element):
    """Represents a Component's position in the element tree.

    An Anchor has the same key as its parent Component and renders its children
    in the right key_context, without creating its own fiber (the Component's
    Fiber already exists at this path).
    """

    def _render_decorator(self, render_func):
        def decorated():
            with key_context(self.key):
                render_func()
        decorated._decorated = True
        return decorated

    def render(self):
        for child in self.children:
            render(child)


class Value(Element):
    """Wraps a plain Python value as an Element, rendering it via st.write()."""

    def render(self):
        render(self.props.get("value"))
