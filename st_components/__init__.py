from importlib.metadata import PackageNotFoundError, version as _package_version
from pathlib import Path

import toml

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


def _resolve_version():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if pyproject.is_file():
        try:
            return toml.loads(pyproject.read_text())["project"]["version"]
        except Exception:
            pass
    try:
        return _package_version("st-components")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

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
