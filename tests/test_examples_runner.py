import st_components

from st_components.examples.runner import (
    available_examples,
    build_streamlit_command,
    resolve_example_module,
    resolve_example_path,
)


def test_examples_runner_resolves_known_example():
    assert resolve_example_module("theme_editor") == "examples.theme_editor"
    path = resolve_example_path("theme_editor")
    assert path.name == "theme_editor.py"


def test_examples_runner_lists_expected_examples():
    names = available_examples()
    assert "dashboard" in names
    assert "theme_editor" in names
    assert "multipage" in names


def test_examples_runner_builds_streamlit_command():
    command = build_streamlit_command("basic", ["--server.headless=true"])
    assert command[0]
    assert command[1:4] == ["-m", "streamlit", "run"]
    assert command[-1] == "--server.headless=true"


def test_package_exposes_version():
    assert st_components.__version__ == "0.1.1"
