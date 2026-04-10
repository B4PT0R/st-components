import ast
from pathlib import Path

import st_components
from st_components.utils import examples_join
from st_components import elements

from st_components.examples.runner import (
    available_examples,
    build_streamlit_command,
    resolve_example_module,
    resolve_example_path,
)


def test_examples_runner_resolves_known_example():
    assert resolve_example_module("01_hello") == "examples.01_hello"
    assert resolve_example_module("multipage") == "examples.15_multipage.app"


def test_examples_runner_lists_expected_examples():
    names = available_examples()
    assert "01_hello" in names
    assert "05_elements" in names
    assert "08_hooks" in names
    assert "09_fragments" in names
    assert "10_scoped_rerun" in names
    assert "11_dynamic_rendering" in names
    assert "15_multipage" in names


def test_examples_runner_builds_streamlit_command():
    command = build_streamlit_command("basic", ["--server.headless=true"])
    assert command[0]
    assert command[1:4] == ["-m", "streamlit", "run"]
    assert command[-1] == "--server.headless=true"


def test_package_exposes_version():
    assert isinstance(st_components.__version__, str)
    parts = st_components.__version__.split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts)


def test_examples_join_resolves_packaged_assets():
    iframe_demo = examples_join("assets", "iframe-demo.html")
    logo_demo = examples_join("assets", "demo-logo.svg")

    assert iframe_demo.is_file()
    assert logo_demo.is_file()


def test_elements_example_covers_public_elements():
    module = ast.parse(Path("examples/05_elements.py").read_text())
    primitive_keys = set()
    demo_keys = set()

    for node in ast.walk(module):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "PRIMITIVES" and isinstance(node.value, ast.Call):
                extras = set()
                for arg in node.value.args:
                    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.BitOr):
                        right = arg.right
                        if isinstance(right, ast.Set):
                            extras = {elt.value for elt in right.elts if isinstance(elt, ast.Constant)}
                primitive_keys = (set(elements.__all__) - {"column", "tab"}) | extras
            if isinstance(target, ast.Name) and target.id == "demos" and isinstance(node.value, ast.Dict):
                demo_keys = {key.value for key in node.value.keys if isinstance(key, ast.Constant)}

    supported = set(elements.__all__) - {"column", "tab"}  # sub-elements of columns/tabs

    assert supported <= primitive_keys
    assert supported <= demo_keys
    assert primitive_keys == demo_keys | {"fragment", "progress"}
