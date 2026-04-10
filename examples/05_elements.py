import datetime
import inspect
import textwrap
import time as pytime

from st_components import App, Component, Ref, State, elements
from st_components.elements import (
    audio,
    altair_chart,
    area_chart,
    audio_input,
    badge,
    balloons,
    bar_chart,
    bokeh_chart,
    button,
    camera_input,
    caption,
    checkbox,
    chat_input,
    chat_message,
    code,
    columns,
    color_picker,
    container,
    dataframe,
    data_editor,
    date_input,
    datetime_input,
    divider,
    dialog,
    download_button,
    empty,
    error,
    expander,
    exception,
    feedback,
    file_uploader,
    form,
    fragment,
    form_submit_button,
    graphviz_chart,
    header,
    help,
    html,
    image,
    info,
    iframe,
    json,
    latex,
    link_button,
    line_chart,
    logo,
    markdown,
    map,
    menu_button,
    metric,
    multiselect,
    number_input,
    page_link,
    pdf,
    pills,
    plotly_chart,
    popover,
    progress,
    pydeck_chart,
    pyplot,
    radio,
    segmented_control,
    select_slider,
    selectbox,
    sidebar,
    slider,
    snow,
    space,
    scatter_chart,
    spinner,
    status,
    subheader,
    success,
    table,
    tabs,
    text,
    text_area,
    text_input,
    time_input,
    title,
    toast,
    toggle,
    vega_lite_chart,
    video,
    warning,
    write,
    write_stream,
)
from st_components.elements.runtime import show_balloons, show_progress, show_snow, show_spinner, show_toast

PRIMITIVES = sorted(elements.__all__)


def signature_doc(name):
    if name == "fragment":
        return "fragment(key=..., scoped=False, run_every=None)"
    target = globals().get(name)
    if target is None:
        raise RuntimeError(f"Missing public callable for primitive {name!r}.")
    try:
        return f"{name}{inspect.signature(target)}"
    except (TypeError, ValueError):
        raise RuntimeError(f"Could not inspect signature for primitive {name!r}.")


def snippet(name, component=None):
    try:
        signature_block = code(key="signature", language="python")(signature_doc(name))
    except RuntimeError as err:
        signature_block = error(key="signature_error")(str(err))

    if component is None:
        implementation_block = error(key="implementation_error")("Missing demo component for source inspection.")
    else:
        try:
            implementation = textwrap.dedent(inspect.getsource(type(component)))
            implementation_block = code(key="implementation", language="python")(implementation)
        except (OSError, TypeError):
            implementation_block = error(key="implementation_error")(
                f"Could not inspect implementation for demo component {type(component).__name__}."
            )

    return container(key="snippet_block")(
        signature_block,
        expander(key="implementation_expander", label="Demo implementation")(
            implementation_block
        ),
    )

class PrimitivePanelValue(Component):
    """Reads the demo element's state via its Ref prop."""

    def render(self):
        ref = self.props.get("demo_ref")
        value = ref.state() if ref else None
        if value is None:
            return None
        return json(key="value")(value)


class PrimitivePanel(Component):
    def __init__(self, *, name, demo, demo_ref, **props):
        super().__init__(name=name, demo=demo, demo_ref=demo_ref, **props)

    def render(self):
        return container(key="panel", border=True)(
            subheader(key="title")(self.props.name),
            self.props.demo,
            PrimitivePanelValue(key="value_block", name=self.props.name, demo_ref=self.props.demo_ref),
            snippet(self.props.name, self.props.demo),
        )


class AudioDemo(Component):
    def render(self):
        return audio(
            key="widget",
            data="https://www.w3schools.com/html/horse.mp3",
            format="audio/mpeg",
        )


class BalloonsDemo(Component):
    class DemoState(State):
        element_runs = 0
        helper_runs = 0
        pending = None
        consumed = None
        last_mode = None

    def trigger_element(self):
        self.state.element_runs += 1
        self.state.pending = self.state.element_runs
        self.state.last_mode = "element"

    def trigger_helper(self):
        show_balloons()
        self.state.helper_runs += 1
        self.state.last_mode = "helper"

    def render(self):
        effect_block = None
        if self.state.pending != self.state.consumed:
            effect_block = balloons(key=f"widget_{self.state.pending}")
            self.state.consumed = self.state.pending
        return (
            markdown(key="hint")(
                "Use the first button to trigger the declarative `balloons(...)` element on the next rerender, "
                "or the second to call `show_balloons()` directly inside the callback."
            ),
            columns(key="actions", spec=2)(
                button(key="element", on_click=self.trigger_element, type="primary")("Trigger via element"),
                button(key="helper", on_click=self.trigger_helper)("Trigger via helper"),
            ),
            effect_block,
        )


class CaptionDemo(Component):
    def render(self):
        return caption(key="widget")("Small secondary text")


