import streamlit as st
from ..core import Element


class image(Element):
    def render(self):
        image_data = self.children[0] if self.children else self.props.get('image')
        st.image(image_data, **self.props.exclude('key', 'children', 'image', 'ref'))

class audio(Element):
    def render(self):
        data = self.children[0] if self.children else self.props.get('data')
        st.audio(data, **self.props.exclude('key', 'children', 'data', 'ref'))

class video(Element):
    def render(self):
        data = self.children[0] if self.children else self.props.get('data')
        st.video(data, **self.props.exclude('key', 'children', 'data', 'ref'))
