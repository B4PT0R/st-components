from uuid import uuid4

from modict import modict

from .base import Component, Element, _auto_key_children, _ensure_key, render, render_to_element, to_tuple
from .context import KEY, context_value_scope, get_context_value, set_context
from .models import ContextData, Props
from .refs import bind_ref
from .store import register_component, track_rendered_fiber, unregister_component


class ContextProviderProps(Props):
    context: object = modict.field(required="always")
    data: object = modict.factory(dict)


class ContextFragment(Element):
    def render(self):
        with context_value_scope(self.props.context, self.props.data):
            for child in self.children:
                render(child)


class ContextProvider(Component):
    __props_class__ = ContextProviderProps

    def _normalized_context_data(self):
        current = get_context_value(self.props.context)
        if not isinstance(current, ContextData):
            raise TypeError(
                f"use_context() expected a ContextData instance, got {type(current)}."
            )
        cls = self.props.context.data_class
        data = self.props.data
        if isinstance(data, cls):
            return data
        if isinstance(data, (ContextData, dict)):
            return cls(data)
        raise TypeError(
            f"Context Provider data must be a ContextData instance or dict, got {type(data)}."
        )

    def _render_component_body(self, render_func):
        _ensure_key(self)
        self._fiber_key = KEY(self.key)
        bind_ref(self, self._fiber_key, "component")
        if not self.is_mounted:
            self.mount()
        if self.fiber.component_id != self._component_id:
            unregister_component(self.fiber.component_id)
            self.fiber.component_id = self._component_id
        register_component(self._component_id, self)
        track_rendered_fiber(self._fiber_key)
        next_data = self._normalized_context_data()
        with set_context(key=self.key, component=self), context_value_scope(
            self.props.context, next_data
        ):
            self._begin_hook_cycle()
            raw_children = to_tuple(render_func())
            _auto_key_children(raw_children)
            children = [render_to_element(child, i) for i, child in enumerate(raw_children)]
            self._end_hook_cycle()
            return ContextFragment(
                key=self.key, context=self.props.context, data=next_data,
            )(*children)

    def render(self):
        return tuple(self.children)


class _ContextProviderFactory:
    def __init__(self, context):
        self._context = context

    def __call__(self, **props):
        return ContextProvider(context=self._context, **props)


class ContextValue:
    def __init__(self, initial, *, name=None):
        self._id = f"context:{uuid4().hex}"
        if not isinstance(initial, ContextData):
            if isinstance(initial, dict):
                initial = ContextData(initial)
            else:
                raise TypeError(
                    f"create_context(...) expects a ContextData instance or dict, got {type(initial)}."
                )
        self.default = initial
        self.data_class = type(initial)
        self.name = name
        self.Provider = _ContextProviderFactory(self)

    def __repr__(self):
        return f"ContextValue({self.name or self._id!r})"


def create_context(initial, *, name=None):
    """Create a new context with a default value.

    *initial* must be a :class:`ContextData` instance (or a plain ``dict``,
    which is auto-wrapped).  Providers override the value for their subtree::

        class ThemeData(ContextData):
            mode: str = "light"

        ThemeContext = create_context(ThemeData())

        # In a component:
        theme = use_context(ThemeContext)

        # In the tree:
        ThemeContext.Provider(key="theme", data={"mode": "dark"})(
            ChildComponent(key="child")
        )
    """
    return ContextValue(initial, name=name)
