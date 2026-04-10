"""
03 - Callbacks

Shows how widget callbacks receive the current value directly, and how
sync_state() provides a shortcut for the most common pattern.
Introduces: on_change, on_click, sync_state, live metrics.
"""
import st_components as stc
from st_components.elements import (
    columns, container, divider, markdown, metric, slider, success,
    text_area, text_input, toggle,
)

from examples._source import source_view


class ProfileForm(stc.Component):
    """Each widget's on_change receives the current value — no unwrapping needed."""

    class ProfileFormState(stc.State):
        name: str = "Ada Lovelace"
        focus: int = 7
        dark_mode: bool = False
        notes: str = ""
        last_event: str = "(nothing yet)"

    def on_name(self, value):
        self.state.name = value
        self.state.last_event = f"name → {value!r}"

    def on_focus(self, value):
        self.state.focus = value
        self.state.last_event = f"focus → {value}"

    def on_dark(self, value):
        self.state.dark_mode = value
        self.state.last_event = f"dark_mode → {value}"

    def on_notes(self, value):
        self.state.notes = value
        self.state.last_event = f"notes → {len(value)} chars"

    def render(self):
        return container(key="form", border=True)(
            markdown(key="h")("### Explicit callbacks"),
            markdown(key="desc")(
                "Each `on_change` callback receives the widget's **current value** directly. "
                "No need to reach into `st.session_state`."
            ),
            text_input(key="name", value=self.state.name, on_change=self.on_name)("Name"),
            slider(key="focus", min_value=0, max_value=10, value=self.state.focus, on_change=self.on_focus)("Focus"),
            toggle(key="dark", value=self.state.dark_mode, on_change=self.on_dark)("Dark mode"),
            text_area(key="notes", value=self.state.notes, height=100, on_change=self.on_notes,
                      placeholder="Type here…")("Notes"),
            success(key="event")(f"Last callback: **{self.state.last_event}**"),
            columns(key="metrics")(
                metric(key="m_name", label="Name", value=self.state.name or "—"),
                metric(key="m_focus", label="Focus", value=self.state.focus),
                metric(key="m_dark", label="Dark", value="Yes" if self.state.dark_mode else "No"),
            ),
        )


class SyncForm(stc.Component):
    """sync_state() is a one-liner shortcut for the most common pattern."""

    class SyncFormState(stc.State):
        city: str = "Paris"
        temp: int = 22
        raining: bool = False

    def render(self):
        return container(key="form", border=True)(
            markdown(key="h")("### sync_state shortcut"),
            markdown(key="desc")(
                "`sync_state(\"field\")` returns a callback that writes the value "
                "into `self.state.field`. One line instead of a full method."
            ),
            text_input(key="city", value=self.state.city, on_change=self.sync_state("city"))("City"),
            slider(key="temp", min_value=-20, max_value=45, value=self.state.temp,
                   on_change=self.sync_state("temp"))("Temperature"),
            toggle(key="rain", value=self.state.raining, on_change=self.sync_state("raining"))("Raining"),
            columns(key="metrics")(
                metric(key="m_city", label="City", value=self.state.city),
                metric(key="m_temp", label="Temp", value=f"{self.state.temp}°C"),
                metric(key="m_rain", label="Rain", value="Yes" if self.state.raining else "No"),
            ),
        )


class CallbacksDemo(stc.Component):
    def render(self):
        return container(key="page")(
            markdown(key="intro")(
                "## Callbacks\n\n"
                "Widget callbacks receive the **current value** as their first argument — "
                "no need to fish it out of `st.session_state`.\n\n"
                "**What to try:** change any widget and watch the metrics and feedback update live."
            ),
            divider(key="d1"),
            columns(key="forms")(
                ProfileForm(key="profile"),
                SyncForm(key="sync"),
            ),
            source_view(__file__),
        )


stc.App(page_title="03 - Callbacks")(CallbacksDemo()).render()
