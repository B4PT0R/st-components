"""
Tests for get_element_value(), Ref, and built-in element wrappers.
"""
import inspect
import importlib
from typing import Iterable, Literal

from st_components.core import Component, Element, Ref, render, Context, get_element_value, refresh_element
from st_components.core.access import _get_widget_key
from st_components import elements
from st_components.elements import dialog, write_stream
from st_components.elements import input as input_elements
from st_components.elements import layout as layout_elements
from st_components.elements import display as display_elements
from st_components.elements import charts as chart_elements
from st_components.elements.input import button, chat_input, data_editor, form_submit_button, menu_button, selectbox, text_input
from st_components.elements.charts import plotly_chart
from st_components.elements.layout import columns, container, tabs
from st_components.elements.display import dataframe, metric

text_elements_module = importlib.import_module("st_components.elements.text")
media_elements_module = importlib.import_module("st_components.elements.media")
feedback_elements_module = importlib.import_module("st_components.elements.feedback")

from tests._mock import fake_ctx, _mock_st, _session_data


def test_get_element_value_from_path():
    _session_data["app.form.name.widget"] = "Alice"
    assert get_element_value("app.form.name") == "Alice"


def test_refresh_element_rotates_runtime_key():
    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("form"), fake_ctx("name")]
    original_key = _get_widget_key()
    refresh_element()
    refreshed_key = _get_widget_key()
    Context.key_stack.clear()

    assert original_key == "app.form.name.widget"
    assert refreshed_key != original_key

    _session_data[refreshed_key] = "Bob"
    assert get_element_value("app.form.name") == "Bob"


def test_get_element_value_in_callback():
    seen = []

    def fake_text_input(label, key=None, on_change=None, value=None, **kwargs):
        _session_data[key] = value
        if on_change is not None:
            on_change()
        return value

    _mock_st.text_input.side_effect = fake_text_input

    class Form(Component):
        def on_name_change(self):
            seen.append(get_element_value())

        def render(self):
            return text_input(key="name", value="Alice", on_change=self.on_name_change)("Name")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.key_stack.clear()

    assert seen == ["Alice"], f"callback saw: {seen}"
    assert _session_data["app.form.name.widget"] == "Alice"