class CodeDemo(Component):
    def render(self):
        return code(key="widget", language="python")("answer = 42")


class ColumnsDemo(Component):
    def render(self):
        return columns(key="widget", spec=2)(
            container(key="left", border=True)(markdown(key="body")("Left column")),
            container(key="right", border=True)(markdown(key="body")("Right column")),
        )


class ContainerDemo(Component):
    def render(self):
        return container(key="widget", border=True)(
            markdown(key="body")("Contained content"),
            badge(key="tag", color="blue")("Nested element"),
        )


class DataframeDemo(Component):
    def render(self):
        return dataframe(key="widget", data=[
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ])


class DividerDemo(Component):
    def render(self):
        return (
            markdown(key="before")("Content before"),
            divider(key="widget"),
            markdown(key="after")("Content after"),
        )


class DownloadButtonDemo(Component):
    def render(self):
        return download_button(key="widget", data="hello from st-components\n", file_name="demo.txt")("Download")


class EmptyDemo(Component):
    def render(self):
        return empty(key="widget")(markdown(key="slot")("Placeholder content"))


class ErrorDemo(Component):
    def render(self):
        return error(key="widget")("Something failed")


class ExpanderDemo(Component):
    def render(self):
        return expander(key="widget", label="More details", expanded=True)(
            markdown(key="body")("Expanded content")
        )


class HeaderDemo(Component):
    def render(self):
        return header(key="widget")("Section heading")


class SubheaderTextDemo(Component):
    def render(self):
        return subheader(key="widget")("Section heading")


class TitleTextDemo(Component):
    def render(self):
        return title(key="widget")("Page title")


class ImageDemo(Component):
    def render(self):
        return image(
            key="widget",
            image="https://www.w3schools.com/html/img_chania.jpg",
            caption="Remote demo image",
        )


class InfoDemo(Component):
    def render(self):
        return info(key="widget")("Heads-up message")


class JsonDemo(Component):
    def render(self):
        payload = {"status": "ok", "count": 3}
        return json(key="widget", body=payload)


class LatexDemo(Component):
    def render(self):
        return latex(key="widget")(r"E = mc^2")


class LinkButtonDemo(Component):
    def render(self):
        return link_button(key="widget", url="https://streamlit.io")("Open docs")


class MarkdownDemo(Component):
    def render(self):
        return markdown(key="widget")("**Bold** _markdown_ sample")


class MetricDemo(Component):
    def render(self):
        return metric(key="widget", label="Revenue", value="EUR 12.4k", delta="+8%")


class PopoverDemo(Component):
    def render(self):
        return popover(key="widget", label="Open popover")(
            markdown(key="body")("Popover content")
        )


class ProgressDemo(Component):
    class DemoState(State):
        runs: int = 0
        p: int = 0

    def _msg(self, p):
        if p == 0: return "Idle"
        if p < 30: return "Starting..."
        if p < 70: return "Progressing..."
        if p < 100: return "Finishing..."
        return "Done!"

    def step(self):
        p = (self.state.p + 10) % 110
        self.state.p = p
        self.state.runs += 1
        # Update the bar in-place via its Streamlit handle (no remount)
        handle = self.widget.handle
        if handle:
            handle.progress(p, text=self._msg(p), width="stretch")

    def render(self):
        return (
            markdown(key="hint")(
                "`self.widget.handle` gives direct access to the Streamlit DeltaGenerator. "
                "Calling `.progress(value)` on it updates in-place without remounting the widget."
            ),
            button(key="step", on_click=self.step, type="primary")("Step progress"),
            progress(key="widget", value=self.state.p, text=self._msg(self.state.p), width="stretch"),
            metric(key="runs", label="Runs", value=self.state.runs),
        )


class SidebarDemo(Component):
    def render(self):
        return (
            markdown(key="hint")("This primitive renders in Streamlit's sidebar, not inside the body panel."),
            sidebar(key="widget")(markdown(key="body")("Sidebar content")),
        )


class SnowDemo(Component):
    class DemoState(State):
        element_runs = 0
        helper_runs = 0
        pending = None
        consumed = None
        last_mode = None

    def trigger_element(self):
        self.state.element_runs += 1
        self.state.pending = self.state.element_runs
        self.state.last_mode = "element"

    def trigger_helper(self):
        show_snow()
        self.state.helper_runs += 1
        self.state.last_mode = "helper"

    def render(self):
        effect_block = None
        if self.state.pending != self.state.consumed:
            effect_block = snow(key=f"widget_{self.state.pending}")
            self.state.consumed = self.state.pending
        return (
            markdown(key="hint")(
                "Use the first button to trigger the declarative `snow(...)` element on the next rerender, "
                "or the second to call `show_snow()` directly inside the callback."
            ),
            columns(key="actions", spec=2)(
                button(key="element", on_click=self.trigger_element, type="primary")("Trigger via element"),
                button(key="helper", on_click=self.trigger_helper)("Trigger via helper"),
            ),
            effect_block,
        )


