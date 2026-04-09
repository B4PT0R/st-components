from contextlib import contextmanager
from typing import Optional

from modict import modict
from streamlit import session_state as state


class CallbackState(modict):
    element_path: Optional[str] = None
    widget_key: Optional[str] = None


class RuntimeState(modict):
    key_stack: list = modict.factory(list)
    component_stack: list = modict.factory(list)
    context_stacks: dict = modict.factory(dict)
    callback: CallbackState = modict.factory(CallbackState)


class PageState(modict):
    active_namespace: Optional[str] = None


class _RenderContext:
    """Transient render-cycle state: key stack, component stack, callback."""

    _KEY = "__st_components_runtime__"

    def _state(self) -> RuntimeState:
        rt = state.get(self._KEY)
        if rt is None:
            rt = RuntimeState()
            state[self._KEY] = rt
        return rt

    def reset(self):
        state[self._KEY] = RuntimeState()

    @property
    def key_stack(self):
        return self._state().key_stack

    @property
    def component_stack(self):
        return self._state().component_stack

    @property
    def callback(self) -> CallbackState:
        return self._state().callback

    @property
    def context_stacks(self) -> dict:
        return self._state().context_stacks



class _PageContext:
    """Page-scoped state: active namespace for multipage routing."""

    _KEY = "__st_components_page__"

    def _state(self) -> PageState:
        page = state.get(self._KEY)
        if page is None:
            page = PageState()
            state[self._KEY] = page
        return page

    @property
    def active_namespace(self) -> Optional[str]:
        return self._state().active_namespace

    @active_namespace.setter
    def active_namespace(self, value: Optional[str]):
        self._state().active_namespace = value


Context = _RenderContext()
PageContext = _PageContext()


def reset_context_runtime():
    Context.reset()


@contextmanager
def page_namespace(namespace):
    previous = PageContext.active_namespace
    try:
        PageContext.active_namespace = namespace
        yield namespace
    finally:
        PageContext.active_namespace = previous


@contextmanager
def key_context(key):
    try:
        Context.key_stack.append(key)
        yield key
    finally:
        if Context.key_stack:
            Context.key_stack.pop(-1)


@contextmanager
def component_context(component):
    try:
        Context.component_stack.append(component)
        yield component
    finally:
        if Context.component_stack:
            Context.component_stack.pop(-1)


@contextmanager
def callback_context(*, element_path=None, widget_key=None):
    previous_element_path = Context.callback.element_path
    previous_widget_key = Context.callback.widget_key
    try:
        Context.callback.element_path = element_path
        Context.callback.widget_key = widget_key
        yield
    finally:
        Context.callback.element_path = previous_element_path
        Context.callback.widget_key = previous_widget_key


@contextmanager
def path_context(keys):
    previous = list(Context.key_stack)
    try:
        Context.key_stack[:] = list(keys)
        yield
    finally:
        Context.key_stack[:] = previous


@contextmanager
def context_value_scope(context, value):
    stacks = Context.context_stacks
    context_id = context._id
    values = stacks.setdefault(context_id, [])
    values.append(value)
    try:
        yield value
    finally:
        if values:
            values.pop(-1)
        if not values and context_id in stacks:
            del stacks[context_id]


def get_key_stack():
    return list(Context.key_stack)


def get_active_page_namespace():
    return PageContext.active_namespace


def get_rendering_component():
    stack = Context.component_stack
    return stack[-1] if stack else None


def get_context_value(context):
    values = Context.context_stacks.get(context._id, [])
    if values:
        return values[-1]
    return context.default


def get_element_path():
    segments = list(Context.key_stack)
    if segments:
        return ".".join(segments)
    return Context.callback.element_path


def KEY(key):
    segments = list(Context.key_stack)
    segments.append(key)
    return ".".join(segments)
