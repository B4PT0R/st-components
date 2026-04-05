from importlib.metadata import version as _package_version

from .core import (
    App,
    Component,
    Config,
    Element,
    Props,
    Ref,
    State,
    Theme,
    component,
    get_app,
    get_component_state,
    get_element_value,
    get_shared_state,
    use_state,
)

__version__ = _package_version("st-components")

__all__ = [
    "__version__",
    "App",
    "Component",
    "Config",
    "Element",
    "Props",
    "Ref",
    "State",
    "Theme",
    "component",
    "get_app",
    "get_component_state",
    "get_element_value",
    "get_shared_state",
    "use_state",
]
