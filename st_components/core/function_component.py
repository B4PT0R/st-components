import inspect
from functools import wraps

from .base import Component


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


def component(func=None, *, fragment=False, run_every=None):
    if func is None:
        return lambda actual_func: component(actual_func, fragment=fragment, run_every=run_every)

    if not callable(func):
        raise TypeError(f"@component expects a callable, got {type(func)}")
    _validate_function_component_signature(func)

    registry_key = (func, fragment, run_every)
    component_class = FUNCTION_COMPONENT_REGISTRY.get(registry_key)
    if component_class is None:
        def render(self):
            return func(_component_props(self.props))

        component_class = type(
            func.__name__,
            (Component,),
            {
                "__doc__": func.__doc__,
                "__module__": func.__module__,
                "__qualname__": getattr(func, "__qualname__", func.__name__),
                "__wrapped__": func,
                "__fragment__": fragment,
                "__fragment_run_every__": run_every,
                "render": render,
            },
        )
        FUNCTION_COMPONENT_REGISTRY[registry_key] = component_class

    @wraps(func)
    def instantiate(**props):
        return component_class(**props)

    instantiate.component_class = component_class
    return instantiate
