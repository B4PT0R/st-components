import datetime
import importlib.util
import time as pytime
from pathlib import Path

from st_components import App, Component, Ref, get_element_value
from st_components.elements import (
    altair_chart,
    area_chart,
    audio_input,
    badge,
    bar_chart,
    bokeh_chart,
    button,
    camera_input,
    caption,
    checkbox,
    chat_input,
    chat_message,
    code,
    color_picker,
    container,
    data_editor,
    date_input,
    datetime_input,
    divider,
    dialog,
    exception as exception_display,
    feedback,
    file_uploader,
    form,
    form_submit_button,
    graphviz_chart,
    help as help_display,
    html,
    iframe,
    json,
    line_chart,
    logo,
    markdown,
    map as map_chart,
    menu_button,
    multiselect,
    number_input,
    page_link,
    pdf,
    pills,
    plotly_chart,
    pydeck_chart,
    pyplot,
    radio,
    segmented_control,
    select_slider,
    selectbox,
    slider,
    space,
    scatter_chart,
    status,
    subheader,
    text_area,
    text_input,
    time_input,
    title,
    toggle,
    vega_lite_chart,
    write_stream,
)

from examples._source import source_view


ASSETS_DIR = Path(__file__).parent / "assets"
IFRAME_DEMO_SRC = ASSETS_DIR / "iframe-demo.html"
LOGO_DEMO_SRC = ASSETS_DIR / "demo-logo.svg"
PDF_DEMO_AVAILABLE = importlib.util.find_spec("streamlit_pdf") is not None
PDF_DEMO_DATA = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R>>endobj\n"
    b"4 0 obj<</Length 44>>stream\n"
    b"BT /F1 18 Tf 36 120 Td (st-components PDF demo) Tj ET\n"
    b"endstream\n"
    b"endobj\n"
    b"xref\n"
    b"0 5\n"
    b"0000000000 65535 f \n"
    b"0000000010 00000 n \n"
    b"0000000053 00000 n \n"
    b"0000000110 00000 n \n"
    b"0000000198 00000 n \n"
    b"trailer<</Root 1 0 R/Size 5>>\n"
    b"startxref\n"
    b"293\n"
    b"%%EOF\n"
)
CHART_ROWS = [
    {"month": "Jan", "alpha": 12, "beta": 7},
    {"month": "Feb", "alpha": 18, "beta": 11},
    {"month": "Mar", "alpha": 9, "beta": 15},
    {"month": "Apr", "alpha": 22, "beta": 13},
]
SCATTER_ROWS = [
    {"x": 1, "y": 3, "size": 10, "segment": "A"},
    {"x": 2, "y": 8, "size": 18, "segment": "A"},
    {"x": 3, "y": 5, "size": 12, "segment": "B"},
    {"x": 4, "y": 11, "size": 20, "segment": "B"},
]
MAP_ROWS = [
    {"lat": 48.8566, "lon": 2.3522},
    {"lat": 51.5072, "lon": -0.1276},
    {"lat": 40.7128, "lon": -74.0060},
]
GRAPHVIZ_DOT = """
digraph Demo {
    rankdir=LR;
    Streamlit -> st_components;
    st_components -> primitives;
    primitives -> browser;
}
""".strip()


PRIMITIVES = [
    "button",
    "checkbox",
    "toggle",
    "radio",
    "selectbox",
    "multiselect",
    "slider",
    "select_slider",
    "text_input",
    "number_input",
    "text_area",
    "date_input",
    "datetime_input",
    "time_input",
    "color_picker",
    "file_uploader",
    "camera_input",
    "audio_input",
    "chat_input",
    "chat_message",
    "status",
    "badge",
    "space",
    "html",
    "iframe",
    "pdf",
    "exception",
    "help",
    "page_link",
    "logo",
    "area_chart",
    "bar_chart",
    "line_chart",
    "scatter_chart",
    "map",
    "graphviz_chart",
    "plotly_chart",
    "altair_chart",
    "vega_lite_chart",
    "pydeck_chart",
    "pyplot",
    "bokeh_chart",
    "fragment",
    "dialog",
    "write_stream",
    "form",
    "form_submit_button",
    "menu_button",
    "pills",
    "segmented_control",
    "feedback",
    "data_editor",
]


