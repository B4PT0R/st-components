import streamlit as st
from ..core import Element, KEY


def _body(self):
    return self.children[0] if self.children else self.props.get('body', '')


class title(Element):
    def render(self):
        st.title(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class header(Element):
    def render(self):
        st.header(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class subheader(Element):
    def render(self):
        st.subheader(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class caption(Element):
    def render(self):
        st.caption(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class text(Element):
    def render(self):
        st.text(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class markdown(Element):
    def render(self):
        st.markdown(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class code(Element):
    def render(self):
        st.code(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class latex(Element):
    def render(self):
        st.latex(_body(self), **self.props.exclude('key', 'children', 'body', 'ref'))

class divider(Element):
    def render(self):
        st.divider()


class badge(Element):
    def render(self):
        label = _body(self)
        st.badge(label, **self.props.exclude('key', 'children', 'body', 'ref'))


class space(Element):
    def render(self):
        size = self.props.get('size', 'small')
        st.space(size)