class SlowSpinnerPreview(Component):
    def render(self):
        pytime.sleep(1.8)
        return success(key="done")("Slow subtree rendered")


class SpinnerDemo(Component):
    class DemoState(State):
        runs: int = 0
        pending: int = 0
        consumed: int = 0

    def trigger(self):
        self.state.runs += 1
        self.state.pending = self.state.runs

    def render(self):
        show_spinner_block = None
        if self.state.pending != self.state.consumed:
            self.state.consumed = self.state.pending
            show_spinner_block = spinner(
                key=f"widget_{self.state.pending}",
                text="Rendering slow subtree",
                show_time=True,
            )(SlowSpinnerPreview(key=f"preview_{self.state.pending}"))

        return (
            markdown(key="hint")(
                "`spinner(...)` wraps a slow subtree during render."
            ),
            button(key="trigger", on_click=self.trigger, type="primary")("Trigger slow render"),
            show_spinner_block,
        )


class SuccessDemo(Component):
    def render(self):
        return success(key="widget")("Saved successfully")


class TableDemo(Component):
    def render(self):
        return table(key="widget", data=[
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ])


class TabsDemo(Component):
    def render(self):
        return tabs(key="widget", tabs=["Alpha", "Beta"])(
            markdown(key="alpha")("Alpha"),
            markdown(key="beta")("Beta"),
        )


class TextDemo(Component):
    def render(self):
        return text(key="widget")("Monospace-like plain text")


class ToastDemo(Component):
    class DemoState(State):
        element_runs = 0
        helper_runs = 0
        pending = None
        consumed = None
        last_mode = None

    def trigger_element(self):
        self.state.element_runs += 1
        self.state.pending = self.state.element_runs
        self.state.last_mode = "element"

    def trigger_helper(self):
        show_toast("Saved draft", duration="short")
        self.state.helper_runs += 1
        self.state.last_mode = "helper"

    def render(self):
        effect_block = None
        if self.state.pending != self.state.consumed:
            effect_block = toast(key=f"widget_{self.state.pending}")("Saved draft")
            self.state.consumed = self.state.pending
        return (
            markdown(key="hint")(
                "Use the first button to trigger the declarative `toast(...)` element on the next rerender, "
                "or the second to call `show_toast(...)` directly inside the callback."
            ),
            columns(key="actions", spec=2)(
                button(key="element", on_click=self.trigger_element, type="primary")("Trigger via element"),
                button(key="helper", on_click=self.trigger_helper)("Trigger via helper"),
            ),
            effect_block,
        )


class VideoDemo(Component):
    def render(self):
        return video(key="widget", data="https://www.w3schools.com/html/mov_bbb.mp4")


class WarningDemo(Component):
    def render(self):
        return warning(key="widget")("Review required")


class WriteDemo(Component):
    def render(self):
        return write("Mixed output", {"count": 3}, key="widget")


class ButtonDemo(Component):
    class DemoState(State):
        clicks = 0

    def click(self):
        self.state.clicks += 1

    def render(self):
        return button(key="widget", on_click=self.click, type="primary")("Click me")