SNIPPETS = {
    "button": 'button(key="save", on_click=self.save, type="primary")("Save")',
    "checkbox": 'checkbox(key="enabled", value=True, on_change=self.sync_value)("Enable feature")',
    "toggle": 'toggle(key="dark_mode", value=False, on_change=self.sync_value)("Dark mode")',
    "radio": 'radio(key="channel", options=["Alpha", "Beta", "Gamma"], on_change=self.sync_value)("Channel")',
    "selectbox": 'selectbox(key="city", options=["Paris", "Berlin", "Tokyo"], on_change=self.sync_value)("City")',
    "multiselect": 'multiselect(key="langs", options=["Python", "Rust"], on_change=self.sync_value)("Languages")',
    "slider": 'slider(key="score", min_value=0, max_value=10, value=5, on_change=self.sync_value)("Score")',
    "select_slider": 'select_slider(key="size", options=["XS", "S", "M", "L"], on_change=self.sync_value)("Size")',
    "text_input": 'text_input(key="name", value="Baptiste", on_change=self.sync_value)("Name")',
    "number_input": 'number_input(key="count", value=42, on_change=self.sync_value)("Count")',
    "text_area": 'text_area(key="notes", value="Short note", on_change=self.sync_value)("Notes")',
    "date_input": 'date_input(key="start_date", value=date.today(), on_change=self.sync_value)("Date")',
    "datetime_input": 'datetime_input(key="schedule", value=datetime.now(), on_change=self.sync_value)("Schedule")',
    "time_input": 'time_input(key="start_time", value=time(9, 30), on_change=self.sync_value)("Time")',
    "color_picker": 'color_picker(key="accent", value="#ff4b4b", on_change=self.sync_value)("Accent color")',
    "file_uploader": 'file_uploader(key="upload", on_change=self.sync_value)("Upload a file")',
    "camera_input": 'camera_input(key="photo", on_change=self.sync_value)("Take a photo")',
    "audio_input": 'audio_input(key="clip", on_change=self.sync_value)("Record a short clip")',
    "chat_input": 'chat_input(key="composer", on_submit=self.submit)("Send a message")',
    "chat_message": 'chat_message(key="answer", name="assistant")(markdown(key="body")("A compact message bubble"))',
    "status": 'status(key="sync", label="Syncing dataset", state="running", expanded=True)(markdown(key="body")("3 files indexed"))',
    "badge": 'badge(key="beta", color="green", icon=":material/check_circle:")("Stable wrapper")',
    "space": 'space(key="gap", size="large")',
    "html": 'html(key="badge", body="<div style=\\"padding:12px;border-radius:12px;background:#111827;color:white\\">Inline HTML</div>")',
    "iframe": 'iframe(key="preview", src=Path("assets/iframe-demo.html"), height=220)',
    "pdf": 'pdf(key="proposal", data=pdf_bytes, height=240)',
    "exception": 'exception(key="failure", exception=RuntimeError("Wrapper smoke test"))',
    "help": 'help(key="docs", obj=datetime.datetime)',
    "page_link": 'page_link(key="docs", page="https://streamlit.io", label="Open Streamlit")',
    "logo": 'logo(key="brand", image=Path("assets/demo-logo.svg"), size="large")',
    "area_chart": 'area_chart(key="sales", data=rows, x="month", y=["alpha", "beta"])',
    "bar_chart": 'bar_chart(key="sales", data=rows, x="month", y=["alpha", "beta"])',
    "line_chart": 'line_chart(key="trend", data=rows, x="month", y=["alpha", "beta"])',
    "scatter_chart": 'scatter_chart(key="clusters", data=points, x="x", y="y", size="size", color="segment")',
    "map": 'map(key="cities", data=points, latitude="lat", longitude="lon", zoom=1)',
    "graphviz_chart": 'graphviz_chart(key="flow", figure_or_dot="digraph { A -> B }")',
    "plotly_chart": 'plotly_chart(key="sales", figure_or_data=fig, on_select=self.sync_value)',
    "altair_chart": 'altair_chart(key="sales", altair_chart=chart, on_select=self.sync_value, selection_mode="pick")',
    "vega_lite_chart": 'vega_lite_chart(key="sales", data=rows, spec=spec, on_select=self.sync_value, selection_mode="pick")',
    "pydeck_chart": 'pydeck_chart(key="cities", pydeck_obj=deck, on_select=self.sync_value)',
    "pyplot": 'pyplot(key="sales", fig=fig)',
    "bokeh_chart": 'bokeh_chart(key="trend", figure=figure)',
    "fragment": 'class Clock(Component, fragment=True, run_every=1): ...',
    "dialog": 'dialog(key="confirm", title="Confirm action", on_dismiss=self.close_dialog)(markdown(key="body")("Modal content"))',
    "write_stream": 'button(key="start", on_click=self.start_stream)("Start stream"); write_stream(key="writer", stream=self.stream(), cursor="▋")',
    "form": 'form(key="signup")(text_input(key="name", ref=name_ref)("Name"), form_submit_button(key="submit", on_click=self.submit)("Submit"))',
    "form_submit_button": 'form_submit_button(key="submit", on_click=self.submit, type="primary")("Save form")',
    "menu_button": 'menu_button(key="actions", options=["Draft", "Review", "Ship"], on_click=self.sync_value)("Actions")',
    "pills": 'pills(key="priority", options=["Low", "Medium", "High"], on_change=self.sync_value)("Priority")',
    "segmented_control": 'segmented_control(key="view", options=["List", "Board"], on_change=self.sync_value)("View")',
    "feedback": 'feedback(key="rating", options="stars", on_change=self.sync_value)',
    "data_editor": 'data_editor(key="tasks", data=rows, num_rows="dynamic", on_change=self.sync_value)',
}


