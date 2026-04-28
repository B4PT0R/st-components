import importlib.util
import subprocess
import sys
from pathlib import Path


EXAMPLE_MODULES = {
    # Guided progression (01-17)
    "01_hello": "examples.01_hello",
    "02_state": "examples.02_state",
    "03_callbacks": "examples.03_callbacks",
    "04_composition": "examples.04_composition",
    "05_styles": "examples.05_styles",
    "06_elements": "examples.06_elements",
    "07_functional": "examples.07_functional",
    "08_refs": "examples.08_refs",
    "09_hooks": "examples.09_hooks",
    "10_fragments": "examples.10_fragments",
    "11_scoped_rerun": "examples.11_scoped_rerun",
    "12_dynamic_rendering": "examples.12_dynamic_rendering",
    "13_context": "examples.13_context",
    "14_flow": "examples.14_flow",
    "15_theming": "examples.15_theming",
    "16_multipage": "examples.16_multipage.app",
    "17_full_data_app": "examples.17_full_data_app.app",
    # Legacy aliases
    "basic": "examples.01_hello",
    "styles": "examples.05_styles",
    "elements": "examples.06_elements",
    "primitives": "examples.06_elements",
    "multipage": "examples.16_multipage.app",
    "data_dashboard": "examples.17_full_data_app.app",
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
