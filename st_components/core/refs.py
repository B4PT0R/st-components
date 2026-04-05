from .access import get_element_value, refresh_element
from .store import fibers


class Ref:

    def __init__(self):
        self.path = None
        self.kind = None

    def _resolve(self, path, kind):
        self.path = path
        self.kind = kind

    def _require_path(self):
        if self.path is None:
            raise RuntimeError("Ref is unresolved. Attach it to a Component or Element and render the tree first.")
        return self.path

    def value(self, default=None):
        path = self._require_path()
        if self.kind != "element":
            raise RuntimeError("Ref.value() is only available for Element refs.")
        return get_element_value(path, default)

    def refresh(self):
        path = self._require_path()
        if self.kind != "element":
            raise RuntimeError("Ref.refresh() is only available for Element refs.")
        refresh_element(path)

    def state(self):
        path = self._require_path()
        if self.kind != "component":
            raise RuntimeError("Ref.state() is only available for Component refs.")
        fiber = fibers().get(path)
        if fiber is None:
            raise RuntimeError(f"No mounted component found at ref path {path!r}.")
        return fiber.state

    def get(self, key, default=None):
        return self.state().get(key, default)


def bind_ref(target, path, kind):
    ref = target.props.get("ref")
    if ref is not None:
        if not isinstance(ref, Ref):
            raise TypeError(f"ref must be a Ref instance, got {type(ref)}")
        ref._resolve(path, kind)
