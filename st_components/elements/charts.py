import streamlit as st
from ..core import Element, KEY, callback_context, get_element_path, set_element_value


def _chart_data(self):
    return self.children[0] if self.children else self.props.get('data')


def _selection_callback(self, callback_name='on_select'):
    callback = self.props.get(callback_name)
    if callback is None:
        return None

    args = tuple(self.props.get('args', ()))
    kwargs = dict(self.props.get('kwargs', {}))
    element_path = get_element_path()
    widget_key = KEY("widget")

    def wrapped(selection=None):
        if selection is not None:
            set_element_value(element_path, selection)
        with callback_context(element_path=element_path, widget_key=widget_key):
            return callback(*args, **kwargs)

    return wrapped


def _is_display_generator(value):
    try:
        from streamlit.delta_generator import DeltaGenerator
    except Exception:
        return False
    return isinstance(value, DeltaGenerator)


def _selection_prop(self):
    on_select = self.props.get('on_select', 'ignore')
    if callable(on_select):
        return _selection_callback(self)
    return on_select


def _store_selection(path, value):
    if value is not None and not _is_display_generator(value):
        set_element_value(path, value)


class area_chart(Element):
    def render(self):
        data = _chart_data(self)
        return st.area_chart(data, **self.props.exclude('key', 'children', 'data', 'ref'))


class bar_chart(Element):
    def render(self):
        data = _chart_data(self)
        return st.bar_chart(data, **self.props.exclude('key', 'children', 'data', 'ref'))


class line_chart(Element):
    def render(self):
        data = _chart_data(self)
        return st.line_chart(data, **self.props.exclude('key', 'children', 'data', 'ref'))


class scatter_chart(Element):
    def render(self):
        data = _chart_data(self)
        return st.scatter_chart(data, **self.props.exclude('key', 'children', 'data', 'ref'))


class map(Element):
    def render(self):
        data = _chart_data(self)
        return st.map(data, **self.props.exclude('key', 'children', 'data', 'ref'))


class graphviz_chart(Element):
    def render(self):
        figure_or_dot = self.children[0] if self.children else self.props.get('figure_or_dot')
        return st.graphviz_chart(figure_or_dot, **self.props.exclude('key', 'children', 'figure_or_dot', 'ref'))


class plotly_chart(Element):
    def render(self):
        figure_or_data = self.children[0] if self.children else self.props.get('figure_or_data')
        element_path = get_element_path()
        value = st.plotly_chart(
            figure_or_data,
            key=KEY("widget"),
            on_select=_selection_prop(self),
            **self.props.exclude('key', 'children', 'figure_or_data', 'ref', 'on_select', 'args', 'kwargs'),
        )
        _store_selection(element_path, value)
        return value


class altair_chart(Element):
    def render(self):
        altair_obj = self.children[0] if self.children else self.props.get('altair_chart')
        element_path = get_element_path()
        value = st.altair_chart(
            altair_obj,
            key=KEY("widget"),
            on_select=_selection_prop(self),
            **self.props.exclude('key', 'children', 'altair_chart', 'ref', 'on_select', 'args', 'kwargs'),
        )
        _store_selection(element_path, value)
        return value


class vega_lite_chart(Element):
    def render(self):
        data = _chart_data(self)
        element_path = get_element_path()
        value = st.vega_lite_chart(
            data,
            key=KEY("widget"),
            on_select=_selection_prop(self),
            **self.props.exclude('key', 'children', 'data', 'ref', 'on_select', 'args', 'kwargs'),
        )
        _store_selection(element_path, value)
        return value


class pydeck_chart(Element):
    def render(self):
        pydeck_obj = self.children[0] if self.children else self.props.get('pydeck_obj')
        element_path = get_element_path()
        value = st.pydeck_chart(
            pydeck_obj,
            key=KEY("widget"),
            on_select=_selection_prop(self),
            **self.props.exclude('key', 'children', 'pydeck_obj', 'ref', 'on_select', 'args', 'kwargs'),
        )
        _store_selection(element_path, value)
        return value


class pyplot(Element):
    def render(self):
        fig = self.children[0] if self.children else self.props.get('fig')
        return st.pyplot(fig, **self.props.exclude('key', 'children', 'fig', 'ref'))


class bokeh_chart(Element):
    def render(self):
        figure = self.children[0] if self.children else self.props.get('figure')
        return st.bokeh_chart(figure, **self.props.exclude('key', 'children', 'figure', 'ref'))
