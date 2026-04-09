"""
Tests for get_state(), widget_output(), Ref, reset_element(), and built-in element wrappers.
"""
import inspect
import importlib
from typing import Iterable, Literal

from st_components.core import callback, Component, Element, Ref, render, Context, reset_element, widget_output, get_state
from st_components.elements.factory import widget_callback
from st_components.core.access import widget_key
from st_components.core.models import ElementFiber, ElementState
from st_components.core.store import fibers
from st_components import elements
from st_components.elements import chat_message, dialog, empty, progress as progress_element, write_stream
from st_components.elements.runtime import show_balloons, show_progress, show_snow, show_spinner, show_toast
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


def test_elements_module_all_matches_public_exports():
    public_names = {
        name for name, value in vars(elements).items()
        if not name.startswith("_") and not inspect.ismodule(value)
    }
    public_names.discard("input_feedback")
    assert set(elements.__all__) == public_names


def test_reset_element_rotates_runtime_key():
    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("form"), fake_ctx("name")]
    original_key = widget_key()
    reset_element()
    refreshed_key = widget_key()
    Context.key_stack.clear()

    assert original_key == "app.form.name.raw"
    assert refreshed_key != original_key


def test_reset_element_accepts_ref():
    ref = Ref()
    ref._resolve("app.form.name", "element")

    _session_data["app.form.name.raw"] = "Alice"
    reset_element(ref)
    refreshed_key = widget_key("app.form.name")

    assert refreshed_key != "app.form.name.raw"


def test_callback_receives_value():
    seen = []

    def fake_text_input(label, key=None, on_change=None, value=None, **kwargs):
        if on_change is not None:
            on_change()
        return _session_data.get(key, value)

    _mock_st.text_input.side_effect = fake_text_input

    class Form(Component):
        def on_name_change(self, value):
            seen.append(value)

        def render(self):
            return text_input(key="name", value="Alice", on_change=self.on_name_change)("Name")

    # Pre-set session_state as Streamlit would before the rerun
    _session_data["app.form.name.raw"] = "Alice"
    Context.key_stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.key_stack.clear()

    assert seen == ["Alice"], f"callback saw: {seen}"
    assert _session_data["app.form.name.raw"] == "Alice"



