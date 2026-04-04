from .base import Component
from .context import get_rendering_component


def use_state(**kwargs):
    current = get_rendering_component()
    if not isinstance(current, Component):
        raise RuntimeError("use_state() must be called while rendering a Component.")

    if current.is_mounted and current.fiber.rendered_state is None and kwargs:
        current.set_state(kwargs)

    return current.state
