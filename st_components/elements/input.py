import streamlit as st
from ..core import Element, KEY, callback_context, get_element_path, set_element_value


def _label(self):
    return self.children[0] if self.children else self.props.get('label', '')


def _data(self):
    return self.children[0] if self.children else self.props.get('data')


def _widget_callback(self, callback_name='on_change'):
    callback = self.props.get(callback_name)
    if callback is None:
        return None

    args = tuple(self.props.get('args', ()))
    kwargs = dict(self.props.get('kwargs', {}))
    element_path = get_element_path()
    widget_key = KEY("widget")

    def wrapped():
        with callback_context(element_path=element_path, widget_key=widget_key):
            return callback(*args, **kwargs)

    return wrapped


def _widget_props(self, *excluded):
    return self.props.exclude('key', 'children', 'label', 'ref', 'on_change', 'args', 'kwargs', *excluded)


def _resolve_data_editor_value(data, editing_state):
    if editing_state is None:
        return data

    try:
        import pyarrow as pa
        from streamlit import dataframe_util
        from streamlit.elements.widgets.data_editor import (
            DataEditorSerde,
            _apply_dataframe_edits,
            determine_dataframe_schema,
        )
    except Exception:
        return data

    data_format = dataframe_util.determine_data_format(data)
    data_df = dataframe_util.convert_anything_to_pandas_df(data, ensure_copy=True)
    arrow_table = pa.Table.from_pandas(data_df)
    dataframe_schema = determine_dataframe_schema(data_df, arrow_table.schema)

    if isinstance(editing_state, str):
        editing_state = DataEditorSerde().deserialize(editing_state)

    _apply_dataframe_edits(data_df, editing_state, dataframe_schema)
    return dataframe_util.convert_pandas_df_to_data_format(data_df, data_format)


class button(Element):
    def render(self):
        return st.button(_label(self), key=KEY("st_button"), **self.props.exclude('key', 'children', 'label', 'ref'))

class download_button(Element):
    def render(self):
        return st.download_button(_label(self), key=KEY("st_download_button"), **self.props.exclude('key', 'children', 'label', 'ref'))

class link_button(Element):
    def render(self):
        return st.link_button(_label(self), key=KEY("st_link_button"), **self.props.exclude('key', 'children', 'label', 'ref'))

class form_submit_button(Element):
    def render(self):
        callback = self.props.get('on_click')
        args = tuple(self.props.get('args', ()))
        kwargs = dict(self.props.get('kwargs', {}))

        def wrapped():
            if callback is None:
                return None
            return callback(*args, **kwargs)

        return st.form_submit_button(
            _label(self),
            key=KEY("st_form_submit_button"),
            on_click=wrapped if callback is not None else None,
            **self.props.exclude('key', 'children', 'label', 'ref', 'on_click', 'args', 'kwargs'),
        )

class checkbox(Element):
    def render(self):
        return st.checkbox(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class toggle(Element):
    def render(self):
        return st.toggle(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class radio(Element):
    def render(self):
        return st.radio(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class selectbox(Element):
    def render(self):
        return st.selectbox(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class multiselect(Element):
    def render(self):
        return st.multiselect(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class slider(Element):
    def render(self):
        return st.slider(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class select_slider(Element):
    def render(self):
        return st.select_slider(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class text_input(Element):
    def render(self):
        return st.text_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class number_input(Element):
    def render(self):
        return st.number_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class text_area(Element):
    def render(self):
        return st.text_area(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class date_input(Element):
    def render(self):
        return st.date_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class time_input(Element):
    def render(self):
        return st.time_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class color_picker(Element):
    def render(self):
        return st.color_picker(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class file_uploader(Element):
    def render(self):
        return st.file_uploader(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))

class camera_input(Element):
    def render(self):
        return st.camera_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))


class audio_input(Element):
    def render(self):
        return st.audio_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))


class menu_button(Element):
    def render(self):
        return st.menu_button(
            _label(self),
            key=KEY("widget"),
            on_click=_widget_callback(self, 'on_click'),
            **_widget_props(self, 'on_click'),
        )


class chat_input(Element):
    def render(self):
        placeholder = self.children[0] if self.children else self.props.get('placeholder', 'Your message')
        return st.chat_input(
            placeholder,
            key=KEY("widget"),
            on_submit=_widget_callback(self, 'on_submit'),
            **_widget_props(self, 'placeholder', 'on_submit'),
        )


class datetime_input(Element):
    def render(self):
        return st.datetime_input(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))


class pills(Element):
    def render(self):
        return st.pills(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))


class segmented_control(Element):
    def render(self):
        return st.segmented_control(_label(self), key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self))


class data_editor(Element):
    def render(self):
        data = _data(self)
        element_path = get_element_path()
        widget_key = KEY("widget")
        callback = self.props.get('on_change')
        args = tuple(self.props.get('args', ()))
        kwargs = dict(self.props.get('kwargs', {}))

        def wrapped_callback():
            set_element_value(element_path, _resolve_data_editor_value(data, st.session_state.get(widget_key)))
            if callback is None:
                return None
            with callback_context(element_path=element_path, widget_key=widget_key):
                return callback(*args, **kwargs)

        value = st.data_editor(
            data,
            key=widget_key,
            on_change=wrapped_callback if callback is not None else None,
            **_widget_props(self, 'data'),
        )
        set_element_value(element_path, value)
        return value


class feedback(Element):
    def render(self):
        options = self.children[0] if self.children else self.props.get('options', 'thumbs')
        return st.feedback(options, key=KEY("widget"), on_change=_widget_callback(self), **_widget_props(self, 'options'))
