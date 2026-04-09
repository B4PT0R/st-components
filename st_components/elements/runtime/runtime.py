from contextlib import ContextDecorator

import streamlit as st


def _placeholder_from_ref(ref, helper_name: str):
    placeholder = ref.state().handle
    if placeholder is None:
        raise RuntimeError(f"{helper_name}() requires a rendered placeholder Ref with a runtime handle.")
    if not hasattr(placeholder, "__enter__") or not hasattr(placeholder, "__exit__"):
        raise RuntimeError(f"{helper_name}() requires a Ref pointing to a placeholder/container context manager.")
    return placeholder


class _SpinnerContext(ContextDecorator):
    def __init__(self, *, ref, text: str = "In progress...", **kwargs):
        self.ref = ref
        self.text = text
        self.kwargs = kwargs
        self._placeholder_cm = None
        self._spinner_cm = None

    def __enter__(self):
        self._placeholder_cm = _placeholder_from_ref(self.ref, "show_spinner")
        self._placeholder_cm.__enter__()
        self._spinner_cm = st.spinner(self.text, **self.kwargs)
        return self._spinner_cm.__enter__()

    def __exit__(self, exc_type, exc, tb):
        suppress = False
        if self._spinner_cm is not None:
            suppress = bool(self._spinner_cm.__exit__(exc_type, exc, tb))
        if self._placeholder_cm is not None:
            placeholder_suppress = self._placeholder_cm.__exit__(exc_type, exc, tb)
            suppress = bool(placeholder_suppress) or suppress
        return suppress


def show_spinner(*, ref, text: str = "In progress...", **kwargs):
    return _SpinnerContext(ref=ref, text=text, **kwargs)


class _ProgressHandle:
    def __init__(self, *, ref, value=0, text=None, **kwargs):
        self.ref = ref
        self.kwargs = kwargs
        self.placeholder = _placeholder_from_ref(ref, "show_progress")
        self.update(value, text=text)

    def update(self, value, text=None, **kwargs):
        render_kwargs = dict(self.kwargs)
        render_kwargs.update(kwargs)
        with self.placeholder:
            self._bar = st.progress(value, text=text, **render_kwargs)
        return self

    def clear(self):
        if hasattr(self.placeholder, "empty"):
            self.placeholder.empty()
        return None


def show_progress(*, ref, value=0, text=None, **kwargs):
    return _ProgressHandle(ref=ref, value=value, text=text, **kwargs)


def show_balloons():
    st.balloons()


def show_snow():
    st.snow()


def show_toast(body, **kwargs):
    st.toast(body, **kwargs)
