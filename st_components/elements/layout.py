import streamlit as st
from ..core import Element, KEY, get_key_stack, path_context, render


class container(Element):
    def render(self):
        with st.container(key=KEY("st_container"), **self.props.exclude('key', 'children', 'ref')):
            for child in self.children:
                render(child)

class columns(Element):
    def render(self):
        spec = self.props.get('spec', len(self.children))
        cols = st.columns(spec=spec, **self.props.exclude('key', 'children', 'spec', 'ref'))
        for child, col in zip(self.children, cols):
            with col:
                render(child)

class tabs(Element):
    def render(self):
        labels = self.props.get('labels', [str(i) for i in range(len(self.children))])
        tab_objs = st.tabs(labels)
        for child, tab_obj in zip(self.children, tab_objs):
            with tab_obj:
                render(child)

class form(Element):
    def render(self):
        form_key = KEY("st_form")
        with st.form(form_key, **self.props.exclude('key', 'children', 'ref')):
            for child in self.children:
                render(child)

class dialog(Element):
    def render(self):
        title = self.props.get('title', '')
        args = tuple(self.props.get('args', ()))
        kwargs = dict(self.props.get('kwargs', {}))
        on_dismiss = self.props.get('on_dismiss', 'ignore')
        context_keys = get_key_stack()

        def dismiss_callback():
            if callable(on_dismiss):
                return on_dismiss(*args, **kwargs)
            return on_dismiss

        @st.dialog(
            title,
            **self.props.exclude('key', 'children', 'title', 'ref', 'on_dismiss', 'args', 'kwargs'),
            on_dismiss=dismiss_callback if callable(on_dismiss) else on_dismiss,
        )
        def body():
            with path_context(context_keys):
                for child in self.children:
                    render(child)

        return body()

class chat_message(Element):
    def render(self):
        name = self.props.get('name', 'assistant')
        with st.chat_message(name, **self.props.exclude('key', 'children', 'name', 'ref')):
            for child in self.children:
                render(child)

class status(Element):
    def render(self):
        label = self.props.get('label', '')
        with st.status(label, **self.props.exclude('key', 'children', 'label', 'ref')):
            for child in self.children:
                render(child)

class expander(Element):
    def render(self):
        with st.expander(**self.props.exclude('key', 'children', 'ref')):
            for child in self.children:
                render(child)

class popover(Element):
    def render(self):
        with st.popover(**self.props.exclude('key', 'children', 'ref')):
            for child in self.children:
                render(child)

class sidebar(Element):
    def render(self):
        with st.sidebar:
            for child in self.children:
                render(child)

class empty(Element):
    def render(self):
        placeholder = st.empty()
        if self.children:
            with placeholder:
                render(self.children[0])
        return placeholder
