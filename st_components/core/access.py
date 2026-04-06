from streamlit import session_state as state

from .context import Context, get_element_path


_WIDGET_REVISIONS_KEY = "__st_components_widget_revisions__"


def set_element_value(path, value):
    state[f"{path}.value"] = value


def _base_value_key(path: str) -> str:
    return f"{path}.value"


def _resolve_path(path_or_ref=None, *, expected_kind=None, fn_name="operation"):
    if path_or_ref is None:
        return get_element_path()

    try:
        from .refs import Ref
    except Exception:
        Ref = None

    if Ref is not None and isinstance(path_or_ref, Ref):
        if path_or_ref.path is None:
            raise RuntimeError(
                f"{fn_name}() requires a resolved Ref. Attach it to a Component or Element and render the tree first."
            )
        if expected_kind is not None and path_or_ref.kind != expected_kind:
            raise RuntimeError(
                f"{fn_name}() expected a {expected_kind} Ref, got {path_or_ref.kind!r}."
            )
        return path_or_ref.path

    return path_or_ref


def _widget_revisions():
    revisions = state.get(_WIDGET_REVISIONS_KEY)
    if revisions is None:
        revisions = {}
        state[_WIDGET_REVISIONS_KEY] = revisions
    return revisions


def _get_widget_key(path=None):
    element_path = path or get_element_path()
    if element_path is None:
        raise RuntimeError(
            "_get_widget_key() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    revision = _widget_revisions().get(base_key, 0)
    if revision == 0:
        return base_key
    return f"{base_key}#{revision}"


def refresh_element(path=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="refresh_element")
    if element_path is None:
        raise RuntimeError(
            "refresh_element() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    current_key = _get_widget_key(element_path)
    if base_key in state:
        del state[base_key]
    if current_key in state:
        del state[current_key]

    revisions = _widget_revisions()
    revisions[base_key] = revisions.get(base_key, 0) + 1
    state[_WIDGET_REVISIONS_KEY] = revisions


def get_element_value(path=None, default=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="get_element_value")
    if element_path is None:
        raise RuntimeError(
            "get_element_value() requires an element path or an active element/widget callback context."
        )
    value_key = _base_value_key(element_path)
    if value_key in state:
        return state.get(value_key, default)

    if path is None and Context.callback.widget_key is not None:
        return state.get(Context.callback.widget_key, default)

    return state.get(_get_widget_key(element_path), default)


def get_component_state(path):
    component_path = _resolve_path(path, expected_kind="component", fn_name="get_component_state")
    if component_path is None:
        raise RuntimeError(
            "get_component_state() requires a component path or a component Ref."
        )

    from .store import fibers

    fiber = fibers().get(component_path)
    if fiber is None:
        raise RuntimeError(f"No mounted component found at path {component_path!r}.")
    return fiber.state