def test_element_ref_value():
    name_ref = Ref()

    def fake_text_input(label, key=None, value=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        return _session_data.get(key, value)

    _mock_st.text_input.side_effect = fake_text_input

    class Form(Component):
        def render(self):
            return text_input(key="name", ref=name_ref, value="Alice")("Name")

    # Pre-set as Streamlit would before the rerun
    _session_data["app.form.name.raw"] = "Alice"
    Context.key_stack[:] = [fake_ctx("app")]
    render(Form(key="form"))
    Context.key_stack.clear()

    assert name_ref.path == "app.form.name"
    assert name_ref.kind == "element"
    assert name_ref.state().output == "Alice"


def test_empty_ref_stores_placeholder_runtime():
    empty_ref = Ref()

    class placeholder_ctx:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    placeholder = placeholder_ctx()
    _mock_st.empty.side_effect = lambda: placeholder

    class EmptyDemo(Component):
        def render(self):
            return empty(key="slot", ref=empty_ref)

    Context.key_stack[:] = [fake_ctx("app")]
    render(EmptyDemo(key="demo"))
    Context.key_stack.clear()

    assert empty_ref.state().handle is placeholder


def test_spinner_runtime_helper_uses_placeholder_ref():
    slot_ref = Ref()
    slot_ref._resolve("app.demo.slot", "element")
    events = []

    class placeholder_ctx:
        def __enter__(self):
            events.append("placeholder_enter")
            return self

        def __exit__(self, *args):
            events.append("placeholder_exit")
            return False

    class spinner_ctx:
        def __enter__(self):
            events.append("spinner_enter")
            return self

        def __exit__(self, *args):
            events.append("spinner_exit")
            return False

    placeholder = placeholder_ctx()
    fiber = ElementFiber(path="app.demo.slot", widget_key="app.demo.slot.raw")
    with fiber.state._writable(): fiber.state.handle = placeholder
    fibers()["app.demo.slot"] = fiber
    _session_data["app.demo.slot.raw"] = placeholder
    _mock_st.spinner.side_effect = lambda text, **kwargs: events.append(("spinner", text, kwargs)) or spinner_ctx()

    with show_spinner(ref=slot_ref, text="Syncing...", show_time=True):
        events.append("body")

    assert events == [
        "placeholder_enter",
        ("spinner", "Syncing...", {"show_time": True}),
        "spinner_enter",
        "body",
        "spinner_exit",
        "placeholder_exit",
    ]


def test_spinner_runtime_helper_rejects_non_context_ref():
    slot_ref = Ref()
    slot_ref._resolve("app.demo.slot", "element")
    non_ctx = object()
    fiber = ElementFiber(path="app.demo.slot", widget_key="app.demo.slot.raw")
    with fiber.state._writable(): fiber.state.handle = non_ctx
    fibers()["app.demo.slot"] = fiber
    _session_data["app.demo.slot.raw"] = non_ctx

    try:
        with show_spinner(ref=slot_ref):
            pass
    except RuntimeError as err:
        assert "placeholder" in str(err).lower()
    else:
        raise AssertionError("Expected show_spinner(ref=...) to reject non-context runtime handles")


def test_progress_runtime_helper_updates_and_clears_placeholder_ref():
    slot_ref = Ref()
    slot_ref._resolve("app.demo.slot", "element")
    events = []

    class placeholder_ctx:
        def __enter__(self):
            events.append("placeholder_enter")
            return self

        def __exit__(self, *args):
            events.append("placeholder_exit")
            return False

        def empty(self):
            events.append("placeholder_empty")

    placeholder = placeholder_ctx()
    fiber = ElementFiber(path="app.demo.slot", widget_key="app.demo.slot.raw")
    with fiber.state._writable(): fiber.state.handle = placeholder
    fibers()["app.demo.slot"] = fiber
    _session_data["app.demo.slot.raw"] = placeholder
    _mock_st.progress.side_effect = lambda value, **kwargs: events.append(("progress", value, kwargs)) or object()
    bar = show_progress(ref=slot_ref, value=10, text="Starting", width="stretch")
    returned = bar.update(50, text="Halfway")
    cleared = bar.clear()

    assert returned is bar
    assert cleared is None
    assert events == [
        "placeholder_enter",
        ("progress", 10, {"text": "Starting", "width": "stretch"}),
        "placeholder_exit",
        "placeholder_enter",
        ("progress", 50, {"text": "Halfway", "width": "stretch"}),
        "placeholder_exit",
        "placeholder_empty",
    ]


def test_progress_element_ref_stores_runtime_handle():
    progress_ref = Ref()
    handle = object()
    _mock_st.progress.side_effect = lambda value, **kwargs: handle

    class ProgressDemo(Component):
        def render(self):
            return progress_element(key="bar", ref=progress_ref, value=10, text="Starting", width="stretch")

    Context.key_stack[:] = [fake_ctx("app")]
    render(ProgressDemo(key="demo"))
    Context.key_stack.clear()

    assert progress_ref.state().handle is handle


def test_progress_runtime_helper_rejects_non_context_ref():
    slot_ref = Ref()
    slot_ref._resolve("app.demo.slot", "element")
    non_ctx = object()
    fiber = ElementFiber(path="app.demo.slot", widget_key="app.demo.slot.raw")
    with fiber.state._writable(): fiber.state.handle = non_ctx
    fibers()["app.demo.slot"] = fiber
    _session_data["app.demo.slot.raw"] = non_ctx

    try:
        show_progress(ref=slot_ref, value=0)
    except RuntimeError as err:
        assert "placeholder" in str(err).lower()
    else:
        raise AssertionError("Expected show_progress(ref=...) to reject invalid runtime handles")


def test_ephemeral_runtime_helpers_delegate_to_streamlit():
    toast_calls = []
    balloon_calls = []
    snow_calls = []

    _mock_st.toast.side_effect = lambda body, **kwargs: toast_calls.append((body, kwargs))
    _mock_st.balloons.side_effect = lambda: balloon_calls.append("balloons")
    _mock_st.snow.side_effect = lambda: snow_calls.append("snow")

    show_toast("Saved draft", icon=":material/check:", duration="long")
    show_balloons()
    show_snow()

    assert toast_calls == [("Saved draft", {"icon": ":material/check:", "duration": "long"})]
    assert balloon_calls == ["balloons"]
    assert snow_calls == ["snow"]


def test_container_ref_stores_delta_generator():
    container_ref = Ref()
    seen = []

    class box_ctx:
        def __enter__(self):
            seen.append("enter")
            return self

        def __exit__(self, *args):
            seen.append("exit")
            return False

    container_obj = box_ctx()
    _mock_st.container.side_effect = lambda **kwargs: container_obj

    class ContainerDemo(Component):
        def render(self):
            return container(key="box", ref=container_ref)(
                "inside",
            )

    Context.key_stack[:] = [fake_ctx("app")]
    render(ContainerDemo(key="demo"))
    Context.key_stack.clear()

    assert container_ref.state().handle is container_obj
    assert seen == ["enter", "exit"]


def test_columns_and_tabs_refs_store_runtime_handles():
    columns_ref = Ref()
    tabs_ref = Ref()

    class slot_ctx:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    column_slots = [slot_ctx(), slot_ctx()]
    tab_slots = [slot_ctx(), slot_ctx()]
    _mock_st.columns.side_effect = lambda *args, **kwargs: column_slots
    _mock_st.tabs.side_effect = lambda *args, **kwargs: tab_slots

    class LayoutDemo(Component):
        def render(self):
            return container(key="root")(
                columns(key="cols", ref=columns_ref, spec=2)("left", "right"),
                tabs(key="tabs", ref=tabs_ref, tabs=["A", "B"])("a", "b"),
            )

    Context.key_stack[:] = [fake_ctx("app")]
    render(LayoutDemo(key="demo"))
    Context.key_stack.clear()

    assert columns_ref.state().handle == column_slots
    assert tabs_ref.state().handle == tab_slots


def test_chat_message_ref_stores_delta_generator():
    message_ref = Ref()

    class message_ctx:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    message_obj = message_ctx()
    _mock_st.chat_message.side_effect = lambda *args, **kwargs: message_obj

    class ChatDemo(Component):
        def render(self):
            return chat_message(key="msg", ref=message_ref, name="assistant")("hello")

    Context.key_stack[:] = [fake_ctx("app")]
    render(ChatDemo(key="demo"))
    Context.key_stack.clear()

    assert message_ref.state().handle is message_obj


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


def test_get_state_accepts_path_and_ref():
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

    assert get_state("app.counter").count == 3
    assert get_state(counter_ref).count == 3


def test_unresolved_ref_error():
    ref = Ref()
    try:
        ref.state().output
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
    progress_params = inspect.signature(feedback_elements_module.progress).parameters
    toast_params = inspect.signature(feedback_elements_module.toast).parameters
    spinner_params = inspect.signature(feedback_elements_module.spinner).parameters

    assert toast_params["duration"].annotation == Literal["short", "long", "infinite"] | int
    assert progress_params["width"].annotation == feedback_elements_module.WidthWithoutContent
    assert spinner_params["width"].annotation == feedback_elements_module.WidthWithoutContent


def test_spinner_element_wraps_child_render():
    events = []

    class spinner_ctx:
        def __enter__(self):
            events.append("spinner_enter")
            return self

        def __exit__(self, *args):
            events.append("spinner_exit")
            return False

    _mock_st.spinner.side_effect = lambda text, **kwargs: events.append(("spinner", text, kwargs)) or spinner_ctx()
    _mock_st.write.side_effect = lambda value: events.append(("write", value))

    from st_components.elements.feedback import spinner as spinner_element

    Context.key_stack[:] = [fake_ctx("app")]
    render(spinner_element(key="loading", text="Loading...", show_time=True)("child output"))
    Context.key_stack.clear()

    assert events == [
        ("spinner", "Loading...", {"show_time": True, "width": "content"}),
        "spinner_enter",
        ("write", "child output"),
        "spinner_exit",
    ]


def test_data_editor_wrapper():
    import sys
    import importlib
    importlib.import_module("st_components.elements.input.data_editor")
    data_editor_module = sys.modules["st_components.elements.input.data_editor"]

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
        if on_change is not None:
            on_change()
        return edited_rows

    _mock_st.data_editor.side_effect = fake_data_editor
    original_resolver = data_editor_module.data_editor._resolve_output
    data_editor_module.data_editor._resolve_output = staticmethod(lambda data, state: edited_rows)

    class TableForm(Component):
        def on_edit(self, value):
            seen.append(value)

        def render(self):
            return data_editor(
                key="editor",
                ref=editor_ref,
                data=[{"task": "Draft", "done": False}],
                on_change=self.on_edit,
            )

    try:
        # Pre-set session_state as Streamlit would before the rerun
        _session_data["app.table.editor.raw"] = editing_state
        Context.key_stack[:] = [fake_ctx("app")]
        render(TableForm(key="table"))
        Context.key_stack.clear()

        # Assertions inside try: state.output is a computed that reads session_state
        # and applies postprocess — both must still be active at assertion time.
        assert editor_ref.path == "app.table.editor"
        assert editor_ref.state().output == edited_rows
        assert seen == [edited_rows], f"callback saw: {seen}"
    finally:
        data_editor_module.data_editor._resolve_output = original_resolver
        del _session_data["app.table.editor.raw"]


def test_chat_input_wrapper():
    composer_ref = Ref()
    seen = []

    def fake_chat_input(placeholder, key=None, on_submit=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        if on_submit is not None:
            on_submit()
        return "Ship it"

    _mock_st.chat_input.side_effect = fake_chat_input

    class Composer(Component):
        def on_submit(self, value):
            seen.append(value)

        def render(self):
            return chat_input(key="composer", ref=composer_ref, on_submit=self.on_submit)("Type a message")

    # Pre-set session_state as Streamlit would before the rerun
    _session_data["app.thread.composer.raw"] = "Ship it"
    Context.key_stack[:] = [fake_ctx("app")]
    render(Composer(key="thread"))
    Context.key_stack.clear()

    assert composer_ref.path == "app.thread.composer"
    assert composer_ref.state().output == "Ship it"
    assert seen == ["Ship it"], f"callback saw: {seen}"


def test_menu_button_wrapper():
    action_ref = Ref()
    seen = []

    def fake_menu_button(label, options, key=None, on_click=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        if on_click is not None:
            on_click()
        return "Ship"

    _mock_st.menu_button.side_effect = fake_menu_button

    class Actions(Component):
        def on_click(self, value):
            seen.append(value)

        def render(self):
            return menu_button(
                key="actions",
                ref=action_ref,
                options=["Draft", "Review", "Ship"],
                on_click=self.on_click,
            )("Actions")

    # Pre-set session_state as Streamlit would before the rerun
    _session_data["app.toolbar.actions.raw"] = "Ship"
    Context.key_stack[:] = [fake_ctx("app")]
    render(Actions(key="toolbar"))
    Context.key_stack.clear()

    assert action_ref.path == "app.toolbar.actions"
    assert action_ref.state().output == "Ship"
    assert seen == ["Ship"], f"callback saw: {seen}"


def test_button_wrapper_on_click():
    seen = []

    def fake_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    _mock_st.button.side_effect = fake_button

    class Actions(Component):
        def on_click(self, value):
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

    def on_save(value):
        seen.append(Context.callback.widget_key)

    def on_submit(value):
        seen.append(Context.callback.widget_key)

    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("actions")]
    render(button(key="save", on_click=on_save)("Save"))
    render(form_submit_button(key="submit", on_click=on_submit)("Submit"))
    Context.key_stack.clear()

    assert seen == [
        "app.actions.save.raw",
        "app.actions.submit.raw",
    ]


def test_form_submit_button_wrapper_on_click():
    seen = []

    def fake_form_submit_button(label, key=None, on_click=None, **kwargs):
        if on_click is not None:
            on_click()
        return True

    _mock_st.form_submit_button.side_effect = fake_form_submit_button

    class Actions(Component):
        def on_click(self, value):
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
    inner = {"points": [{"x": 2, "y": 8}]}
    selection = {"selection": inner}

    def fake_plotly_chart(figure_or_data, key=None, on_select=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        if callable(on_select):
            on_select()
        return selection

    _mock_st.plotly_chart.side_effect = fake_plotly_chart

    class Dashboard(Component):
        def on_select(self, value):
            seen.append(value)

        def render(self):
            return plotly_chart(
                key="chart",
                ref=chart_ref,
                figure_or_data={"data": []},
                on_select=self.on_select,
            )

    # Pre-set session_state as Streamlit would before the rerun
    _session_data["app.dashboard.chart.raw"] = selection
    Context.key_stack[:] = [fake_ctx("app")]
    render(Dashboard(key="dashboard"))
    Context.key_stack.clear()

    assert chart_ref.path == "app.dashboard.chart"
    assert chart_ref.state().output == selection
    assert seen == [selection], f"callback saw: {seen}"


def test_dataframe_wrapper_on_select():
    table_ref = Ref()
    seen = []
    inner = {"rows": [1]}
    selection = {"selection": inner}

    def fake_dataframe(data, key=None, on_select=None, **kwargs):
        assert "ref" not in kwargs, f"ref leaked to streamlit kwargs: {kwargs}"
        if callable(on_select):
            on_select()
        return selection

    _mock_st.dataframe.side_effect = fake_dataframe

    class Table(Component):
        def on_select(self, value):
            seen.append(value)

        def render(self):
            return dataframe(
                key="table",
                ref=table_ref,
                data=[{"a": 1}, {"a": 2}],
                on_select=self.on_select,
            )

    # Pre-set session_state as Streamlit would before the rerun
    _session_data["app.dashboard.table.raw"] = selection
    Context.key_stack[:] = [fake_ctx("app")]
    render(Table(key="dashboard"))
    Context.key_stack.clear()

    assert table_ref.path == "app.dashboard.table"
    assert table_ref.state().output == selection
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
    assert text_input_keys == ["app.modal.confirm.name.raw"], (
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
    assert stream_ref.state().output == "Hello world"


def test_none_children_filtered_by_props_validator():
    from st_components.core import Component

    class DummyComp(Component):
        def render(self):
            pass

    comp = DummyComp(key="f")
    comp(None, "a", None, "b", None)
    assert comp.props.children == ["a", "b"]
    assert comp.children == ["a", "b"]


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


# ---------------------------------------------------------------------------
# widget_output()
# ---------------------------------------------------------------------------

def test_widget_output_returns_session_state_value():
    _session_data["app.form.name.raw"] = "Alice"
    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("form"), fake_ctx("name")]
    from modict import MISSING
    result = widget_output()
    Context.key_stack.clear()
    assert result == "Alice"


def test_widget_output_returns_missing_when_key_absent():
    from modict import MISSING
    Context.key_stack[:] = [fake_ctx("app"), fake_ctx("form"), fake_ctx("nothere")]
    result = widget_output()
    Context.key_stack.clear()
    assert result is MISSING


def test_widget_output_accepts_explicit_path():
    from modict import MISSING
    _session_data["some.element.raw"] = 42
    result = widget_output("some.element")
    assert result == 42


def test_widget_output_accepts_element_ref():
    from modict import MISSING
    ref = Ref()
    ref._resolve("app.widget", "element")
    _session_data["app.widget.raw"] = "hello"
    result = widget_output(ref)
    assert result == "hello"


def test_widget_output_in_callback_context_falls_back_to_widget_key():
    from modict import MISSING
    from st_components.core.context import callback_context
    _session_data["app.btn.raw"] = True
    with callback_context(element_path="app.btn", widget_key="app.btn.raw"):
        result = widget_output()
    assert result is True


# ---------------------------------------------------------------------------
# ElementState frozen protection
# ---------------------------------------------------------------------------

def test_element_state_frozen_outside_writable():
    state = ElementState()
    try:
        state.output = "forbidden"
    except Exception as err:
        assert "frozen" in str(err).lower() or "immutable" in str(err).lower() or isinstance(err, (TypeError, AttributeError))
    else:
        raise AssertionError("Expected write to frozen ElementState to raise")


def test_element_state_writable_context_allows_write():
    state = ElementState()
    with state._writable():
        state.output = "allowed"
    assert state.output == "allowed"


def test_element_state_frozen_restored_after_writable():
    state = ElementState()
    with state._writable():
        state.output = "x"
    try:
        state.output = "y"
    except Exception:
        pass
    else:
        raise AssertionError("ElementState should be frozen again after _writable() exits")


def test_element_state_writable_is_reentrant():
    state = ElementState()
    with state._writable():
        with state._writable():
            state.output = "inner"
        # outer context still open — must not have re-frozen
        state.output = "outer"
    assert state.output == "outer"


# ---------------------------------------------------------------------------
# Ref.reset() edge cases
# ---------------------------------------------------------------------------

def test_ref_reset_raises_on_unresolved():
    ref = Ref()
    try:
        ref.reset()
    except RuntimeError as err:
        assert "unresolved" in str(err).lower()
    else:
        raise AssertionError("Expected unresolved ref reset to raise")


def test_ref_reset_raises_on_component_ref():
    ref = Ref()
    ref._resolve("app.mycomp", "component")
    try:
        ref.reset()
    except RuntimeError as err:
        assert "element" in str(err).lower()
    else:
        raise AssertionError("Expected component ref reset to raise")


# ---------------------------------------------------------------------------
# reset_element() edge cases
# ---------------------------------------------------------------------------

def test_reset_element_raises_on_component_ref():
    ref = Ref()
    ref._resolve("app.mycomp", "component")
    try:
        reset_element(ref)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected reset_element() on component ref to raise")