def snippet(name):
    return code(key="snippet", language="python")(SNIPPETS[name])


def uploaded_file_info(value):
    if value is None:
        return None
    if isinstance(value, list):
        return [uploaded_file_info(item) for item in value]
    return {
        "name": getattr(value, "name", None),
        "type": getattr(value, "type", None),
        "size": getattr(value, "size", None),
    }


class ButtonDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(clicks=0)

    def click(self):
        self.state.clicks += 1

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("button"),
            button(key="widget", on_click=self.click, type="primary")("Click me"),
            json(key="value")({"clicks": self.state.clicks}),
            snippet("button"),
        )


class CheckboxDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=True)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("checkbox"),
            checkbox(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Enable feature"),
            json(key="value")({"value": self.state.value}),
            snippet("checkbox"),
        )


class ToggleDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=False)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("toggle"),
            toggle(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Dark mode"),
            json(key="value")({"value": self.state.value}),
            snippet("toggle"),
        )


class RadioDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="Alpha")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("radio"),
            radio(
                key="widget",
                options=["Alpha", "Beta", "Gamma"],
                index=["Alpha", "Beta", "Gamma"].index(self.state.value),
                on_change=self.sync_state("value"),
            )("Channel"),
            json(key="value")({"value": self.state.value}),
            snippet("radio"),
        )


class SelectboxDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="Paris")

    def render(self):
        options = ["Paris", "Berlin", "Tokyo"]
        return container(key="panel", border=True)(
            subheader(key="title")("selectbox"),
            selectbox(
                key="widget",
                options=options,
                index=options.index(self.state.value),
                on_change=self.sync_state("value"),
            )("City"),
            json(key="value")({"value": self.state.value}),
            snippet("selectbox"),
        )


class MultiselectDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=["Python"])

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("multiselect"),
            multiselect(
                key="widget",
                options=["Python", "Rust", "Go", "TypeScript"],
                default=self.state.value,
                on_change=self.sync_state("value"),
            )("Languages"),
            json(key="value")({"value": self.state.value}),
            snippet("multiselect"),
        )


class SliderDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=5)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("slider"),
            slider(key="widget", min_value=0, max_value=10, value=self.state.value, on_change=self.sync_state("value"))("Score"),
            json(key="value")({"value": self.state.value}),
            snippet("slider"),
        )


class SelectSliderDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="M")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("select_slider"),
            select_slider(
                key="widget",
                options=["XS", "S", "M", "L", "XL"],
                value=self.state.value,
                on_change=self.sync_state("value"),
            )("Size"),
            json(key="value")({"value": self.state.value}),
            snippet("select_slider"),
        )


class TextInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="Baptiste")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("text_input"),
            text_input(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Name"),
            json(key="value")({"value": self.state.value}),
            snippet("text_input"),
        )


class NumberInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=42)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("number_input"),
            number_input(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Count"),
            json(key="value")({"value": self.state.value}),
            snippet("number_input"),
        )


class TextAreaDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="Short multiline note.")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("text_area"),
            text_area(key="widget", value=self.state.value, height=120, on_change=self.sync_state("value"))("Notes"),
            json(key="value")({"value": self.state.value}),
            snippet("text_area"),
        )


class DateInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=datetime.date.today())

    def render(self):
        value = self.state.value.isoformat() if self.state.value is not None else None
        return container(key="panel", border=True)(
            subheader(key="title")("date_input"),
            date_input(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Date"),
            json(key="value")({"value": value}),
            snippet("date_input"),
        )


class DatetimeInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=datetime.datetime.now().replace(second=0, microsecond=0))

    def render(self):
        value = self.state.value.isoformat() if self.state.value is not None else None
        return container(key="panel", border=True)(
            subheader(key="title")("datetime_input"),
            datetime_input(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Schedule"),
            json(key="value")({"value": value}),
            snippet("datetime_input"),
        )


class TimeInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=datetime.time(hour=9, minute=30))

    def render(self):
        value = self.state.value.isoformat() if self.state.value is not None else None
        return container(key="panel", border=True)(
            subheader(key="title")("time_input"),
            time_input(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Time"),
            json(key="value")({"value": value}),
            snippet("time_input"),
        )


class ColorPickerDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="#ff4b4b")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("color_picker"),
            color_picker(key="widget", value=self.state.value, on_change=self.sync_state("value"))("Accent color"),
            json(key="value")({"value": self.state.value}),
            snippet("color_picker"),
        )


class FileUploaderDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=None)

    def sync_value(self, value):
        self.state.value = uploaded_file_info(value)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("file_uploader"),
            file_uploader(key="widget", on_change=self.sync_value)("Upload a file"),
            json(key="value")({"value": self.state.value}),
            snippet("file_uploader"),
        )


class CameraInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=None)

    def sync_value(self, value):
        self.state.value = uploaded_file_info(value)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("camera_input"),
            camera_input(key="widget", on_change=self.sync_value)("Take a photo"),
            json(key="value")({"value": self.state.value}),
            snippet("camera_input"),
        )


class AudioInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=None)

    def sync_value(self, value):
        self.state.value = uploaded_file_info(value)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("audio_input"),
            audio_input(key="widget", on_change=self.sync_value)("Record a short clip"),
            json(key="value")({"value": self.state.value}),
            snippet("audio_input"),
        )


class ChatInputDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(messages=["The callback receives the submitted message as `value`."])

    def submit(self, value):
        message = value
        if message:
            self.state.messages.append(message)

    def render(self):
        message_nodes = [
            chat_message(key="intro", name="assistant")(
                markdown(key="body")("Submit a message below to append it to this thread.")
            )
        ]
        message_nodes.extend(
            chat_message(key=f"message_{index}", name="user")(
                markdown(key="body")(message)
            )
            for index, message in enumerate(self.state.messages)
        )
        return container(key="panel", border=True)(
            subheader(key="title")("chat_input"),
            *message_nodes,
            chat_input(key="widget", on_submit=self.submit)("Send a message"),
            json(key="value")({"messages": self.state.messages}),
            snippet("chat_input"),
        )


class ChatMessageDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("chat_message"),
            chat_message(key="assistant", name="assistant")(
                markdown(key="body")("Use this wrapper to compose chat UIs from simple children.")
            ),
            chat_message(key="user", name="user")(
                markdown(key="body")("Messages stay regular Elements inside the container.")
            ),
            json(key="value")({"names": ["assistant", "user"]}),
            snippet("chat_message"),
        )


class StatusDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("status"),
            status(key="widget", label="Syncing dataset", state="running", expanded=True)(
                markdown(key="body")("3 files indexed, 1 pending."),
            ),
            json(key="value")({"label": "Syncing dataset", "state": "running"}),
            snippet("status"),
        )


class BadgeDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("badge"),
            badge(key="widget", color="green", icon=":material/check_circle:")("Stable wrapper"),
            json(key="value")({"label": "Stable wrapper", "color": "green"}),
            snippet("badge"),
        )


class SpaceDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("space"),
            markdown(key="before")("Block before the spacer."),
            space(key="widget", size="large"),
            markdown(key="after")("Block after the spacer."),
            json(key="value")({"size": "large"}),
            snippet("space"),
        )


