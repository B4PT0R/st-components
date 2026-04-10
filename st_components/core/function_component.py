"""The ``@component`` decorator — turns a plain function into a Component class.

The generated class is cached per function object so that repeated
``@component`` calls on the same function return the same class (stable
fiber identity across reruns).
"""
import inspect
from functools import wraps

from .base import Component
from .errors import ComponentDefinitionError
from .models import Props


FUNCTION_COMPONENT_REGISTRY = {}
"""Cache: function → generated Component class (stable across reruns)."""


def _validate_function_component_signature(func):
    """Ensure *func* has exactly one positional parameter (the props argument)."""
    parameters = list(inspect.signature(func).parameters.values())
    if len(parameters) != 1:
        raise ComponentDefinitionError(
            f"@component expects a function with exactly one positional parameter (props), "
            f"but {func.__name__}() has {len(parameters)}: "
            f"{', '.join(p.name for p in parameters) or 'none'}."
        )

    parameter = parameters[0]
    if parameter.kind not in (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        raise ComponentDefinitionError(
            f"@component expects a positional parameter, but {func.__name__}() "
            f"has a {parameter.kind.name.lower()} parameter {parameter.name!r}. "
            f"Use: def {func.__name__}(props): ..."
        )


def _props_class_from_annotation(func):
    """Extract a Props subclass from the type annotation of the props parameter, if any."""
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
        raise ComponentDefinitionError(f"@component expects a callable, got {type(func).__name__!r}.")
    _validate_function_component_signature(func)

    component_class = FUNCTION_COMPONENT_REGISTRY.get(func)
    if component_class is None:
        def render(self):
            return func(self.props.exclude("key", "ref"))

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