class CheckboxDemo(Component):
    class DemoState(State):
        current = True

    def render(self):
        return checkbox(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Enable feature")


class ToggleDemo(Component):
    class DemoState(State):
        current = False

    def render(self):
        return toggle(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Dark mode")


class RadioDemo(Component):
    class DemoState(State):
        current = "Alpha"

    def render(self):
        return radio(
            key="widget",
            options=["Alpha", "Beta", "Gamma"],
            index=["Alpha", "Beta", "Gamma"].index(self.state.current),
            on_change=self.sync_state("current"),
        )("Channel")


class SelectboxDemo(Component):
    class DemoState(State):
        current = "Paris"

    def render(self):
        options = ["Paris", "Berlin", "Tokyo"]
        return selectbox(
            key="widget",
            options=options,
            index=options.index(self.state.current),
            on_change=self.sync_state("current"),
        )("City")


class MultiselectDemo(Component):
    class DemoState(State):
        current = ["Python"]

    def render(self):
        return multiselect(
            key="widget",
            options=["Python", "Rust", "Go", "TypeScript"],
            default=self.state.current,
            on_change=self.sync_state("current"),
        )("Languages")


class SliderDemo(Component):
    class DemoState(State):
        current = 5

    def render(self):
        return slider(key="widget", min_value=0, max_value=10, value=self.state.current, on_change=self.sync_state("current"))("Score")


class SelectSliderDemo(Component):
    class DemoState(State):
        current = "M"

    def render(self):
        return select_slider(
            key="widget",
            options=["XS", "S", "M", "L", "XL"],
            value=self.state.current,
            on_change=self.sync_state("current"),
        )("Size")


class TextInputDemo(Component):
    class DemoState(State):
        current = "Baptiste"

    def render(self):
        return text_input(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Name")


class NumberInputDemo(Component):
    class DemoState(State):
        current = 42

    def render(self):
        return number_input(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Count")


class TextAreaDemo(Component):
    class DemoState(State):
        current = "Short multiline note."

    def render(self):
        return text_area(key="widget", value=self.state.current, height=120, on_change=self.sync_state("current"))("Notes")


class DateInputDemo(Component):
    class DemoState(State):
        current = datetime.date.today()

    def render(self):
        return date_input(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Date")


class DatetimeInputDemo(Component):
    class DemoState(State):
        current = datetime.datetime.now().replace(second=0, microsecond=0)

    def render(self):
        return datetime_input(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Schedule")


class TimeInputDemo(Component):
    class DemoState(State):
        current = datetime.time(hour=9, minute=30)

    def render(self):
        return time_input(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Time")


class ColorPickerDemo(Component):
    class DemoState(State):
        current = "#ff4b4b"

    def render(self):
        return color_picker(key="widget", value=self.state.current, on_change=self.sync_state("current"))("Accent color")


class FileUploaderDemo(Component):
    class DemoState(State):
        value = None

    def file_info(self, value):
        if value is None:
            return None
        if isinstance(value, list):
            return [self.file_info(item) for item in value]
        return {
            "name": getattr(value, "name", None),
            "type": getattr(value, "type", None),
            "size": getattr(value, "size", None),
        }

    def sync_value(self, value):
        self.state.value = self.file_info(value)

    def render(self):
        return file_uploader(key="widget", on_change=self.sync_value)("Upload a file")


class CameraInputDemo(Component):
    class DemoState(State):
        value = None

    def file_info(self, value):
        if value is None:
            return None
        return {
            "name": getattr(value, "name", None),
            "type": getattr(value, "type", None),
            "size": getattr(value, "size", None),
        }

    def sync_value(self, value):
        self.state.value = self.file_info(value)

    def render(self):
        return camera_input(key="widget", on_change=self.sync_value)("Take a photo")


class AudioInputDemo(Component):
    class DemoState(State):
        value = None

    def file_info(self, value):
        if value is None:
            return None
        return {
            "name": getattr(value, "name", None),
            "type": getattr(value, "type", None),
            "size": getattr(value, "size", None),
        }

    def sync_value(self, value):
        self.state.value = self.file_info(value)

    def render(self):
        return audio_input(key="widget", on_change=self.sync_value)("Record a short clip")


class ChatInputDemo(Component):
    class DemoState(State):
        messages = ["The callback receives the submitted message directly."]

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
        return (
            *message_nodes,
            chat_input(key="widget", on_submit=self.submit)("Send a message"),
        )


class ChatMessageDemo(Component):
    def render(self):
        return (
            chat_message(key="assistant", name="assistant")(
                markdown(key="body")("Use this wrapper to compose chat UIs from simple children.")
            ),
            chat_message(key="user", name="user")(
                markdown(key="body")("Messages stay regular Elements inside the container.")
            ),
        )


class StatusDemo(Component):
    def render(self):
        return status(key="widget", label="Syncing dataset", state="running", expanded=True)(
            markdown(key="body")("3 files indexed, 1 pending."),
        )


class BadgeDemo(Component):
    def render(self):
        return badge(key="widget", color="green", icon=":material/check_circle:")("Stable wrapper")


class SpaceDemo(Component):
    def render(self):
        return (
            markdown(key="before")("Block before the spacer."),
            space(key="widget", size="large"),
            markdown(key="after")("Block after the spacer."),
        )


class HtmlDemo(Component):
    def render(self):
        body = (
            '<div style="padding: 12px 16px; border-radius: 14px; '
            'background: linear-gradient(135deg, #0f172a, #1d4ed8); color: white;">'
            '<strong>html()</strong><br/>Inline markup passed directly to Streamlit.'
            '</div>'
        )
        return html(key="widget", body=body)


class IframeDemo(Component):
    def render(self):
        return iframe(key="widget", src="https://example.com", height=240)


class PdfDemo(Component):
    def render(self):
        return pdf(
            key="widget",
            data="https://academicpages.github.io/files/paper2.pdf",
            height=240,
        )


class ExceptionDemo(Component):
    def render(self):
        return exception(key="widget", exception=RuntimeError("Wrapper smoke test"))


class HelpDemo(Component):
    def render(self):
        return help(key="widget", obj=datetime.datetime)


class PageLinkDemo(Component):
    def render(self):
        return page_link(
            key="widget",
            page="https://streamlit.io",
            label="Open Streamlit",
            icon=":material/open_in_new:",
        )


class LogoDemo(Component):
    def render(self):
        return (
            markdown(key="hint")("This primitive updates the app chrome logo, not the body of the page."),
            logo(
                key="widget",
                image="https://streamlit.io/images/brand/streamlit-mark-color.png",
                size="large",
            ),
        )


class AreaChartDemo(Component):
    def render(self):
        return area_chart(key="widget", data=[
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ], x="month", y=["alpha", "beta"], height=260)


class BarChartDemo(Component):
    def render(self):
        return bar_chart(key="widget", data=[
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ], x="month", y=["alpha", "beta"], height=260)


class LineChartDemo(Component):
    def render(self):
        return line_chart(key="widget", data=[
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ], x="month", y=["alpha", "beta"], height=260)


class ScatterChartDemo(Component):
    def render(self):
        return scatter_chart(key="widget", data=[
            {"x": 1, "y": 3, "size": 10, "segment": "A"},
            {"x": 2, "y": 8, "size": 18, "segment": "A"},
            {"x": 3, "y": 5, "size": 12, "segment": "B"},
            {"x": 4, "y": 11, "size": 20, "segment": "B"},
        ], x="x", y="y", size="size", color="segment", height=260)


class MapDemo(Component):
    def render(self):
        return map(key="widget", data=[
            {"lat": 48.8566, "lon": 2.3522},
            {"lat": 51.5072, "lon": -0.1276},
            {"lat": 40.7128, "lon": -74.0060},
        ], latitude="lat", longitude="lon", zoom=1, height=320)


class GraphvizChartDemo(Component):
    def render(self):
        return graphviz_chart(key="widget", figure_or_dot="""
        digraph Demo {
            rankdir=LR;
            Streamlit -> st_components;
            st_components -> primitives;
            primitives -> browser;
        }
        """.strip())


class PlotlyChartDemo(Component):
    class DemoState(State):
        selection = None

    def render(self):
        import plotly.express as px

        fig = px.scatter([
            {"x": 1, "y": 3, "size": 10, "segment": "A"},
            {"x": 2, "y": 8, "size": 18, "segment": "A"},
            {"x": 3, "y": 5, "size": 12, "segment": "B"},
            {"x": 4, "y": 11, "size": 20, "segment": "B"},
        ], x="x", y="y", size="size", color="segment")
        return (
            markdown(key="hint")("Box- or lasso-select points to trigger `on_select`."),
            plotly_chart(key="widget", figure_or_data=fig, on_select=self.sync_state("selection"), height=360),
        )


class AltairChartDemo(Component):
    class DemoState(State):
        selection = None

    def render(self):
        import altair as alt

        pick = alt.selection_interval(name="pick")
        chart = (
            alt.Chart(alt.Data(values=[
                {"x": 1, "y": 3, "size": 10, "segment": "A"},
                {"x": 2, "y": 8, "size": 18, "segment": "A"},
                {"x": 3, "y": 5, "size": 12, "segment": "B"},
                {"x": 4, "y": 11, "size": 20, "segment": "B"},
            ]))
            .mark_circle(size=120)
            .encode(
                x="x:Q",
                y="y:Q",
                color="segment:N",
                tooltip=["x:Q", "y:Q", "segment:N"],
            )
            .add_params(pick)
        )
        return (
            markdown(key="hint")("Drag a region on the chart to test `on_select`."),
            altair_chart(key="widget", altair_chart=chart, on_select=self.sync_state("selection"), selection_mode="pick", height=320),
        )


class VegaLiteChartDemo(Component):
    class DemoState(State):
        selection = None

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
        return (
            markdown(key="hint")("Drag a region on the chart to test `on_select`."),
            vega_lite_chart(
                key="widget",
                data=[
                    {"x": 1, "y": 3, "size": 10, "segment": "A"},
                    {"x": 2, "y": 8, "size": 18, "segment": "A"},
                    {"x": 3, "y": 5, "size": 12, "segment": "B"},
                    {"x": 4, "y": 11, "size": 20, "segment": "B"},
                ],
                spec=spec,
                on_select=self.sync_state("selection"),
                selection_mode="pick",
                height=320,
            ),
        )


class PydeckChartDemo(Component):
    class DemoState(State):
        selection = None

    def render(self):
        import pydeck as pdk

        deck = pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=48.8566, longitude=2.3522, zoom=1),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=[
                        {"lat": 48.8566, "lon": 2.3522},
                        {"lat": 51.5072, "lon": -0.1276},
                        {"lat": 40.7128, "lon": -74.0060},
                    ],
                    get_position="[lon, lat]",
                    get_fill_color="[34, 197, 94, 180]",
                    get_radius=180000,
                    pickable=True,
                )
            ],
        )
        return (
            markdown(key="hint")("Click a point on the map to test `on_select`."),
            pydeck_chart(key="widget", pydeck_obj=deck, on_select=self.sync_state("selection"), height=360),
        )


class PyplotDemo(Component):
    def render(self):
        import matplotlib.pyplot as plt

        rows = [
            {"month": "Jan", "alpha": 12, "beta": 7},
            {"month": "Feb", "alpha": 18, "beta": 11},
            {"month": "Mar", "alpha": 9, "beta": 15},
            {"month": "Apr", "alpha": 22, "beta": 13},
        ]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot([row["month"] for row in rows], [row["alpha"] for row in rows], label="alpha")
        ax.plot([row["month"] for row in rows], [row["beta"] for row in rows], label="beta")
        ax.set_ylabel("value")
        ax.legend()
        return pyplot(key="widget", fig=fig)


class BokehChartDemo(Component):
    def render(self):
        from bokeh.plotting import figure

        fig = figure(height=280, sizing_mode="stretch_width", title="Bokeh wrapper")
        fig.line([1, 2, 3, 4], [3, 7, 5, 9], line_width=3)
        fig.circle([1, 2, 3, 4], [3, 7, 5, 9], size=10)
        return bokeh_chart(key="widget", figure=fig)


class LiveClock(Component):
    """Must live INSIDE the fragment so it re-renders on each fragment rerun."""
    def render(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return container(key="frame", border=True)(
            markdown(key="title")(f"**Fragment clock:** `{now}`"),
            caption(key="body")("Auto-refreshes every second."),
        )


class FragmentDemo(Component):
    class DemoState(State):
        clicks: int = 0

    def click(self):
        self.state.clicks += 1

    def inject(self):
        self.target(
            metric(key="injected", label="Injected at", value=datetime.datetime.now().strftime("%H:%M:%S")),
            caption(key="note")("This content was pushed via `self.target(children)`."),
        )

    def reset(self):
        self.target.reset()

    def render(self):
        return (
            markdown(key="hint")(
                "`fragment` supports scoped re-rendering (`run_every`), "
                "and dynamic children injection via `self.ref` navigation."
            ),
            fragment(key="target", scoped=True, run_every=1)(
                LiveClock(key="clock"),
            ),
            columns(key="actions")(
                button(key="clicks", on_click=self.click)(f"Parent button ({self.state.clicks})"),
                button(key="inject", on_click=self.inject, type="primary")("Inject content"),
                button(key="reset", on_click=self.reset)("Reset"),
            ),
        )


class DialogDemo(Component):
    class DemoState(State):
        open = False
        confirmed = 0

    def open_dialog(self):
        self.state.open = True

    def close_dialog(self):
        self.state.open = False

    def confirm(self):
        self.state.confirmed += 1
        self.state.open = False

    def render(self):
        children = [
            button(key="open", on_click=self.open_dialog, type="primary")("Open dialog"),
        ]
        if self.state.open:
            children.insert(
                1,
                dialog(key="widget", title="Confirm action", on_dismiss=self.close_dialog)(
                    markdown(key="body")("This modal is rendered through the `dialog` Element wrapper."),
                    button(key="confirm", on_click=self.confirm, type="primary")("Confirm"),
                ),
            )
        return tuple(children)


class WriteStreamDemo(Component):
    class DemoState(State):
        pending = False
        runs = 0

    def start_stream(self):
        self.state.pending = True
        self.state.runs += 1

    def stream(self):
        for chunk in ("Streaming ", "from ", "st-components"):
            pytime.sleep(0.2)
            yield chunk

    def render(self):
        children = [
            markdown(key="hint")(
                "Click the button to stream a short sentence with a small delay between chunks."
            ),
            button(key="start", on_click=self.start_stream, type="primary")("Start stream"),
        ]
        if self.state.pending:
            children.append(write_stream(key="widget", stream=self.stream(), cursor="▋"))
            self.state.pending = False
        return tuple(children)


class FormDemo(Component):
    class DemoState(State):
        submitted = None

    def submit(self):
        # Navigate to form children via relative ref
        self.state.submitted = {
            "name": self.widget.name.state().output or "",
            "notes": self.widget.notes.state().output or "",
        }

    def render(self):
        return form(key="widget", clear_on_submit=False)(
            text_input(key="name")("Name"),
            text_area(key="notes", height=100)("Notes"),
            form_submit_button(key="submit", on_click=self.submit, type="primary")("Submit"),
        )


class FormSubmitButtonDemo(Component):
    class DemoState(State):
        submissions = 0

    def submit(self):
        self.state.submissions += 1

    def render(self):
        return form(key="widget_form")(
            text_input(key="title", value="Draft release notes")("Title"),
            form_submit_button(key="widget", on_click=self.submit, type="primary")("Save form"),
        )


class MenuButtonDemo(Component):
    class DemoState(State):
        choice = None

    def render(self):
        return menu_button(
            key="widget",
            options=["Draft", "Review", "Ship"],
            on_click=self.sync_state("choice"),
            type="primary",
        )("Actions")


class PillsDemo(Component):
    class DemoState(State):
        current = "Medium"

    def render(self):
        return pills(key="widget", options=["Low", "Medium", "High"], default=self.state.current, on_change=self.sync_state("current"))("Priority")


class SegmentedControlDemo(Component):
    class DemoState(State):
        current = "List"

    def render(self):
        return segmented_control(
            key="widget",
            options=["List", "Board", "Calendar"],
            default=self.state.current,
            on_change=self.sync_state("current"),
        )("View")


class FeedbackDemo(Component):
    class DemoState(State):
        rating = None

    def render(self):
        return feedback(key="widget", options="stars", on_change=self.sync_state("rating"))


class DataEditorDemo(Component):
    class DemoState(State):
        rows = [
            {"task": "Write wrappers", "done": True, "priority": "High"},
            {"task": "Test app", "done": False, "priority": "Medium"},
        ]

    def render(self):
        return data_editor(key="widget", data=self.state.rows, num_rows="dynamic", on_change=self.sync_state("rows"), width="stretch")


class PrimitivesApp(Component):
    class DemoState(State):
        selected = PRIMITIVES[0]

    def current_demo(self):
        demo_ref = Ref()
        demos = {
            "audio": AudioDemo(key="audio_demo", ref=demo_ref),
            "audio_input": AudioInputDemo(key="audio_input_demo", ref=demo_ref),
            "altair_chart": AltairChartDemo(key="altair_chart_demo", ref=demo_ref),
            "area_chart": AreaChartDemo(key="area_chart_demo", ref=demo_ref),
            "badge": BadgeDemo(key="badge_demo", ref=demo_ref),
            "balloons": BalloonsDemo(key="balloons_demo", ref=demo_ref),
            "bar_chart": BarChartDemo(key="bar_chart_demo", ref=demo_ref),
            "bokeh_chart": BokehChartDemo(key="bokeh_chart_demo", ref=demo_ref),
            "button": ButtonDemo(key="button_demo", ref=demo_ref),
            "camera_input": CameraInputDemo(key="camera_input_demo", ref=demo_ref),
            "caption": CaptionDemo(key="caption_demo", ref=demo_ref),
            "chat_input": ChatInputDemo(key="chat_input_demo", ref=demo_ref),
            "chat_message": ChatMessageDemo(key="chat_message_demo", ref=demo_ref),
            "checkbox": CheckboxDemo(key="checkbox_demo", ref=demo_ref),
            "code": CodeDemo(key="code_demo", ref=demo_ref),
            "color_picker": ColorPickerDemo(key="color_picker_demo", ref=demo_ref),
            "columns": ColumnsDemo(key="columns_demo", ref=demo_ref),
            "container": ContainerDemo(key="container_demo", ref=demo_ref),
            "data_editor": DataEditorDemo(key="data_editor_demo", ref=demo_ref),
            "dataframe": DataframeDemo(key="dataframe_demo", ref=demo_ref),
            "date_input": DateInputDemo(key="date_input_demo", ref=demo_ref),
            "datetime_input": DatetimeInputDemo(key="datetime_input_demo", ref=demo_ref),
            "dialog": DialogDemo(key="dialog_demo", ref=demo_ref),
            "divider": DividerDemo(key="divider_demo", ref=demo_ref),
            "download_button": DownloadButtonDemo(key="download_button_demo", ref=demo_ref),
            "empty": EmptyDemo(key="empty_demo", ref=demo_ref),
            "error": ErrorDemo(key="error_demo", ref=demo_ref),
            "exception": ExceptionDemo(key="exception_demo", ref=demo_ref),
            "expander": ExpanderDemo(key="expander_demo", ref=demo_ref),
            "feedback": FeedbackDemo(key="feedback_demo", ref=demo_ref),
            "file_uploader": FileUploaderDemo(key="file_uploader_demo", ref=demo_ref),
            "form": FormDemo(key="form_demo", ref=demo_ref),
            "form_submit_button": FormSubmitButtonDemo(key="form_submit_button_demo", ref=demo_ref),
            "graphviz_chart": GraphvizChartDemo(key="graphviz_chart_demo", ref=demo_ref),
            "fragment": FragmentDemo(key="fragment_demo", ref=demo_ref),
            "header": HeaderDemo(key="header_demo", ref=demo_ref),
            "help": HelpDemo(key="help_demo", ref=demo_ref),
            "html": HtmlDemo(key="html_demo", ref=demo_ref),
            "iframe": IframeDemo(key="iframe_demo", ref=demo_ref),
            "image": ImageDemo(key="image_demo", ref=demo_ref),
            "info": InfoDemo(key="info_demo", ref=demo_ref),
            "json": JsonDemo(key="json_demo", ref=demo_ref),
            "latex": LatexDemo(key="latex_demo", ref=demo_ref),
            "line_chart": LineChartDemo(key="line_chart_demo", ref=demo_ref),
            "link_button": LinkButtonDemo(key="link_button_demo", ref=demo_ref),
            "logo": LogoDemo(key="logo_demo", ref=demo_ref),
            "map": MapDemo(key="map_demo", ref=demo_ref),
            "markdown": MarkdownDemo(key="markdown_demo", ref=demo_ref),
            "menu_button": MenuButtonDemo(key="menu_button_demo", ref=demo_ref),
            "metric": MetricDemo(key="metric_demo", ref=demo_ref),
            "multiselect": MultiselectDemo(key="multiselect_demo", ref=demo_ref),
            "number_input": NumberInputDemo(key="number_input_demo", ref=demo_ref),
            "page_link": PageLinkDemo(key="page_link_demo", ref=demo_ref),
            "pdf": PdfDemo(key="pdf_demo", ref=demo_ref),
            "pills": PillsDemo(key="pills_demo", ref=demo_ref),
            "plotly_chart": PlotlyChartDemo(key="plotly_chart_demo", ref=demo_ref),
            "popover": PopoverDemo(key="popover_demo", ref=demo_ref),
            "progress": ProgressDemo(key="progress_demo", ref=demo_ref),
            "pydeck_chart": PydeckChartDemo(key="pydeck_chart_demo", ref=demo_ref),
            "pyplot": PyplotDemo(key="pyplot_demo", ref=demo_ref),
            "radio": RadioDemo(key="radio_demo", ref=demo_ref),
            "scatter_chart": ScatterChartDemo(key="scatter_chart_demo", ref=demo_ref),
            "segmented_control": SegmentedControlDemo(key="segmented_control_demo", ref=demo_ref),
            "select_slider": SelectSliderDemo(key="select_slider_demo", ref=demo_ref),
            "selectbox": SelectboxDemo(key="selectbox_demo", ref=demo_ref),
            "sidebar": SidebarDemo(key="sidebar_demo", ref=demo_ref),
            "slider": SliderDemo(key="slider_demo", ref=demo_ref),
            "snow": SnowDemo(key="snow_demo", ref=demo_ref),
            "space": SpaceDemo(key="space_demo", ref=demo_ref),
            "spinner": SpinnerDemo(key="spinner_demo", ref=demo_ref),
            "status": StatusDemo(key="status_demo", ref=demo_ref),
            "subheader": SubheaderTextDemo(key="subheader_demo", ref=demo_ref),
            "success": SuccessDemo(key="success_demo", ref=demo_ref),
            "table": TableDemo(key="table_demo", ref=demo_ref),
            "tabs": TabsDemo(key="tabs_demo", ref=demo_ref),
            "text": TextDemo(key="text_demo", ref=demo_ref),
            "text_area": TextAreaDemo(key="text_area_demo", ref=demo_ref),
            "text_input": TextInputDemo(key="text_input_demo", ref=demo_ref),
            "time_input": TimeInputDemo(key="time_input_demo", ref=demo_ref),
            "title": TitleTextDemo(key="title_text_demo", ref=demo_ref),
            "toast": ToastDemo(key="toast_demo", ref=demo_ref),
            "toggle": ToggleDemo(key="toggle_demo", ref=demo_ref),
            "vega_lite_chart": VegaLiteChartDemo(key="vega_lite_chart_demo", ref=demo_ref),
            "video": VideoDemo(key="video_demo", ref=demo_ref),
            "warning": WarningDemo(key="warning_demo", ref=demo_ref),
            "write": WriteDemo(key="write_demo", ref=demo_ref),
            "write_stream": WriteStreamDemo(key="write_stream_demo", ref=demo_ref),
        }
        return demos[self.state.selected], demo_ref

    def render(self):
        demo, demo_ref = self.current_demo()
        return container(key="page")(
            markdown(key="title")(
                "## Elements Index\n\n"
                "Browse and test every element wrapped by st-components. "
                "Pick one below to see it in action with a live demo, "
                "its current state snapshot, and the implementation source."
            ),
            selectbox(
                key="selector",
                options=PRIMITIVES,
                index=PRIMITIVES.index(self.state.selected),
                on_change=self.sync_state("selected"),
            )(f"Element ({len(PRIMITIVES)} available)"),
            divider(key="divider"),
            PrimitivePanel(key="current_panel", name=self.state.selected, demo=demo, demo_ref=demo_ref),
        )


App(page_title="Elements Index")(PrimitivesApp(key="app")).render()
