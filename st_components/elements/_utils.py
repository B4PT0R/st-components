from ..core import callback_context, get_element_path, set_element_value
from ..core.access import _get_widget_key


def child_or_prop(element, prop_name, default=None):
    return element.children[0] if element.children else element.props.get(prop_name, default)


def is_display_generator(value):
    try:
        from streamlit.delta_generator import DeltaGenerator
    except Exception:
        return False
    return isinstance(value, DeltaGenerator)


def store_element_value(path, value):
    if value is not None and not is_display_generator(value):
        set_element_value(path, value)


def selection_callback(element, callback_name="on_select"):
    callback = element.props.get(callback_name)
    if callback is None:
        return None

    element_path = get_element_path()
    widget_key = _get_widget_key(element_path)

    def wrapped(selection=None):
        if selection is not None:
            set_element_value(element_path, selection)
        with callback_context(element_path=element_path, widget_key=widget_key):
            return callback(selection)

    return wrapped


def selection_prop(element, callback_name="on_select"):
    on_select = element.props.get(callback_name, "ignore")
    if callable(on_select):
        return selection_callback(element, callback_name)
    return on_select
