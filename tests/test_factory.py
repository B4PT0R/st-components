"""
Tests for element_factory() and the widget_child / widget_props / widget_callback helpers.
"""
import pytest

from st_components.core import Component, ctx, Element, render
from st_components.core.access import widget_key
from st_components.elements.factory import (
    Element as FactoryElement,
    element_factory,
    widget_callback,
    widget_child,
    widget_props,
)

from tests._mock import fake_ctx, _mock_st, _session_data


# ---------------------------------------------------------------------------
# widget_child
# ---------------------------------------------------------------------------

def test_widget_child_returns_first_child_when_present():
    class Wrapper(Component):
        def render(self):
            return _TestElem(key="e")("child_value")

    class _TestElem(Element):
        def render(self):
            self._captured = widget_child("label", "default")

    elem_instances = []

    class Capture(Component):
        def render(self):
            e = _TestElem(key="e")("child_value")
            elem_instances.append(e)
            return e

    ctx.replace("key", [fake_ctx("app")])
    render(Capture(key="cap"))
    ctx.replace("key", [])

    assert elem_instances[0]._captured == "child_value"


def test_widget_child_returns_prop_default_when_no_children():
    class _TestElem(Element):
        def render(self):
            self._captured = widget_child("label", "fallback")

    class Capture(Component):
        def render(self):
            e = _TestElem(key="e", label="from_prop")
            self._elem = e
            return e

    cap = Capture(key="cap")
    ctx.replace("key", [fake_ctx("app")])
    render(cap)
    ctx.replace("key", [])

    assert cap._elem._captured == "from_prop"


def test_widget_child_returns_default_when_no_children_no_prop():
    class _TestElem(Element):
        def render(self):
            self._captured = widget_child("label", "default_val")

    class Capture(Component):
        def render(self):
            e = _TestElem(key="e")
            self._elem = e
            return e

    cap = Capture(key="cap")
    ctx.replace("key", [fake_ctx("app")])
    render(cap)
    ctx.replace("key", [])

    assert cap._elem._captured == "default_val"


# ---------------------------------------------------------------------------
# widget_props
# ---------------------------------------------------------------------------

def test_widget_props_excludes_standard_and_custom():
    class _TestElem(Element):
        def render(self):
            self._captured = dict(widget_props("on_change"))

    class Capture(Component):
        def render(self):
            e = _TestElem(key="e", label="hi", on_change="cb", disabled=True)
            self._elem = e
            return e

    cap = Capture(key="cap")
    ctx.replace("key", [fake_ctx("app")])
    render(cap)
    ctx.replace("key", [])

    props = cap._elem._captured
    assert "key" not in props
    assert "children" not in props
    assert "ref" not in props
    assert "on_change" not in props
    assert props["label"] == "hi"
    assert props["disabled"] is True


# ---------------------------------------------------------------------------
# widget_callback
# ---------------------------------------------------------------------------

def test_widget_callback_returns_none_for_absent_prop():
    class _TestElem(Element):
        def render(self):
            self._captured = widget_callback("on_change")

    class Capture(Component):
        def render(self):
            e = _TestElem(key="e")
            self._elem = e
            return e

    cap = Capture(key="cap")
    ctx.replace("key", [fake_ctx("app")])
    render(cap)
    ctx.replace("key", [])

    assert cap._elem._captured is None


# ---------------------------------------------------------------------------
# widget_child / widget_props raise outside render
# ---------------------------------------------------------------------------

def test_widget_child_raises_outside_render():
    with pytest.raises(RuntimeError, match="widget helpers"):
        widget_child("label")


def test_widget_props_raises_outside_render():
    with pytest.raises(RuntimeError, match="widget helpers"):
        widget_props()


# ---------------------------------------------------------------------------
# element_factory
# ---------------------------------------------------------------------------

def test_element_factory_basic():
    calls = []

    def fake_st_widget(label, key=None, on_change=None, **kwargs):
        calls.append({"label": label, "key": key, **kwargs})
        return "result"

    fake_st_widget.__name__ = "fake_widget"

    WidgetElement = element_factory(
        fake_st_widget,
        child_prop="label",
        callback_prop="on_change",
        default_prop="value",
    )

    assert WidgetElement.__name__ == "fake_widget"
    assert issubclass(WidgetElement, Element)

    # Test _default_output_prop is set
    assert WidgetElement._default_output_prop == "value"


def test_element_factory_no_default_prop():
    def fake_fn(key=None, **kwargs):
        pass

    fake_fn.__name__ = "plain"

    WidgetElement = element_factory(fake_fn, has_key=True)
    assert WidgetElement._default_output_prop is None


def test_element_factory_with_child_prop_tuple():
    calls = []

    def fake_fn(label, key=None, **kwargs):
        calls.append(label)

    fake_fn.__name__ = "labeled"

    WidgetElement = element_factory(fake_fn, child_prop=("label", "Default Label"))

    class Wrapper(Component):
        def render(self):
            return WidgetElement(key="w")

    ctx.replace("key", [fake_ctx("app")])
    render(Wrapper(key="wrap"))
    ctx.replace("key", [])

    assert calls == ["Default Label"]
