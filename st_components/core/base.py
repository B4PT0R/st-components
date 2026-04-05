import random
import string
from uuid import uuid4

import streamlit as st

from .context import KEY, component_context, get_key_stack, key_context, path_context
from .access import get_element_value
from .models import Fiber, Props, State
from .refs import bind_ref
from .store import fibers, register_component, track_rendered_fiber, unregister_component



def unique_id(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def to_tuple(value):
    if isinstance(value, tuple):
        return value
    return (value,)


def render_to_element(obj):
    if isinstance(obj, Element):
        return obj
    if isinstance(obj, Component):
        return render_to_element(obj.render())
    return Primitive(value=obj)


def render(obj):
    if isinstance(obj, Element):
        return obj.render()
    if isinstance(obj, Component):
        return render_to_element(obj).render()
    if obj is not None:
        try:
            return st.write(obj)
        except Exception:
            return st.error(f"Object of type {type(obj)} can't be rendered.")


class Element:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in list(vars(cls).values()):
            if isinstance(attr, type) and issubclass(attr, Props) and attr is not Props:
                cls.__props_class__ = attr

    def __init__(self, **props):
        props_cls = getattr(type(self), "__props_class__", Props)
        self.props = props_cls(props)
        self._decorate_render()

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

    def __call__(self, *children):
        self.props.children = list(children)
        return self

    def _decorate_render(self):
        if not hasattr(self.render, "_decorated"):
            self.render = self._render_decorator(self.render)

    def _render_decorator(self, render_func):
        def decorated():
            element_path = KEY(self.key)
            bind_ref(self, element_path, "element")
            with key_context(self.key):
                result = render_func()
                return render(result) if isinstance(result, Element) else result

        decorated._decorated = True
        return decorated

    def render(self):
        raise NotImplementedError("Element subclasses must implement a render method")


class Fragment(Element):

    def render(self):
        for child in self.children:
            render(child)


class Primitive(Element):

    def __init__(self, value=None):
        super().__init__(key=unique_id())
        self.value = value

    def render(self):
        return self.value


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
        def sync():
            self.state.update(**{state_key: get_element_value()})

        return sync

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
            children = map(render_to_element, to_tuple(render_func()))
            return Fragment(key=self.key)(*children)

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
