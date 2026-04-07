from importlib.metadata import PackageNotFoundError, version as _package_version
from pathlib import Path

import toml

from .core import (
    App,
    Component,
    Config,
    ContextData,
    ContextProvider,
    ContextValue,
    Element,
    Props,
    Ref,
    State,
    Theme,
    component,
    create_context,
    get_app,
    get_component_state,
    get_element_value,
    get_shared_state,
    reset_element,
    use_callback,
    use_context,
    use_effect,
    use_id,
    use_memo,
    use_previous,
    use_ref,
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
    "ContextData",
    "ContextProvider",
    "ContextValue",
    "Element",
    "Props",
    "Ref",
    "State",
    "Theme",
    "component",
    "create_context",
    "get_app",
    "get_component_state",
    "get_element_value",
    "get_shared_state",
    "reset_element",
    "use_callback",
    "use_context",
    "use_effect",
    "use_id",
    "use_memo",
    "use_previous",
    "use_ref",
    "use_state",
]
