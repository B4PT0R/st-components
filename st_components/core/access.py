from streamlit import session_state as state

from .context import Context, get_element_path


_WIDGET_REVISIONS_KEY = "__st_components_widget_revisions__"


def _raw_key(path: str) -> str:
    """Key under which layout element Streamlit objects are stored (e.g. container, form)."""
    return f"{path}.raw"


def _base_value_key(path: str) -> str:
    """Key under which input widget Streamlit values are stored."""
    return f"{path}.raw"


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


def set_element_value(path, value):
    from .store import fibers
    from .models import ElementFiber
    fiber = fibers().get(path)
    if isinstance(fiber, ElementFiber):
        fiber["cache"] = value


def reset_element(path=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="reset_element")
    if element_path is None:
        raise RuntimeError(
            "reset_element() requires an element path or an active element/widget callback context."
        )

    base_key = _base_value_key(element_path)
    current_key = _get_widget_key(element_path)
    if base_key in state:
        del state[base_key]
    if current_key in state and current_key != base_key:
        del state[current_key]

    revisions = _widget_revisions()
    revisions[base_key] = revisions.get(base_key, 0) + 1
    state[_WIDGET_REVISIONS_KEY] = revisions

    from .store import fibers
    from .models import ElementFiber
    from modict import MISSING
    fiber = fibers().get(element_path)
    if isinstance(fiber, ElementFiber):
        fiber["cache"] = MISSING


def get_state(path_or_ref=None):
    from .store import fibers
    path = _resolve_path(path_or_ref) if path_or_ref is not None else get_element_path()
    if path is None:
        return None
    fiber = fibers().get(path)
    if fiber is None:
        return None
    return fiber.state


def get_element_value(path=None, default=None):
    element_path = _resolve_path(path, expected_kind="element", fn_name="get_element_value") if path is not None else get_element_path()
    if element_path is None:
        if Context.callback.widget_key is not None:
            return state.get(Context.callback.widget_key, default)
        return default

    result = get_state(element_path)
    if result is not None and result.value is not None:
        return result.value

    if path is None and Context.callback.widget_key is not None:
        return state.get(Context.callback.widget_key, default)

    return state.get(_get_widget_key(element_path), default)


def get_component_state(path):
    return get_state(path)
