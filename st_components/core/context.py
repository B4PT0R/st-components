from contextlib import contextmanager

from streamlit import session_state as state


RUNTIME_KEY = "__st_components_runtime__"


def _runtime():
    runtime = state.get(RUNTIME_KEY)
    if runtime is None:
        runtime = {
            "key_stack": [],
            "component_stack": [],
            "callback": {
                "element_path": None,
                "widget_key": None,
            },
        }
        state[RUNTIME_KEY] = runtime
    return runtime


def _key_stack():
    return _runtime()["key_stack"]


def _component_stack():
    return _runtime()["component_stack"]


def _callback():
    return _runtime()["callback"]


def _active_page_namespace():
    return _runtime().get("active_page_namespace")


class _ContextProxy:

    @property
    def stack(self):
        return _key_stack()


class _CallbackContextProxy:

    @property
    def element_path(self):
        return _callback()["element_path"]

    @element_path.setter
    def element_path(self, value):
        _callback()["element_path"] = value

    @property
    def widget_key(self):
        return _callback()["widget_key"]

    @widget_key.setter
    def widget_key(self, value):
        _callback()["widget_key"] = value


Context = _ContextProxy()
CallbackContext = _CallbackContextProxy()


def reset_context_runtime():
    runtime = _runtime()
    runtime["key_stack"].clear()
    runtime["component_stack"].clear()
    runtime["callback"]["element_path"] = None
    runtime["callback"]["widget_key"] = None


@contextmanager
def page_namespace(namespace):
    runtime = _runtime()
    previous = runtime.get("active_page_namespace")
    try:
        runtime["active_page_namespace"] = namespace
        yield namespace
    finally:
        runtime["active_page_namespace"] = previous


@contextmanager
def key_context(key):
    try:
        _key_stack().append(key)
        yield key
    finally:
        if _key_stack():
            _key_stack().pop(-1)


@contextmanager
def component_context(component):
    try:
        _component_stack().append(component)
        yield component
    finally:
        if _component_stack():
            _component_stack().pop(-1)


@contextmanager
def callback_context(*, element_path=None, widget_key=None):
    previous_element_path = CallbackContext.element_path
    previous_widget_key = CallbackContext.widget_key
    try:
        CallbackContext.element_path = element_path
        CallbackContext.widget_key = widget_key
        yield
    finally:
        CallbackContext.element_path = previous_element_path
        CallbackContext.widget_key = previous_widget_key


@contextmanager
def path_context(keys):
    stack = _key_stack()
    previous_stack = list(stack)
    try:
        stack[:] = list(keys)
        yield
    finally:
        stack[:] = previous_stack


def get_key_stack():
    return list(_key_stack())


def get_active_page_namespace():
    return _active_page_namespace()


def get_rendering_component():
    stack = _component_stack()
    if stack:
        return stack[-1]
    return None


def get_element_path():
    segments = []
    if _active_page_namespace():
        segments.append(f"page[{_active_page_namespace()}]")
    segments.extend(_key_stack())
    if segments:
        return ".".join(segments)
    return CallbackContext.element_path


def KEY(key):
    segments = []
    if _active_page_namespace():
        segments.append(f"page[{_active_page_namespace()}]")
    segments.extend(_key_stack())
    segments.append(key)
    return ".".join(segments)
