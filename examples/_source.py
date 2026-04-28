from pathlib import Path

from st_components.elements import code, expander


def source_view(path, *, key="source", label="View source"):
    return expander(key=key, label=label, expanded=False)(
        code(key="code", language="python")(Path(path).read_text(encoding="utf-8"))
    )
