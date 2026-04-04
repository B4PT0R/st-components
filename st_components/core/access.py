from streamlit import session_state as state

from .context import get_element_path


def set_element_value(path, value):
    state[f"{path}.value"] = value


def get_element_value(path=None, default=None):
    element_path = path or get_element_path()
    if element_path is None:
        raise RuntimeError(
            "get_element_value() requires an element path or an active element/widget callback context."
        )
    value_key = f"{element_path}.value"
    if value_key in state:
        return state.get(value_key, default)
    return state.get(f"{element_path}.widget", default)
