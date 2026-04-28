"""React-style component framework for Streamlit.

Build stateful, reusable, composable UI components on top of Streamlit's
rendering engine.  Supports class-based and functional components, hooks,
context providers, multipage routing, and the full Streamlit widget catalog.

Quick start::

    import st_components as stc
    from st_components.elements import text_input, button, container

    class Counter(stc.Component):
        class CounterState(stc.State):
            count: int = 0

        def render(self):
            self.state.count += int(self.props.get("step", 1))
            return container(key="box")(
                text_input(key="label", value=str(self.state.count))("Count"),
                button(key="inc", on_click=lambda: None)("+1"),
            )

    stc.App(Counter(key="counter"), page_title="Demo").render()

Functional style::

    @stc.component
    def Greeting(props):
        state = stc.use_state(name="world")
        return text_input(key="name", value=state.name,
                          on_change=lambda v: state.update(name=v))("Name")
"""
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
    ThemeSection,
    component,
    create_context,
    fibers,
    get_app,
    get_shared_state,
    get_state,
    reset_element,
    set_state,
    use_callback,
    use_context,
    use_effect,
    use_id,
    use_memo,
    use_previous,
    use_ref,
    use_state,
)
from .core.errors import (
    AlreadyMountedError, AppError, CallbackError, ComponentDefinitionError,
    ConfigError, ContextError, FiberNotFoundError, HookContextError,
    HookError, HookOrderError, LifecycleError, LocalStoreError,
    NotMountedError, PageError, RefError, RenderDepthError, RenderError,
    RouterError, SharedStateError, StateError, StcError, StcTypeError,
    StcValueError, UnresolvedRefError,
)
from .core.local_storage import LocalStore, get_local_store
from .core.query_params import QueryParams


def _resolve_version():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if pyproject.is_file():
        try:
            return toml.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
        except Exception:
            pass
    try:
        return _package_version("st-components")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

__all__ = [
    "__version__",
    # Errors
    "AlreadyMountedError", "AppError", "CallbackError", "ComponentDefinitionError",
    "ConfigError", "ContextError", "FiberNotFoundError", "HookContextError",
    "HookError", "HookOrderError", "LifecycleError", "LocalStoreError",
    "NotMountedError", "PageError", "RefError", "RenderDepthError", "RenderError",
    "RouterError", "SharedStateError", "StateError", "StcError", "StcTypeError",
    "StcValueError", "UnresolvedRefError",
    # Core
    "App",
    "Component",
    "Config",
    "ContextData",
    "ContextProvider",
    "ContextValue",
    "Element",
    "LocalStore",
    "Props",
    "QueryParams",
    "Ref",
    "State",
    "Theme",
    "ThemeSection",
    "component",
    "create_context",
    "fibers",
    "get_app",
    "get_local_store",
    "get_shared_state",
    "get_state",
    "reset_element",
    "set_state",
    "use_callback",
    "use_context",
    "use_effect",
    "use_id",
    "use_memo",
    "use_previous",
    "use_ref",
    "use_state",
]