def test_element_ref_value():
    name_ref = Ref()

    def fake_text_input(label, key=None, value=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        _session_data[key] = value
        return value

    _mock_st.text_input.side_effect = fake_text_input

    class Form(Component):
        def render(self):
            return text_input(key="name", ref=name_ref, value="Alice")("Name")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.key_stack.clear()

    assert name_ref.path == "app.form.name"
    assert name_ref.kind == "element"
    assert name_ref.value() == "Alice"


def test_component_ref_state():
    counter_ref = Ref()

    class Counter(Component):
        def __init__(self, **props):
            super().__init__(**props)
            self.state = dict(count=3)

        def render(self):
            pass

    Context.key_stack[:] = [fake_ctx("app")]
    render(Counter(key="counter", ref=counter_ref))
    Context.key_stack.clear()

    assert counter_ref.path == "app.counter"
    assert counter_ref.kind == "component"
    assert counter_ref.state().count == 3
    assert counter_ref.get("count") == 3


def test_unresolved_ref_error():
    ref = Ref()
    try:
        ref.value()
    except RuntimeError as err:
        assert "unresolved" in str(err).lower()
    else:
        raise AssertionError("Expected unresolved ref access to raise")


def test_feedback_export_is_callable_wrapper():
    assert inspect.isclass(elements.feedback), (
        f"elements.feedback should be a wrapper class, got {elements.feedback!r}"
    )
    assert issubclass(elements.feedback, Element)


def test_input_wrappers_expose_explicit_signatures():
    widget = button(key="save", type="primary", width="stretch")
    chooser = selectbox(key="theme", options=["light", "dark"], index=1, accept_new_options=True)

    button_params = inspect.signature(button).parameters
    selectbox_params = inspect.signature(selectbox).parameters

    assert "type" in button_params
    assert button_params["type"].annotation == input_elements.ButtonType
    assert button_params["key"].kind is inspect.Parameter.KEYWORD_ONLY

    assert "accept_new_options" in selectbox_params
    assert selectbox_params["filter_mode"].annotation == input_elements.SelectWidgetFilterMode
    assert selectbox_params["key"].kind is inspect.Parameter.KEYWORD_ONLY

    assert widget.props.type == "primary"
    assert widget.props.width == "stretch"
    assert chooser.props.options == ["light", "dark"]
    assert chooser.props.accept_new_options is True


def test_layout_display_and_chart_wrappers_expose_explicit_signatures():
    container_params = inspect.signature(container).parameters
    columns_params = inspect.signature(columns).parameters
    tabs_params = inspect.signature(tabs).parameters
    metric_params = inspect.signature(metric).parameters
    dataframe_params = inspect.signature(dataframe).parameters
    plotly_params = inspect.signature(plotly_chart).parameters

    assert container_params["gap"].annotation == layout_elements.Gap
    assert container_params["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert columns_params["spec"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert tabs_params["width"].annotation == layout_elements.WidthWithoutContent
    assert metric_params["chart_type"].annotation == Literal["line", "bar", "area"]
    assert metric_params["delta_arrow"].annotation == display_elements.DeltaArrow
    assert dataframe_params["selection_mode"].annotation == display_elements.DataSelectionMode | Iterable[display_elements.DataSelectionMode]
    assert plotly_params["on_select"].annotation == chart_elements.SelectionBehavior
    assert plotly_params["selection_mode"].annotation == chart_elements.PlotlySelectionMode | Iterable[chart_elements.PlotlySelectionMode]


def test_text_and_media_wrappers_expose_explicit_signatures():
    markdown_params = inspect.signature(text_elements_module.markdown).parameters
    title_params = inspect.signature(text_elements_module.title).parameters
    badge_params = inspect.signature(text_elements_module.badge).parameters
    image_params = inspect.signature(media_elements_module.image).parameters
    audio_params = inspect.signature(media_elements_module.audio).parameters

    assert markdown_params["width"].annotation == text_elements_module.Width | Literal["auto"]
    assert title_params["anchor"].annotation == text_elements_module.Anchor
    assert badge_params["color"].annotation == text_elements_module.BadgeColor
    assert image_params["use_column_width"].annotation == media_elements_module.UseColumnWidth
    assert image_params["channels"].annotation == Literal["RGB", "BGR"]
    assert audio_params["width"].annotation == media_elements_module.WidthWithoutContent


def test_feedback_wrappers_expose_explicit_signatures():
    toast_params = inspect.signature(feedback_elements_module.toast).parameters
    progress_params = inspect.signature(feedback_elements_module.progress).parameters
    spinner_params = inspect.signature(feedback_elements_module.spinner).parameters

    assert toast_params["duration"].annotation == Literal["short", "long", "infinite"] | int
    assert progress_params["width"].annotation == feedback_elements_module.WidthWithoutContent
    assert spinner_params["show_time"].annotation == bool


def test_data_editor_wrapper():
    editor_ref = Ref()
    seen = []
    edited_rows = [{"task": "Ship it", "done": True}]
    editing_state = {
        "edited_rows": {0: {"task": "Ship it", "done": True}},
        "added_rows": [],
        "deleted_rows": [],
    }

    def fake_data_editor(data, key=None, on_change=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        _session_data[key] = editing_state
        if on_change is not None:
            on_change()
        return edited_rows

    _mock_st.data_editor.side_effect = fake_data_editor
    original_resolver = input_elements._resolve_data_editor_value
    input_elements._resolve_data_editor_value = lambda data, state: edited_rows

    class TableForm(Component):
        def on_edit(self):
            seen.append(get_element_value())

        def render(self):
            return data_editor(
                key="editor",
                ref=editor_ref,
                data=[{"task": "Draft", "done": False}],
                on_change=self.on_edit,
            )

    try:
        Context.key_stack[:] = [fake_ctx("app")]
        render(TableForm(key="table"))
        Context.key_stack.clear()
    finally:
        input_elements._resolve_data_editor_value = original_resolver

    assert editor_ref.path == "app.table.editor"
    assert editor_ref.value() == edited_rows
    assert seen == [edited_rows], f"callback saw: {seen}"


def test_chat_input_wrapper():
    composer_ref = Ref()
    seen = []

    def fake_chat_input(placeholder, key=None, on_submit=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        _session_data[key] = "Ship it"
        if on_submit is not None:
            on_submit()
        return "Ship it"

    _mock_st.chat_input.side_effect = fake_chat_input

    class Composer(Component):
        def on_submit(self):
            seen.append(get_element_value())

        def render(self):
            return chat_input(key="composer", ref=composer_ref, on_submit=self.on_submit)("Type a message")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Composer(key="thread"))
    Context.key_stack.clear()

    assert composer_ref.path == "app.thread.composer"
    assert composer_ref.value() == "Ship it"
    assert seen == ["Ship it"], f"callback saw: {seen}"


def test_menu_button_wrapper():
    action_ref = Ref()
    seen = []

    def fake_menu_button(label, options, key=None, on_click=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        _session_data[key] = "Ship"
        if on_click is not None:
            on_click()
        return "Ship"

    _mock_st.menu_button.side_effect = fake_menu_button

    class Actions(Component):
        def on_click(self):
            seen.append(get_element_value())

        def render(self):
            return menu_button(
                key="actions",
                ref=action_ref,
                options=["Draft", "Review", "Ship"],
                on_click=self.on_click,
            )("Actions")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Actions(key="toolbar"))
    Context.key_stack.clear()

    assert action_ref.path == "app.toolbar.actions"
    assert action_ref.value() == "Ship"
    assert seen == ["Ship"], f"callback saw: {seen}"


def test_button_wrapper_on_click():
    seen = []

    def fake_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    _mock_st.button.side_effect = fake_button

    class Actions(Component):
        def on_click(self):
            seen.append("clicked")

        def render(self):
            return button(key="save", on_click=self.on_click, type="primary")("Save")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Actions(key="toolbar"))
    Context.key_stack.clear()

    assert seen == ["clicked"]


def test_button_and_submit_button_use_standard_widget_key():
    seen = []

    def fake_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    def fake_form_submit_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    _mock_st.button.side_effect = fake_button
    _mock_st.form_submit_button.side_effect = fake_form_submit_button

    def on_save():
        seen.append(Context.callback.widget_key)

    def on_submit():
        seen.append(Context.callback.widget_key)

    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("actions")]
    render(button(key="save", on_click=on_save)("Save"))
    render(form_submit_button(key="submit", on_click=on_submit)("Submit"))
    Context.key_stack.clear()

    assert seen == [
        "app.actions.save.widget",
        "app.actions.submit.widget",
    ]


def test_form_submit_button_wrapper_on_click():
    seen = []

    def fake_form_submit_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    _mock_st.form_submit_button.side_effect = fake_form_submit_button

    class Actions(Component):
        def on_click(self):
            seen.append("submitted")

        def render(self):
            return form_submit_button(key="submit", on_click=self.on_click, type="primary")("Submit")

    Context.key_stack[:] = [fake_ctx("app")]
    render(Actions(key="toolbar"))
    Context.key_stack.clear()

    assert seen == ["submitted"]




def test_plotly_chart_wrapper():
    chart_ref = Ref()
    seen = []
    selection = {"selection": {"points": [{"x": 2, "y": 8}]}}

    def fake_plotly_chart(figure_or_data, key=None, on_select=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        if callable(on_select):
            on_select(selection)
        return selection

    _mock_st.plotly_chart.side_effect = fake_plotly_chart

    class Dashboard(Component):
        def on_select(self):
            seen.append(get_element_value())

        def render(self):
            return plotly_chart(
                key="chart",
                ref=chart_ref,
                figure_or_data={"data": []},
                on_select=self.on_select,
            )

    Context.key_stack[:] = [fake_ctx("app")]
    render(Dashboard(key="dashboard"))
    Context.key_stack.clear()

    assert chart_ref.path == "app.dashboard.chart"
    assert chart_ref.value() == selection
    assert seen == [selection], f"callback saw: {seen}"


def test_dialog_wrapper():
    dialog_calls = []
    text_input_keys = []

    def fake_dialog(title, **kwargs):
        def decorator(inner):
            def wrapped(*args, **inner_kwargs):
                dialog_calls.append((title, kwargs))
                return inner(*args, **inner_kwargs)
            return wrapped
        return decorator

    def fake_text_input(label, key=None, value=None, **kwargs):
        text_input_keys.append(key)
        _session_data[key] = value
        return value

    _mock_st.dialog.side_effect = fake_dialog
    _mock_st.text_input.side_effect = fake_text_input

    class Modal(Component):
        def render(self):
            return dialog(key="confirm", title="Confirm action")(
                text_input(key="name", value="Alice")("Name")
            )

    Context.key_stack[:] = [fake_ctx("app")]
    render(Modal(key="modal"))
    Context.key_stack.clear()

    assert dialog_calls == [("Confirm action", {"width": "small", "dismissible": True, "icon": None, "on_dismiss": "ignore"})], (
        f"got dialog calls: {dialog_calls}"
    )
    assert text_input_keys == ["app.modal.confirm.name.widget"], (
        f"got text input keys: {text_input_keys}"
    )


def test_write_stream_wrapper():
    stream_ref = Ref()

    def fake_write_stream(stream, **kwargs):
        return "".join(list(stream))

    _mock_st.write_stream.side_effect = fake_write_stream

    class StreamDemo(Component):
        def render(self):
            return write_stream(key="writer", ref=stream_ref, stream=iter(["Hello", " ", "world"]))

    Context.key_stack[:] = [fake_ctx("app")]
    render(StreamDemo(key="demo"))
    Context.key_stack.clear()

    assert stream_ref.path == "app.demo.writer"
    assert stream_ref.value() == "Hello world"


def test_none_children_filtered_by_props_validator():
    from st_components.core.base import Fragment

    frag = Fragment(key="f")
    frag(None, "a", None, "b", None)
    assert frag.props.children == ["a", "b"]
    assert frag.children == ["a", "b"]


def test_none_children_skipped_at_render():
    rendered = []

    def fake_container(key=None, **kwargs):
        class ctx:
            def __enter__(self): return self
            def __exit__(self, *a): pass
        return ctx()

    def fake_write(obj, **kwargs):
        rendered.append(obj)

    _mock_st.container.side_effect = fake_container
    _mock_st.write.side_effect = fake_write

    from st_components.core import render
    from st_components.elements.layout import container

    box = container(key="box")("a", None, "b")
    box.render()

    assert None not in rendered
    assert "a" in rendered
    assert "b" in rendered
