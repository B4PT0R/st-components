"""
Tests for App lifecycle, Router, multipage routing, and shared state.
"""
import tomllib

import st_components

from st_components.builtins import (
    Case,
    Conditional,
    Default,
    KeepAlive,
    Match,
    Page,
    Router,
    Switch,
    ThemeEditor,
    ThemeEditorButton,
    ThemeEditorDialog,
)
from st_components.core import App, Component, clear_shared_state, fibers, shared_states, State
from st_components import Config, Props, Theme, get_app, get_shared_state

from tests._mock import _mock_st


def test_app_unmounts_stale_components():
    mount_count = [0]
    unmount_count = [0]

    class Child(Component):
        def component_did_mount(self):
            mount_count[0] += 1

        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if self.props.show_child:
                return Child(key="child")

    App(root=Root(key="root", show_child=True)).render()
    assert "root.child" in fibers()
    assert mount_count[0] == 1
    assert unmount_count[0] == 0

    App(root=Root(key="root", show_child=False)).render()
    assert "root.child" not in fibers()
    assert unmount_count[0] == 1


def test_get_app_returns_current_instance():
    app = App()
    assert get_app() is app


def test_component_sync_state_shortcut():
    class Form(Component):
        class FormState(State):
            name: str = ""

        def render(self):
            return None

    form = Form(key="form")
    sync_name = form.sync_state("name")

    import st_components.core.base as base_module

    original_get_element_value = base_module.get_element_value
    base_module.get_element_value = lambda: "Alice"
    try:
        sync_name()
    finally:
        base_module.get_element_value = original_get_element_value

    assert form.state.name == "Alice"


def test_component_sync_state_accepts_injected_value():
    class Form(Component):
        class FormState(State):
            name: str = ""

        def render(self):
            return None

    form = Form(key="form")
    sync_name = form.sync_state("name")
    sync_name("Bob")

    assert form.state.name == "Bob"


def test_app_set_theme_and_set_css():
    app = App()

    app.set_theme({"primaryColor": "#123456"})
    app.set_css(".x { color: red; }")

    assert isinstance(app.theme, Theme)
    assert app.theme.primaryColor == "#123456"
    assert app.css == ".x { color: red; }"


def test_theme_editor_render_reruns_app_when_local_theme_differs():
    _mock_st.rerun.reset_mock()
    App(theme=Theme(base="light"))
    editor = ThemeEditor(key="editor")
    editor._load_state(Theme(base="light"), "")
    editor.state.editor.update(primaryColor="#123456")

    editor.render()

    _mock_st.rerun.assert_called_once_with(scope="app")


def test_theme_editor_button_opens_and_closes_dialog():
    widget = ThemeEditorButton(key="theme")

    rendered = widget.render()
    dialog_fragment = rendered.children[1]
    assert widget.state.open is False
    assert dialog_fragment.children[0].value is None

    widget._open()
    rendered = widget.render()
    dialog_fragment = rendered.children[1]
    assert widget.state.open is True
    assert dialog_fragment.children[0].props.title == "Theme editor"

    widget._close()
    rendered = widget.render()
    dialog_fragment = rendered.children[1]
    assert widget.state.open is False
    assert dialog_fragment.children[0].value is None


def test_theme_editor_load_preserves_runtime_theme_defaults():
    runtime_options = {
        "theme.base": "dark",
        "theme.primaryColor": "#abcdef",
        "theme.backgroundColor": "#101010",
        "theme.secondaryBackgroundColor": "#202020",
        "theme.textColor": "#f5f5f5",
        "theme.borderColor": "#303030",
        "theme.baseFontSize": 18,
        "theme.baseRadius": "large",
        "theme.buttonRadius": "full",
        "theme.showWidgetBorder": False,
        "theme.sidebar.backgroundColor": "#111111",
    }
    _mock_st.get_option.side_effect = lambda key: runtime_options.get(key)
    try:
        App(theme=None)
        editor = ThemeEditor(key="editor")
        editor._load_state(None, "")

        assert editor.state.editor.base == "dark"
        assert editor.state.editor.primaryColor == "#abcdef"
        assert editor.state.editor.backgroundColor == "#101010"
        assert editor.state.editor.sidebarBackgroundColor == "#111111"
        assert editor.state.editor.baseFontSize == 18
        assert editor.state.editor.showWidgetBorder is False
    finally:
        _mock_st.get_option.side_effect = None


