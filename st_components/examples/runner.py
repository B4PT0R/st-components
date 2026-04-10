import importlib.util
import subprocess
import sys
from pathlib import Path


EXAMPLE_MODULES = {
    # Guided progression (01-16)
    "01_hello": "examples.01_hello",
    "02_state": "examples.02_state",
    "03_callbacks": "examples.03_callbacks",
    "04_composition": "examples.04_composition",
    "05_elements": "examples.05_elements",
    "06_functional": "examples.06_functional",
    "07_refs": "examples.07_refs",
    "08_hooks": "examples.08_hooks",
    "09_fragments": "examples.09_fragments",
    "10_scoped_rerun": "examples.10_scoped_rerun",
    "11_dynamic_rendering": "examples.11_dynamic_rendering",
    "12_context": "examples.12_context",
    "13_flow": "examples.13_flow",
    "14_theming": "examples.14_theming",
    "15_multipage": "examples.15_multipage.app",
    "16_full_data_app": "examples.16_full_data_app.app",
    # Legacy aliases
    "basic": "examples.01_hello",
    "elements": "examples.05_elements",
    "primitives": "examples.05_elements",
    "multipage": "examples.15_multipage.app",
    "data_dashboard": "examples.16_full_data_app.app",
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
