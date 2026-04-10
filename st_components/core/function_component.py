import inspect
from functools import wraps

from .base import Component
from .models import Props


FUNCTION_COMPONENT_REGISTRY = {}


def _component_props(props):
    return props.exclude("key", "ref")


def _validate_function_component_signature(func):
    parameters = list(inspect.signature(func).parameters.values())
    if len(parameters) != 1:
        raise TypeError("@component expects a function with signature func(props)")

    parameter = parameters[0]
    if parameter.kind not in (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        raise TypeError("@component expects a function with signature func(props)")


def _props_class_from_annotation(func):
    params = list(inspect.signature(func).parameters.values())
    annotation = params[0].annotation
    if annotation is inspect.Parameter.empty:
        return None
    if isinstance(annotation, type) and issubclass(annotation, Props) and annotation is not Props:
        return annotation
    return None


def component(func):
    """Decorator that turns a function into a Component.

    The function must accept a single ``props`` argument::

        @component
        def Greeting(props):
            state = use_state(name="world")
            return text_input(key="name", value=state.name)("Name")

    Use as a factory::

        Greeting(key="g", extra_prop="value")

    For scoped re-rendering, wrap the return value in a ``fragment``
    element instead of annotating the decorator::

        from st_components.elements import fragment

        @component
        def LiveFeed(props):
            return fragment(key="f", scoped=True, run_every="5s")(
                my_chart, my_controls,
            )

    Type the ``props`` argument for IDE completion::

        class BadgeProps(Props):
            label: str = ""
            color: str = "blue"

        @component
        def Badge(props: BadgeProps):
            ...
    """
    if not callable(func):
        raise TypeError(f"@component expects a callable, got {type(func)}")
    _validate_function_component_signature(func)

    component_class = FUNCTION_COMPONENT_REGISTRY.get(func)
    if component_class is None:
        def render(self):
            return func(_component_props(self.props))

        class_dict = {
            "__doc__": func.__doc__,
            "__module__": func.__module__,
            "__qualname__": getattr(func, "__qualname__", func.__name__),
            "__wrapped__": func,
            "render": render,
        }

        props_cls = _props_class_from_annotation(func)
        if props_cls is not None:
            class_dict["__props_class__"] = props_cls

        component_class = type(func.__name__, (Component,), class_dict)
        FUNCTION_COMPONENT_REGISTRY[func] = component_class

    @wraps(func)
    def instantiate(**props):
        return component_class(**props)

    instantiate.component_class = component_class
    return instantiate
