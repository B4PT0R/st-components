import streamlit as st
from ..core import Element, render


def _body(self):
    return self.children[0] if self.children else self.props.get('body', '')


class success(Element):
    def render(self):
        st.success(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class info(Element):
    def render(self):
        st.info(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class warning(Element):
    def render(self):
        st.warning(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class error(Element):
    def render(self):
        st.error(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class toast(Element):
    def render(self):
        st.toast(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class progress(Element):
    def render(self):
        value = self.children[0] if self.children else self.props.get('value', 0)
        st.progress(value, **self.props.exclude('key', 'children', 'value', 'ref'))

class spinner(Element):
    def render(self):
        text = self.props.get('text', 'Running...')
        with st.spinner(text):
            for child in self.children:
                render(child)

class balloons(Element):
    def render(self):
        st.balloons()

class snow(Element):
    def render(self):
        st.snow()
