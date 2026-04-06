import importlib.util
from pathlib import Path


def _package_root(package_name: str) -> Path:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise RuntimeError(f"Could not resolve installed package {package_name!r}.")
    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations)))
    if spec.origin is None:
        raise RuntimeError(f"Could not resolve installed package {package_name!r}.")
    return Path(spec.origin).resolve().parent


def examples_join(*parts: str) -> Path:
    return _package_root("examples").joinpath(*parts)
