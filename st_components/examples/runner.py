import importlib.util
import subprocess
import sys
from pathlib import Path


EXAMPLE_MODULES = {
    "basic": "examples.basic",
    "dashboard": "examples.dashboard",
    "data_dashboard": "examples.data_dashboard",
    "flow": "examples.flow",
    "functional": "examples.functional",
    "functional_typed": "examples.functional_typed",
    "multipage": "examples.multipage.app",
    "primitives": "examples.primitives",
    "theme_editor": "examples.theme_editor",
    "typed_props": "examples.typed_props",
    "typed_state": "examples.typed_state",
}


def available_examples():
    return sorted(EXAMPLE_MODULES)


def resolve_example_module(name):
    try:
        return EXAMPLE_MODULES[name]
    except KeyError as exc:
        available = ", ".join(available_examples())
        raise ValueError(f"Unknown example {name!r}. Available examples: {available}") from exc


def resolve_example_path(name):
    module_name = resolve_example_module(name)
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        raise RuntimeError(f"Could not resolve installed example module {module_name!r}.")
    return Path(spec.origin)


def build_streamlit_command(name, extra_args=None):
    extra_args = list(extra_args or ())
    return [sys.executable, "-m", "streamlit", "run", str(resolve_example_path(name)), *extra_args]


def run_example(name, extra_args=None):
    return subprocess.call(build_streamlit_command(name, extra_args))