class HtmlDemo(Component):
    def render(self):
        body = (
            '<div style="padding: 12px 16px; border-radius: 14px; '
            'background: linear-gradient(135deg, #0f172a, #1d4ed8); color: white;">'
            '<strong>html()</strong><br/>Inline markup passed directly to Streamlit.'
            '</div>'
        )
        return container(key="panel", border=True)(
            subheader(key="title")("html"),
            html(key="widget", body=body),
            json(key="value")({"body_preview": "Inline markup passed directly to Streamlit."}),
            snippet("html"),
        )


class IframeDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("iframe"),
            iframe(key="widget", src=IFRAME_DEMO_SRC, height=240),
            json(key="value")({"src": str(IFRAME_DEMO_SRC)}),
            snippet("iframe"),
        )


class PdfDemo(Component):
    def render(self):
        children = [
            subheader(key="title")("pdf"),
            json(key="value")({"available": PDF_DEMO_AVAILABLE}),
            snippet("pdf"),
        ]
        if PDF_DEMO_AVAILABLE:
            children.insert(1, pdf(key="widget", data=PDF_DEMO_DATA, height=240))
        else:
            children.insert(
                1,
                markdown(key="note")(
                    "`st.pdf` is wrapped, but this local environment does not have the optional `streamlit[pdf]` extra installed."
                ),
            )
        return container(key="panel", border=True)(*children)


class ExceptionDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("exception"),
            exception_display(key="widget", exception=RuntimeError("Wrapper smoke test")),
            json(key="value")({"exception": "RuntimeError('Wrapper smoke test')"}),
            snippet("exception"),
        )


class HelpDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("help"),
            help_display(key="widget", obj=datetime.datetime),
            json(key="value")({"object": "datetime.datetime"}),
            snippet("help"),
        )


class PageLinkDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("page_link"),
            page_link(
                key="widget",
                page="https://streamlit.io",
                label="Open Streamlit",
                icon=":material/open_in_new:",
            ),
            json(key="value")({"page": "https://streamlit.io"}),
            snippet("page_link"),
        )


class LogoDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("logo"),
            logo(key="widget", image=LOGO_DEMO_SRC, size="large"),
            markdown(key="note")("This primitive updates the app chrome logo, not the body of the page."),
            json(key="value")({"image": str(LOGO_DEMO_SRC), "size": "large"}),
            snippet("logo"),
        )


class AreaChartDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("area_chart"),
            area_chart(key="widget", data=CHART_ROWS, x="month", y=["alpha", "beta"], height=260),
            json(key="value")({"rows": len(CHART_ROWS), "series": ["alpha", "beta"]}),
            snippet("area_chart"),
        )


class BarChartDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("bar_chart"),
            bar_chart(key="widget", data=CHART_ROWS, x="month", y=["alpha", "beta"], height=260),
            json(key="value")({"rows": len(CHART_ROWS), "series": ["alpha", "beta"]}),
            snippet("bar_chart"),
        )


class LineChartDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("line_chart"),
            line_chart(key="widget", data=CHART_ROWS, x="month", y=["alpha", "beta"], height=260),
            json(key="value")({"rows": len(CHART_ROWS), "series": ["alpha", "beta"]}),
            snippet("line_chart"),
        )


class ScatterChartDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("scatter_chart"),
            scatter_chart(key="widget", data=SCATTER_ROWS, x="x", y="y", size="size", color="segment", height=260),
            json(key="value")({"rows": len(SCATTER_ROWS), "color": "segment"}),
            snippet("scatter_chart"),
        )


class MapDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("map"),
            map_chart(key="widget", data=MAP_ROWS, latitude="lat", longitude="lon", zoom=1, height=320),
            json(key="value")({"points": len(MAP_ROWS)}),
            snippet("map"),
        )


class GraphvizChartDemo(Component):
    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("graphviz_chart"),
            graphviz_chart(key="widget", figure_or_dot=GRAPHVIZ_DOT),
            json(key="value")({"nodes": 4}),
            snippet("graphviz_chart"),
        )


class PlotlyChartDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(selection=None)

    def render(self):
        import plotly.express as px

        fig = px.scatter(SCATTER_ROWS, x="x", y="y", size="size", color="segment")
        return container(key="panel", border=True)(
            subheader(key="title")("plotly_chart"),
            markdown(key="hint")("Box- or lasso-select points to trigger `on_select`."),
            plotly_chart(key="widget", figure_or_data=fig, on_select=self.sync_state("selection"), height=360),
            json(key="value")({"selection": self.state.selection}),
            snippet("plotly_chart"),
        )


class AltairChartDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(selection=None)

    def render(self):
        import altair as alt

        pick = alt.selection_interval(name="pick")
        chart = (
            alt.Chart(alt.Data(values=SCATTER_ROWS))
            .mark_circle(size=120)
            .encode(
                x="x:Q",
                y="y:Q",
                color="segment:N",
                tooltip=["x:Q", "y:Q", "segment:N"],
            )
            .add_params(pick)
        )
        return container(key="panel", border=True)(
            subheader(key="title")("altair_chart"),
            markdown(key="hint")("Drag a region on the chart to test `on_select`."),
            altair_chart(key="widget", altair_chart=chart, on_select=self.sync_state("selection"), selection_mode="pick", height=320),
            json(key="value")({"selection": self.state.selection}),
            snippet("altair_chart"),
        )


class VegaLiteChartDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(selection=None)

    def render(self):
        spec = {
            "mark": {"type": "point", "filled": True, "size": 140},
            "params": [{"name": "pick", "select": "interval"}],
            "encoding": {
                "x": {"field": "x", "type": "quantitative"},
                "y": {"field": "y", "type": "quantitative"},
                "color": {"field": "segment", "type": "nominal"},
                "tooltip": [
                    {"field": "x", "type": "quantitative"},
                    {"field": "y", "type": "quantitative"},
                    {"field": "segment", "type": "nominal"},
                ],
            },
        }
        return container(key="panel", border=True)(
            subheader(key="title")("vega_lite_chart"),
            markdown(key="hint")("Drag a region on the chart to test `on_select`."),
            vega_lite_chart(
                key="widget",
                data=SCATTER_ROWS,
                spec=spec,
                on_select=self.sync_state("selection"),
                selection_mode="pick",
                height=320,
            ),
            json(key="value")({"selection": self.state.selection}),
            snippet("vega_lite_chart"),
        )


class PydeckChartDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(selection=None)

    def render(self):
        import pydeck as pdk

        deck = pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=48.8566, longitude=2.3522, zoom=1),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=MAP_ROWS,
                    get_position="[lon, lat]",
                    get_fill_color="[34, 197, 94, 180]",
                    get_radius=180000,
                    pickable=True,
                )
            ],
        )
        return container(key="panel", border=True)(
            subheader(key="title")("pydeck_chart"),
            markdown(key="hint")("Click a point on the map to test `on_select`."),
            pydeck_chart(key="widget", pydeck_obj=deck, on_select=self.sync_state("selection"), height=360),
            json(key="value")({"selection": self.state.selection}),
            snippet("pydeck_chart"),
        )


