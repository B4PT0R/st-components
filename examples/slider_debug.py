"""
Minimal debug example: slider + visual feedback via ref.

Run:
    streamlit run examples/slider_debug.py
"""
from st_components import App, Component, Ref, get_state
from st_components.elements import metric, slider, container, subheader


class SliderWidget(Component):
    def __init__(self, **props):
        super().__init__(**props)
        self.slider_ref = Ref()

    def render(self):
        return container(key="box", border=True)(
            subheader(key="h")("Slider"),
            slider(
                key="s",
                ref=self.slider_ref,
                min_value=0,
                max_value=100,
                value=50,
            )("Value"),
            Feedback(key="feedback", slider_ref=self.slider_ref),
        )


class Feedback(Component):
    def render(self):
        slider_ref = self.props.get("slider_ref")
        state = get_state(slider_ref)
        current = state.output if state is not None else "?"
        return metric(key="m", label="Reported by get_state(ref).output", value=current)


App()(SliderWidget(key="app")).render()
