import random
import string

import streamlit as st

from .context import KEY, component_context, get_key_stack, key_context, path_context
from .models import Props
from .refs import bind_ref
from .store import Fiber, State, fibers, track_rendered_fiber


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

    def __init__(self, **props):
        self.props = Props(props)
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
        self.props.children = value

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

    def __init__(self, **props):
        self.props = Props(props)
        self._state = State()
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
            fibers()[self._fiber_key] = Fiber(state=self._state, component=self, rendered_state=None)
            self.component_did_mount()
        else:
            raise RuntimeError("Can't mount a component that's already mounted")

    def unmount(self):
        if self.is_mounted:
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
        self.props.children = value

    @property
    def state(self):
        if not self.is_mounted:
            return self._state
        return self.fiber.state

    @state.setter
    def state(self, value):
        if not self.is_mounted:
            self._state = State(**value)

    def set_state(self, other=None, /, **kwargs):
        if not self.is_mounted:
            if other is not None:
                if isinstance(other, dict):
                    self._state = State(**other)
                else:
                    raise TypeError(f"Can only assign a dict to state, got {type(other)}")
            self._state.update(**kwargs)
        else:
            if other is not None:
                if isinstance(other, dict):
                    self.fiber.state = State(**other)
                else:
                    raise TypeError(f"Can only assign a dict to state, got {type(other)}")
            self.fiber.state.update(**kwargs)

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
        self.fiber.component = self
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
