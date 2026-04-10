"""Ref system — path-based handles for navigating and mutating the component tree.

A Ref points to a node (Component or Element) by its fiber path.  It supports:
- Reading state: ``ref.state()``
- Navigating: ``ref.parent``, ``ref["child"]``, ``ref.child``
- Overriding props/children from callbacks: ``ref(color="blue")("new child")``
- Resetting: ``ref.reset()``, ``ref.reset_widget()``
"""
from .access import get_state, reset_element
from .errors import RefError, StcTypeError, UnresolvedRefError


class Ref:
    """Handle for accessing any node in the component tree.

    Supports reading state, overriding props/children from callbacks,
    navigating to the parent, and resetting overrides.

    ::

        # From a component:
        me = self.ref()                    # ref to self
        child = self.ref("panel.results")  # ref to a child

        # Navigate up:
        child.parent                       # ref to "panel"
        child.parent.parent                # ref to the component

        # Override from a callback:
        child("new_child_a", "new_child_b")
        child(color="blue")("styled child")
        child.reset()
    """

    __slots__ = ("path", "kind")

    def __getitem__(self, key):
        """Navigate to a child node by key.

        ::

            ref = self.ref()
            ref["panel"]["results"]        # Ref("app.page.panel.results")
            ref["panel"]["results"]("new") # override children
        """
        path = self._require_path()
        return Ref._from_path(f"{path}.{key}")

    def __getattr__(self, name):
        """Shorthand for ``ref[name]`` — attribute-style navigation.

        Falls back to ``__getitem__`` so it works even if the key collides
        with a Ref method name::

            ref.panel.results          # same as ref["panel"]["results"]
        """
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self[name]
        except RuntimeError:
            raise AttributeError(name)

    def __init__(self):
        self.path = None
        self.kind = None

    @classmethod
    def _from_path(cls, path):
        """Create a resolved Ref from an absolute fiber path."""
        ref = cls()
        ref.path = path
        ref.kind = "component"
        return ref

    def __repr__(self):
        if self.path is None:
            return "Ref(unresolved)"
        return f"Ref({self.path!r})"

    def _resolve(self, path, kind):
        self.path = path
        self.kind = kind

    def _require_path(self):
        if self.path is None:
            raise UnresolvedRefError(
                "Ref is unresolved — attach it to a Component or Element via the ref= prop "
                "and render the tree first."
            )
        return self.path

    # ── Read ─────────────────────────────────────────────────────────────

    def state(self):
        """Return the current state of the referenced node."""
        return get_state(self._require_path())

    @property
    def handle(self):
        """Return the Streamlit container handle, or ``None``."""
        s = self.state()
        return getattr(s, "handle", None) if s else None

    # ── Navigate ─────────────────────────────────────────────────────────

    @property
    def parent(self):
        """Return a Ref to the parent node, or ``None`` for the root."""
        path = self._require_path()
        parts = path.split(".")
        if len(parts) <= 1:
            return None
        return Ref._from_path(".".join(parts[:-1]))

    # ── Override ─────────────────────────────────────────────────────────

    def __call__(self, *children, **props):
        """Override props and/or children on the target's fiber.

        Returns ``self`` for chaining::

            ref(color="blue")(child_a, child_b)
        """
        path = self._require_path()
        from .store import fibers
        fiber = fibers().get(path)
        if fiber is None:
            return self

        overrides = dict(fiber.overrides) if fiber.overrides else {}
        if props:
            overrides["props"] = {**(overrides.get("props") or {}), **props}
        if children:
            overrides["children"] = list(children)
        fiber.overrides = overrides or None
        return self

    def reset(self):
        """Clear all overrides — the target reverts to parent-passed values."""
        path = self._require_path()
        from .store import fibers
        fiber = fibers().get(path)
        if fiber is not None:
            fiber.overrides = None

    def reset_widget(self):
        """Reset an Element's widget value in session_state."""
        path = self._require_path()
        if self.kind != "element":
            raise RefError(
                f"reset_widget() is only available for Element refs, "
                f"but this Ref points to a {self.kind!r} (path={self.path!r})."
            )
        reset_element(path)


def bind_ref(target, path, kind):
    """Resolve a Ref passed via the ``ref=`` prop, binding it to the target's fiber path."""
    ref = target.props.get("ref")
    if ref is not None:
        if not isinstance(ref, Ref):
            raise StcTypeError(f"ref= prop must be a Ref instance, got {type(ref).__name__!r}.")
        ref._resolve(path, kind)
