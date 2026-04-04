"""
Tests for get_element_value(), Ref, and built-in element wrappers.
"""
import inspect

from st_components.core import Component, Element, Ref, render, Context, get_element_value
from st_components import elements
from st_components.elements import dialog, write_stream
from st_components.elements import input as input_elements
from st_components.elements.input import chat_input, data_editor, menu_button, text_input
from st_components.elements.charts import plotly_chart

from tests._mock import fake_ctx, _mock_st, _session_data


def test_get_element_value_from_path():
    _session_data["app.form.name.widget"] = "Alice"
    assert get_element_value("app.form.name") == "Alice"


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

    Context.stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.stack.clear()

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

    Context.stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.stack.clear()

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

    Context.stack[:] = [fake_ctx("app")]
    render(Counter(key="counter", ref=counter_ref))
    Context.stack.clear()

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
        Context.stack[:] = [fake_ctx("app")]
        render(TableForm(key="table"))
        Context.stack.clear()
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

    Context.stack[:] = [fake_ctx("app")]
    render(Composer(key="thread"))
    Context.stack.clear()

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

    Context.stack[:] = [fake_ctx("app")]
    render(Actions(key="toolbar"))
    Context.stack.clear()

    assert action_ref.path == "app.toolbar.actions"
    assert action_ref.value() == "Ship"
    assert seen == ["Ship"], f"callback saw: {seen}"


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

    Context.stack[:] = [fake_ctx("app")]
    render(Dashboard(key="dashboard"))
    Context.stack.clear()

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

    Context.stack[:] = [fake_ctx("app")]
    render(Modal(key="modal"))
    Context.stack.clear()

    assert dialog_calls == [("Confirm action", {"on_dismiss": "ignore"})], (
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

    Context.stack[:] = [fake_ctx("app")]
    render(StreamDemo(key="demo"))
    Context.stack.clear()

    assert stream_ref.path == "app.demo.writer"
    assert stream_ref.value() == "Hello world"
