"""
Tests for App lifecycle, Router, multipage routing, and shared state.
"""
from st_components.core import App, Component, fibers, State
from st_components import Page, Router, clear_shared_state, get_shared_state, shared_states

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