class PyplotDemo(Component):
    def render(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot([row["month"] for row in CHART_ROWS], [row["alpha"] for row in CHART_ROWS], label="alpha")
        ax.plot([row["month"] for row in CHART_ROWS], [row["beta"] for row in CHART_ROWS], label="beta")
        ax.set_ylabel("value")
        ax.legend()
        return container(key="panel", border=True)(
            subheader(key="title")("pyplot"),
            pyplot(key="widget", fig=fig),
            json(key="value")({"series": ["alpha", "beta"]}),
            snippet("pyplot"),
        )


class BokehChartDemo(Component):
    def render(self):
        from bokeh.plotting import figure

        fig = figure(height=280, sizing_mode="stretch_width", title="Bokeh wrapper")
        fig.line([1, 2, 3, 4], [3, 7, 5, 9], line_width=3)
        fig.circle([1, 2, 3, 4], [3, 7, 5, 9], size=10)
        return container(key="panel", border=True)(
            subheader(key="title")("bokeh_chart"),
            bokeh_chart(key="widget", figure=fig),
            json(key="value")({"points": 4}),
            snippet("bokeh_chart"),
        )


class ClockFragment(Component, fragment=True, run_every=1):
    def render(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return container(key="frame", border=True)(
            markdown(key="title")(f"**Fragment clock:** `{now}`"),
            caption(key="body")("This subtree reruns every second through `st.fragment`."),
        )


class FragmentDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(clicks=0)

    def click(self):
        self.state.clicks += 1

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("fragment"),
            markdown(key="hint")(
                "The clock below is a fragment-based component with `run_every=1`. "
                "It should update once per second without needing any manual interaction."
            ),
            ClockFragment(key="clock"),
            button(key="clicks", on_click=self.click)("Regular parent button"),
            json(key="value")({"parent_clicks": self.state.clicks}),
            snippet("fragment"),
        )


class DialogDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(open=False, confirmed=0)

    def open_dialog(self):
        self.state.open = True

    def close_dialog(self):
        self.state.open = False

    def confirm(self):
        self.state.confirmed += 1
        self.state.open = False

    def render(self):
        children = [
            subheader(key="title")("dialog"),
            button(key="open", on_click=self.open_dialog, type="primary")("Open dialog"),
            json(key="value")({"open": self.state.open, "confirmed": self.state.confirmed}),
            snippet("dialog"),
        ]
        if self.state.open:
            children.insert(
                2,
                dialog(key="widget", title="Confirm action", on_dismiss=self.close_dialog)(
                    markdown(key="body")("This modal is rendered through the `dialog` Element wrapper."),
                    button(key="confirm", on_click=self.confirm, type="primary")("Confirm"),
                ),
            )
        return container(key="panel", border=True)(*children)


class WriteStreamDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(pending=False, runs=0)

    def start_stream(self):
        self.state.pending = True
        self.state.runs += 1

    def stream(self):
        for chunk in ("Streaming ", "from ", "st-components"):
            pytime.sleep(0.2)
            yield chunk

    def render(self):
        children = [
            subheader(key="title")("write_stream"),
            markdown(key="hint")(
                "Click the button to stream a short sentence with a small delay between chunks."
            ),
            button(key="start", on_click=self.start_stream, type="primary")("Start stream"),
        ]
        if self.state.pending:
            children.append(write_stream(key="widget", stream=self.stream(), cursor="▋"))
            self.state.pending = False
        children.extend(
            [
                json(key="value")({"runs": self.state.runs, "result": "Streaming from st-components"}),
                snippet("write_stream"),
            ]
        )
        return container(key="panel", border=True)(*children)


class FormDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.name_ref = Ref()
        self.notes_ref = Ref()
        self.state = dict(submitted=None)

    def submit(self):
        self.state.submitted = {
            "name": get_element_value(self.name_ref, ""),
            "notes": get_element_value(self.notes_ref, ""),
        }

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("form"),
            form(key="widget", clear_on_submit=False)(
                text_input(key="name", ref=self.name_ref)("Name"),
                text_area(key="notes", ref=self.notes_ref, height=100)("Notes"),
                form_submit_button(key="submit", on_click=self.submit, type="primary")("Submit"),
            ),
            json(key="value")({"submitted": self.state.submitted}),
            snippet("form"),
        )


class FormSubmitButtonDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(submissions=0)

    def submit(self):
        self.state.submissions += 1

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("form_submit_button"),
            form(key="widget_form")(
                text_input(key="title", value="Draft release notes")("Title"),
                form_submit_button(key="widget", on_click=self.submit, type="primary")("Save form"),
            ),
            json(key="value")({"submissions": self.state.submissions}),
            snippet("form_submit_button"),
        )


class MenuButtonDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=None)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("menu_button"),
            menu_button(
                key="widget",
                options=["Draft", "Review", "Ship"],
                on_click=self.sync_state("value"),
                type="primary",
            )("Actions"),
            json(key="value")({"value": self.state.value}),
            snippet("menu_button"),
        )


class PillsDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="Medium")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("pills"),
            pills(key="widget", options=["Low", "Medium", "High"], default=self.state.value, on_change=self.sync_state("value"))("Priority"),
            json(key="value")({"value": self.state.value}),
            snippet("pills"),
        )


class SegmentedControlDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value="List")

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("segmented_control"),
            segmented_control(
                key="widget",
                options=["List", "Board", "Calendar"],
                default=self.state.value,
                on_change=self.sync_state("value"),
            )("View"),
            json(key="value")({"value": self.state.value}),
            snippet("segmented_control"),
        )


class FeedbackDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(value=None)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("feedback"),
            feedback(key="widget", options="stars", on_change=self.sync_state("value")),
            json(key="value")({"value": self.state.value}),
            snippet("feedback"),
        )


class DataEditorDemo(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(
            value=[
                {"task": "Write wrappers", "done": True, "priority": "High"},
                {"task": "Test app", "done": False, "priority": "Medium"},
            ]
        )

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")("data_editor"),
            data_editor(key="widget", data=self.state.value, num_rows="dynamic", on_change=self.sync_state("value"), width="stretch"),
            json(key="value")({"value": self.state.value}),
            snippet("data_editor"),
        )


