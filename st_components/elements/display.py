import streamlit as st
from ..core import Element, KEY, get_element_path, set_element_value


class write(Element):
    def render(self):
        st.write(*self.children, **self.props.exclude('key', 'children', 'ref'))

class dataframe(Element):
    def render(self):
        data = self.children[0] if self.children else self.props.get('data')
        st.dataframe(data, **self.props.exclude('key', 'children', 'data', 'ref'))

class table(Element):
    def render(self):
        data = self.children[0] if self.children else self.props.get('data')
        st.table(data, **self.props.exclude('key', 'children', 'data', 'ref'))

class metric(Element):
    def render(self):
        label = self.children[0] if self.children else self.props.get('label', '')
        st.metric(label, **self.props.exclude('key', 'children', 'label', 'ref'))

class json(Element):
    def render(self):
        body = self.children[0] if self.children else self.props.get('body')
        st.json(body, **self.props.exclude('key', 'children', 'body', 'ref'))


class html(Element):
    def render(self):
        body = self.children[0] if self.children else self.props.get('body', '')
        st.html(body, **self.props.exclude('key', 'children', 'body', 'ref'))


class iframe(Element):
    def render(self):
        src = self.children[0] if self.children else self.props.get('src')
        st.iframe(src, **self.props.exclude('key', 'children', 'src', 'ref'))


class pdf(Element):
    def render(self):
        data = self.children[0] if self.children else self.props.get('data')
        st.pdf(data, key=KEY("st_pdf"), **self.props.exclude('key', 'children', 'data', 'ref'))


class exception(Element):
    def render(self):
        error = self.children[0] if self.children else self.props.get('exception')
        st.exception(error, **self.props.exclude('key', 'children', 'exception', 'ref'))


class help(Element):
    def render(self):
        obj = self.children[0] if self.children else self.props.get('obj')
        st.help(obj, **self.props.exclude('key', 'children', 'obj', 'ref'))


class page_link(Element):
    def render(self):
        page = self.children[0] if self.children else self.props.get('page')
        st.page_link(page, **self.props.exclude('key', 'children', 'page', 'ref'))


class logo(Element):
    def render(self):
        image_data = self.children[0] if self.children else self.props.get('image')
        st.logo(image_data, **self.props.exclude('key', 'children', 'image', 'ref'))


class write_stream(Element):
    def render(self):
        stream = self.children[0] if self.children else self.props.get('stream')
        result = st.write_stream(stream, **self.props.exclude('key', 'children', 'stream', 'ref'))
        set_element_value(get_element_path(), result)
        return result
