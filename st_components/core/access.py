from streamlit import session_state as state

from .context import Context, get_element_path


_WIDGET_REVISIONS_KEY = "__st_components_widget_revisions__"


def set_element_value(path, value):
    state[f"{path}.value"] = value


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

    base_key = f"{element_path}.widget"
    revision = _widget_revisions().get(base_key, 0)
    if revision == 0:
        return base_key
    return f"{base_key}#{revision}"


def refresh_element(path=None):
    element_path = path or get_element_path()
    if element_path is None:
        raise RuntimeError(
            "refresh_element() requires an element path or an active element/widget callback context."
        )

    base_key = f"{element_path}.widget"
    current_key = _get_widget_key(element_path)
    if current_key in state:
        del state[current_key]

    revisions = _widget_revisions()
    revisions[base_key] = revisions.get(base_key, 0) + 1
    state[_WIDGET_REVISIONS_KEY] = revisions


def get_element_value(path=None, default=None):
    element_path = path or get_element_path()
    if element_path is None:
        raise RuntimeError(
            "get_element_value() requires an element path or an active element/widget callback context."
        )
    value_key = f"{element_path}.value"
    if value_key in state:
        return state.get(value_key, default)

    if path is None and Context.callback.widget_key is not None:
        return state.get(Context.callback.widget_key, default)

    return state.get(_get_widget_key(element_path), default)