class PrimitivesApp(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.state = dict(selected="button")

    def current_demo(self):
        demos = {
            "button": ButtonDemo(key="button_demo"),
            "checkbox": CheckboxDemo(key="checkbox_demo"),
            "toggle": ToggleDemo(key="toggle_demo"),
            "radio": RadioDemo(key="radio_demo"),
            "selectbox": SelectboxDemo(key="selectbox_demo"),
            "multiselect": MultiselectDemo(key="multiselect_demo"),
            "slider": SliderDemo(key="slider_demo"),
            "select_slider": SelectSliderDemo(key="select_slider_demo"),
            "text_input": TextInputDemo(key="text_input_demo"),
            "number_input": NumberInputDemo(key="number_input_demo"),
            "text_area": TextAreaDemo(key="text_area_demo"),
            "date_input": DateInputDemo(key="date_input_demo"),
            "datetime_input": DatetimeInputDemo(key="datetime_input_demo"),
            "time_input": TimeInputDemo(key="time_input_demo"),
            "color_picker": ColorPickerDemo(key="color_picker_demo"),
            "file_uploader": FileUploaderDemo(key="file_uploader_demo"),
            "camera_input": CameraInputDemo(key="camera_input_demo"),
            "audio_input": AudioInputDemo(key="audio_input_demo"),
            "chat_input": ChatInputDemo(key="chat_input_demo"),
            "chat_message": ChatMessageDemo(key="chat_message_demo"),
            "status": StatusDemo(key="status_demo"),
            "badge": BadgeDemo(key="badge_demo"),
            "space": SpaceDemo(key="space_demo"),
            "html": HtmlDemo(key="html_demo"),
            "iframe": IframeDemo(key="iframe_demo"),
            "pdf": PdfDemo(key="pdf_demo"),
            "exception": ExceptionDemo(key="exception_demo"),
            "help": HelpDemo(key="help_demo"),
            "page_link": PageLinkDemo(key="page_link_demo"),
            "logo": LogoDemo(key="logo_demo"),
            "area_chart": AreaChartDemo(key="area_chart_demo"),
            "bar_chart": BarChartDemo(key="bar_chart_demo"),
            "line_chart": LineChartDemo(key="line_chart_demo"),
            "scatter_chart": ScatterChartDemo(key="scatter_chart_demo"),
            "map": MapDemo(key="map_demo"),
            "graphviz_chart": GraphvizChartDemo(key="graphviz_chart_demo"),
            "plotly_chart": PlotlyChartDemo(key="plotly_chart_demo"),
            "altair_chart": AltairChartDemo(key="altair_chart_demo"),
            "vega_lite_chart": VegaLiteChartDemo(key="vega_lite_chart_demo"),
            "pydeck_chart": PydeckChartDemo(key="pydeck_chart_demo"),
            "pyplot": PyplotDemo(key="pyplot_demo"),
            "bokeh_chart": BokehChartDemo(key="bokeh_chart_demo"),
            "fragment": FragmentDemo(key="fragment_demo"),
            "dialog": DialogDemo(key="dialog_demo"),
            "write_stream": WriteStreamDemo(key="write_stream_demo"),
            "form": FormDemo(key="form_demo"),
            "form_submit_button": FormSubmitButtonDemo(key="form_submit_button_demo"),
            "menu_button": MenuButtonDemo(key="menu_button_demo"),
            "pills": PillsDemo(key="pills_demo"),
            "segmented_control": SegmentedControlDemo(key="segmented_control_demo"),
            "feedback": FeedbackDemo(key="feedback_demo"),
            "data_editor": DataEditorDemo(key="data_editor_demo"),
        }
        return demos[self.state.selected]

    def render(self):
        return container(key="page")(
            title(key="title")("Primitives smoke test"),
            caption(key="caption")(
                "Manual test app for the wrapped Streamlit primitives currently exposed by st-components."
            ),
            markdown(key="body")(
                "Use the selector to switch demos. Each panel renders one primitive, a compact JSON snapshot, and a short invocation snippet."
            ),
            divider(key="divider"),
            selectbox(
                key="selector",
                options=PRIMITIVES,
                index=PRIMITIVES.index(self.state.selected),
                on_change=self.sync_state("selected"),
            )("Primitive"),
            self.current_demo(),
            source_view(__file__),
        )


App(root=PrimitivesApp(key="app")).render()