def test_app_set_config():
    app = App()
    app.set_config({"client": {"toolbarMode": "minimal"}})

    assert isinstance(app.config, Config)
    assert app.config.client.toolbarMode == "minimal"


def test_set_theme_does_not_persist_without_save(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    app = App(root=Root(key="root"), persist_theme=False)
    app.set_theme({"primaryColor": "#123456"})
    app.render()

    config_path = tmp_path / ".streamlit" / "config.toml"
    assert not config_path.exists()


def test_save_theme_persists_current_theme(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    app = App(root=Root(key="root"), persist_theme=False)
    app.set_theme({"primaryColor": "#123456"})
    app.save_theme()

    config_path = tmp_path / ".streamlit" / "config.toml"
    config = tomllib.loads(config_path.read_text())
    assert config["theme"]["primaryColor"] == "#123456"


def test_set_config_does_not_persist_without_save(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    app = App(root=Root(key="root"), persist_config=False)
    app.set_config({"client": {"toolbarMode": "minimal"}})
    app.render()

    config_path = tmp_path / ".streamlit" / "config.toml"
    assert not config_path.exists()


def test_save_config_persists_current_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    app = App(root=Root(key="root"), persist_config=False)
    app.set_config({"client": {"toolbarMode": "minimal", "showSidebarNavigation": False}})
    app.save_config()

    config_path = tmp_path / ".streamlit" / "config.toml"
    config = tomllib.loads(config_path.read_text())
    assert config["client"]["toolbarMode"] == "minimal"
    assert config["client"]["showSidebarNavigation"] is False


def test_save_config_persists_runtime_relevant_sections(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    app = App(root=Root(key="root"), persist_config=False)
    app.set_config(
        {
            "runner": {"fastReruns": False},
            "browser": {"gatherUsageStats": False},
            "server": {"runOnSave": True},
        }
    )
    app.save_config()

    config_path = tmp_path / ".streamlit" / "config.toml"
    config = tomllib.loads(config_path.read_text())
    assert config["runner"]["fastReruns"] is False
    assert config["browser"]["gatherUsageStats"] is False
    assert config["server"]["runOnSave"] is True


def test_app_reuses_persisted_theme_and_css_when_not_provided():
    app = App()
    app.set_theme({"primaryColor": "#123456"})
    app.set_css(".x { color: red; }")

    rebound = App()

    assert isinstance(rebound.theme, Theme)
    assert rebound.theme.primaryColor == "#123456"
    assert rebound.css == ".x { color: red; }"

    rebound.set_theme(None)
    rebound.set_css(None)


def test_app_writes_theme_to_config_and_preserves_other_sections(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".streamlit"
    config_dir.mkdir()
    config_path = config_dir / "config.toml"
    config_path.write_text(
        "[server]\nheadless = true\n\n[theme]\ntextColor = \"#111111\"\n"
    )

    class Root(Component):
        def render(self):
            return None

    App(
        root=Root(key="root"),
        theme={
            "primaryColor": "#123456",
            "sidebar": {"backgroundColor": "#eeeeee"},
        },
    ).render()

    config = tomllib.loads(config_path.read_text())
    assert config["server"]["headless"] is True
    assert config["theme"]["primaryColor"] == "#123456"
    assert config["theme"]["sidebar"]["backgroundColor"] == "#eeeeee"
    assert "textColor" not in config["theme"]


def test_app_replaces_theme_section_when_keys_are_removed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".streamlit"
    config_dir.mkdir()
    config_path = config_dir / "config.toml"
    config_path.write_text(
        "[theme]\nprimaryColor = \"#123456\"\nbackgroundColor = \"#ffffff\"\n"
    )

    class Root(Component):
        def render(self):
            return None

    App(
        root=Root(key="root"),
        theme={"primaryColor": "#abcdef"},
    ).render()

    config = tomllib.loads(config_path.read_text())
    assert config["theme"]["primaryColor"] == "#abcdef"
    assert "backgroundColor" not in config["theme"]


def test_app_casts_theme_dict_to_theme():
    app = App(theme={"primaryColor": "#123456"})
    assert isinstance(app.theme, Theme)
    assert app.theme.primaryColor == "#123456"


def test_theme_model_prunes_empty_sections():
    theme = Theme(
        primaryColor="#123456",
        sidebar={"backgroundColor": "#eeeeee"},
        light={},
        dark=None,
        fontFaces=[],
    )
    normalized = Theme(theme)

    assert "primaryColor" in normalized
    assert "sidebar" in normalized
    assert "light" not in normalized
    assert "dark" not in normalized
    assert "fontFaces" not in normalized


def test_theme_model_revalidates_on_assignment():
    theme = Theme(
        primaryColor="#123456",
        sidebar={"backgroundColor": "#eeeeee"},
    )

    theme.sidebar = None
    theme.primaryColor = None
    theme.fontFaces = []

    assert "sidebar" not in theme
    assert "primaryColor" not in theme
    assert "fontFaces" not in theme


def test_config_model_revalidates_on_assignment():
    config = Config(
        client={"toolbarMode": "minimal"},
        runner={"fastReruns": False},
    )

    config.client = None
    config.runner.fastReruns = None

    assert "client" not in config
    assert "fastReruns" not in config.runner


def test_app_accepts_theme_modict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class Root(Component):
        def render(self):
            return None

    App(
        root=Root(key="root"),
        theme=Theme(
            primaryColor="#123456",
            sidebar={"backgroundColor": "#eeeeee"},
        ),
    ).render()

    config_path = tmp_path / ".streamlit" / "config.toml"
    config = tomllib.loads(config_path.read_text())
    assert config["theme"]["primaryColor"] == "#123456"
    assert config["theme"]["sidebar"]["backgroundColor"] == "#eeeeee"


def test_app_injects_css_from_raw_string_and_file(tmp_path):
    css_path = tmp_path / "theme.css"
    css_path.write_text(".file { color: blue; }")

    class Root(Component):
        def render(self):
            return None

    App(
        root=Root(key="root"),
        css=[
            ".raw { color: red; }",
            css_path,
        ],
    ).render()

    _mock_st.html.assert_called_once_with(
        "<style>\n.raw { color: red; }\n\n.file { color: blue; }\n</style>"
    )


def test_app_remounts_after_unmount():
    mount_count = [0]
    unmount_count = [0]

    class Child(Component):
        def component_did_mount(self):
            mount_count[0] += 1

        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if self.props.show_child:
                return Child(key="child")

    App(root=Root(key="root", show_child=True)).render()
    App(root=Root(key="root", show_child=False)).render()
    App(root=Root(key="root", show_child=True)).render()

    assert mount_count[0] == 2
    assert unmount_count[0] == 1
    assert "root.child" in fibers()


def test_flow_components_are_exported_from_builtins_package():
    assert not hasattr(st_components, "Conditional")
    assert not hasattr(st_components, "Case")
    assert not hasattr(st_components, "Page")
    assert not hasattr(st_components, "Router")
    assert not hasattr(st_components, "clear_shared_state")
    assert not hasattr(st_components, "declare_shared_state")
    assert Props is not None
    assert Conditional is not None
    assert Case is not None
    assert Switch is not None
    assert Match is not None
    assert Default is not None
    assert KeepAlive is not None
    assert ThemeEditor is not None
    assert ThemeEditorButton is not None
    assert ThemeEditorDialog is not None
    assert Page is not None
    assert Router is not None


def test_conditional_preserves_hidden_child_state():
    mount_count = [0]
    unmount_count = [0]

    class Child(Component):
        class ChildState(State):
            count: int = 0

        def component_did_mount(self):
            mount_count[0] += 1

        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            return Conditional(key="cond", condition=self.props.show)(
                Child(key="child")
            )

    App(root=Root(key="root", show=True)).render()
    fibers()["root.cond.child"].state.count = 5

    App(root=Root(key="root", show=False)).render()
    assert "root.cond.child" in fibers()
    assert fibers()["root.cond.child"].state.count == 5
    assert mount_count[0] == 1
    assert unmount_count[0] == 0

    App(root=Root(key="root", show=True)).render()
    assert "root.cond.child" in fibers()
    assert fibers()["root.cond.child"].state.count == 5
    assert mount_count[0] == 1
    assert unmount_count[0] == 0


def test_conditional_preserves_both_branches():
    mount_counts = {"left": 0, "right": 0}
    unmount_counts = {"left": 0, "right": 0}

    class Left(Component):
        class LeftState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["left"] += 1

        def component_did_unmount(self):
            unmount_counts["left"] += 1

        def render(self):
            pass

    class Right(Component):
        class RightState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["right"] += 1

        def component_did_unmount(self):
            unmount_counts["right"] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            return Conditional(key="cond", condition=self.props.show_left)(
                Left(key="left"),
                Right(key="right"),
            )

    App(root=Root(key="root", show_left=True)).render()
    fibers()["root.cond.left"].state.count = 2

    App(root=Root(key="root", show_left=False)).render()
    assert "root.cond.left" in fibers()
    assert "root.cond.right" in fibers()
    fibers()["root.cond.right"].state.count = 7

    App(root=Root(key="root", show_left=True)).render()
    assert fibers()["root.cond.left"].state.count == 2
    assert fibers()["root.cond.right"].state.count == 7
    assert mount_counts == {"left": 1, "right": 1}
    assert unmount_counts == {"left": 0, "right": 0}


def test_conditional_hidden_child_unmounts_when_parent_disappears():
    unmount_count = [0]

    class Child(Component):
        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if not self.props.show_conditional:
                return None
            return Conditional(key="cond", condition=self.props.show_child)(
                Child(key="child")
            )

    App(root=Root(key="root", show_conditional=True, show_child=True)).render()
    assert "root.cond.child" in fibers()

    App(root=Root(key="root", show_conditional=True, show_child=False)).render()
    assert "root.cond.child" in fibers()

    App(root=Root(key="root", show_conditional=False, show_child=False)).render()
    assert "root.cond.child" not in fibers()
    assert unmount_count[0] == 1


def test_case_preserves_non_selected_branches():
    mount_counts = {"a": 0, "b": 0, "c": 0}
    unmount_counts = {"a": 0, "b": 0, "c": 0}

    class BranchA(Component):
        class BranchAState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["a"] += 1

        def component_did_unmount(self):
            unmount_counts["a"] += 1

        def render(self):
            pass

    class BranchB(Component):
        class BranchBState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["b"] += 1

        def component_did_unmount(self):
            unmount_counts["b"] += 1

        def render(self):
            pass

    class BranchC(Component):
        class BranchCState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["c"] += 1

        def component_did_unmount(self):
            unmount_counts["c"] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            return Case(key="case", case=self.props.case)(
                BranchA(key="a"),
                BranchB(key="b"),
                BranchC(key="c"),
            )

    App(root=Root(key="root", case=0)).render()
    fibers()["root.case.a"].state.count = 1

    App(root=Root(key="root", case=1)).render()
    fibers()["root.case.b"].state.count = 2

    App(root=Root(key="root", case=2)).render()
    fibers()["root.case.c"].state.count = 3

    App(root=Root(key="root", case=0)).render()
    assert fibers()["root.case.a"].state.count == 1
    assert fibers()["root.case.b"].state.count == 2
    assert fibers()["root.case.c"].state.count == 3
    assert mount_counts == {"a": 1, "b": 1, "c": 1}
    assert unmount_counts == {"a": 0, "b": 0, "c": 0}


def test_case_unmounts_preserved_branches_when_parent_disappears():
    unmount_count = [0]

    class Child(Component):
        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if not self.props.show_case:
                return None
            return Case(key="case", case=self.props.case)(
                Child(key="a"),
                Child(key="b"),
            )

    App(root=Root(key="root", show_case=True, case=0)).render()
    App(root=Root(key="root", show_case=True, case=1)).render()
    assert "root.case.a" in fibers()
    assert "root.case.b" in fibers()

    App(root=Root(key="root", show_case=False, case=1)).render()
    assert "root.case.a" not in fibers()
    assert "root.case.b" not in fibers()
    assert unmount_count[0] == 2


def test_keep_alive_preserves_hidden_child_state():
    mount_count = [0]
    unmount_count = [0]

    class Child(Component):
        class ChildState(State):
            count: int = 0

        def component_did_mount(self):
            mount_count[0] += 1

        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            return KeepAlive(key="keep", active=self.props.active)(
                Child(key="child")
            )

    App(root=Root(key="root", active=True)).render()
    fibers()["root.keep.child"].state.count = 5

    App(root=Root(key="root", active=False)).render()
    assert "root.keep.child" in fibers()
    assert fibers()["root.keep.child"].state.count == 5
    assert mount_count[0] == 1
    assert unmount_count[0] == 0

    App(root=Root(key="root", active=True)).render()
    assert fibers()["root.keep.child"].state.count == 5
    assert mount_count[0] == 1
    assert unmount_count[0] == 0


def test_keep_alive_unmounts_preserved_child_when_parent_disappears():
    unmount_count = [0]

    class Child(Component):
        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if not self.props.show_keep_alive:
                return None
            return KeepAlive(key="keep", active=self.props.active)(
                Child(key="child")
            )

    App(root=Root(key="root", show_keep_alive=True, active=True)).render()
    App(root=Root(key="root", show_keep_alive=True, active=False)).render()
    assert "root.keep.child" in fibers()

    App(root=Root(key="root", show_keep_alive=False, active=False)).render()
    assert "root.keep.child" not in fibers()
    assert unmount_count[0] == 1


def test_switch_preserves_matching_and_default_branches():
    mount_counts = {"loading": 0, "ready": 0, "error": 0}
    unmount_counts = {"loading": 0, "ready": 0, "error": 0}

    class Loading(Component):
        class LoadingState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["loading"] += 1

        def component_did_unmount(self):
            unmount_counts["loading"] += 1

        def render(self):
            pass

    class Ready(Component):
        class ReadyState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["ready"] += 1

        def component_did_unmount(self):
            unmount_counts["ready"] += 1

        def render(self):
            pass

    class Error(Component):
        class ErrorState(State):
            count: int = 0

        def component_did_mount(self):
            mount_counts["error"] += 1

        def component_did_unmount(self):
            unmount_counts["error"] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            return Switch(key="switch", value=self.props.status)(
                Match(key="loading", when="loading")(Loading(key="panel")),
                Match(key="ready", when="ready")(Ready(key="panel")),
                Default(key="default")(Error(key="panel")),
            )

    App(root=Root(key="root", status="loading")).render()
    fibers()["root.switch.loading.panel"].state.count = 1

    App(root=Root(key="root", status="ready")).render()
    fibers()["root.switch.ready.panel"].state.count = 2

    App(root=Root(key="root", status="unknown")).render()
    fibers()["root.switch.default.panel"].state.count = 3

    App(root=Root(key="root", status="loading")).render()
    assert fibers()["root.switch.loading.panel"].state.count == 1
    assert fibers()["root.switch.ready.panel"].state.count == 2
    assert fibers()["root.switch.default.panel"].state.count == 3
    assert mount_counts == {"loading": 1, "ready": 1, "error": 1}
    assert unmount_counts == {"loading": 0, "ready": 0, "error": 0}


def test_switch_unmounts_preserved_branches_when_parent_disappears():
    unmount_count = [0]

    class Child(Component):
        def component_did_unmount(self):
            unmount_count[0] += 1

        def render(self):
            pass

    class Root(Component):
        def render(self):
            if not self.props.show_switch:
                return None
            return Switch(key="switch", value=self.props.status)(
                Match(key="a", when="a")(Child(key="child")),
                Default(key="default")(Child(key="child")),
            )

    App(root=Root(key="root", show_switch=True, status="a")).render()
    App(root=Root(key="root", show_switch=True, status="b")).render()
    assert "root.switch.a.child" in fibers()
    assert "root.switch.default.child" in fibers()

    App(root=Root(key="root", show_switch=False, status="b")).render()
    assert "root.switch.a.child" not in fibers()
    assert "root.switch.default.child" not in fibers()
    assert unmount_count[0] == 2


def test_switch_rejects_invalid_children():
    class Root(Component):
        def render(self):
            return Switch(key="switch", value="x")(
                Component(key="invalid"),
            )

    try:
        App(root=Root(key="root")).render()
    except TypeError as err:
        assert "Match or Default" in str(err)
    else:
        raise AssertionError("Expected Switch to reject non-Match children")


def test_app_page_config_single_page():
    class Root(Component):
        def render(self):
            return None

    App(
        root=Root(key="root"),
        page_title="Single page",
        page_icon=":material/dashboard:",
        layout="wide",
    ).render()

    _mock_st.set_page_config.assert_called_with(
        page_title="Single page",
        page_icon=":material/dashboard:",
        layout="wide",
    )


def test_app_multipage_inline_component():
    navigation_calls = []

    class FakeStreamlitPage:
        def __init__(self, source, **kwargs):
            self._source = source
            self.title = kwargs.get("title") or ""
            self.icon = kwargs.get("icon") or ""
            self.url_path = "" if kwargs.get("default") else (kwargs.get("url_path") or self.title.lower())
            self.visibility = kwargs.get("visibility", "visible")

        def run(self):
            if callable(self._source):
                return self._source()
            raise AssertionError("Expected callable page source for inline page")

    def fake_page(source, **kwargs):
        return FakeStreamlitPage(source, **kwargs)

    def fake_navigation(pages, **kwargs):
        navigation_calls.append((pages, kwargs))
        return pages[1]

    _mock_st.Page.side_effect = fake_page
    _mock_st.navigation.side_effect = fake_navigation

    class Home(Component):
        def render(self):
            return None

    class Settings(Component):
        def render(self):
            return None

    app = App(
        page_title="Demo app",
        page_icon=":material/dashboard:",
        layout="wide",
    )(
        Router(position="top")(
            Page(key="home", nav_title="Home", default=True)(Home(key="root")),
            Page(key="settings", nav_title="Settings", page_title="Settings page")(Settings(key="root")),
        )
    )
    app.render(position="top")

    assert navigation_calls[0][1] == {"position": "top", "expanded": False}
    _mock_st.set_page_config.assert_called_with(
        page_title="Settings page",
        page_icon=":material/dashboard:",
        layout="wide",
    )
    assert "page[settings].root" in fibers()
    assert "page[home].root" not in fibers()


def test_app_multipage_file_page_namespace():
    file_registry = {}

    class FakeStreamlitPage:
        def __init__(self, source, **kwargs):
            self._source = source
            self.title = kwargs.get("title") or ""
            self.icon = kwargs.get("icon") or ""
            self.url_path = "" if kwargs.get("default") else (kwargs.get("url_path") or self.title.lower())
            self.visibility = kwargs.get("visibility", "visible")

        def run(self):
            if isinstance(self._source, str):
                return file_registry[self._source]()
            return self._source()

    def fake_page(source, **kwargs):
        return FakeStreamlitPage(source, **kwargs)

    def fake_navigation(pages, **kwargs):
        return pages[0]

    _mock_st.Page.side_effect = fake_page
    _mock_st.navigation.side_effect = fake_navigation

    class SettingsRoot(Component):
        def render(self):
            return None

    file_registry["pages/settings.py"] = lambda: App.render_page(SettingsRoot(key="root"))

    app = App(page_title="Demo app")(
        Router()(
            Page(key="settings", nav_title="Settings")("pages/settings.py")
        )
    )
    app.render()

    _mock_st.set_page_config.assert_called_with(page_title="Demo app")
    assert "page[settings].root" in fibers()


def test_router_rejects_non_page_children():
    try:
        Router()(Component(key="oops"))
    except TypeError as err:
        assert "Page children" in str(err)
    else:
        raise AssertionError("Expected Router to reject non-Page children")


def test_router_rejects_global_page_config_props():
    try:
        Router(page_title="Demo app")
    except TypeError as err:
        assert "Pass them to App" in str(err)
    else:
        raise AssertionError("Expected Router to reject global page config props")


def test_app_shared_state_persists():
    class WorkspaceState(State):
        team: str = "Core"
        focus: int = 7

    app = App()
    app.shared_state("workspace", WorkspaceState())

    shared = get_shared_state("workspace")
    assert isinstance(shared, State)
    assert shared.team == "Core"
    assert shared.focus == 7

    shared.focus = 9

    same = get_shared_state("workspace")
    assert same is shared
    assert same.focus == 9
    assert same.team == "Core"


def test_app_shared_state_accepts_class():
    class ShellState(State):
        team: str = "Core"
        show_code: bool = True

    App().shared_state("shell", ShellState)

    shared = get_shared_state("shell")
    assert isinstance(shared, ShellState)
    assert shared.team == "Core"
    assert shared.show_code is True


def test_get_shared_state_requires_declaration():
    try:
        get_shared_state("missing")
    except RuntimeError as err:
        assert "not declared" in str(err)
    else:
        raise AssertionError("Expected get_shared_state() to fail for an undeclared namespace")


def test_clear_shared_state():
    App().shared_state("workspace", State(team="Core"))
    App().shared_state("auth", State(user="baptiste"))

    clear_shared_state("workspace")
    assert "workspace" not in shared_states()
    assert "auth" in shared_states()

    clear_shared_state()
    assert dict(shared_states()) == {}
