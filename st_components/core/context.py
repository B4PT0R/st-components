"""
Centralized render context — ContextOrchestrator + Context modict.

The :class:`Context` modict defines the schema, types, defaults, and stores
the actual stacks.  The :class:`ContextOrchestrator` wraps it with push/pop/
current helpers and session_state persistence.

The modict config on Context controls admissibility of keys:

- Default / ``extra="allow"`` → dynamic stacks accepted
- ``extra="forbid"`` → only declared fields are valid in set_context
- ``extra="ignore"`` → unknown keys silently dropped

Fields are typed as ``list[T]`` — they ARE the stacks.  Defaults set the
initial state on ``reset()``::

    class Context(modict):
        key: list[str] = modict.factory(list)                          # empty
        callback: list[CallbackState] = modict.factory(lambda: [CallbackState()])  # one default
"""
from contextlib import contextmanager

from modict import modict

from . import _session as ss


# ── Data models ──────────────────────────────────────────────────────────────

class CallbackState(modict):
    """Callback context: element path and widget key active during a widget callback."""
    element_path: str | None = None
    widget_key: str | None = None


class Context(modict):
    """Render context schema and storage.

    Each field is a **stack** (list).  The orchestrator pushes/pops values
    onto these lists.  Type annotations document what each stack holds.
    Factories set the initial state on ``reset()``.

    The modict ``_config`` controls whether unknown keys are accepted::

        class StrictContext(Context):
            _config = modict.config(require_all="never", extra="forbid")
            # only declared fields are valid in set_context()
    """
    _config = modict.config(require_all="never")

    key: list = modict.factory(list)
    component: list = modict.factory(list)
    callback: list[CallbackState] = modict.factory(lambda: [CallbackState()])
    page: list = modict.factory(list)


class CurrentContext(modict):
    """Read-only snapshot of the active context.

    Every stack appears as an attribute holding its top value::

        c = get_context()
        c.key          # "panel"
        c.component    # <Panel …>
        c.key_stack    # ["app", "dashboard", "panel"]
        c.element_path # "app.dashboard.panel"
    """
    _config = modict.config(require_all="never")


# ── Orchestrator ─────────────────────────────────────────────────────────────

class ContextOrchestrator:
    """Wraps a :class:`Context` modict with push/pop/current operations.

    The Context instance lives in session_state and is cached locally.
    On ``reset()``, a fresh Context is created from the class defaults.

    Parameters
    ----------
    context_class : type[Context]
        The modict class to use as schema and storage.
    """

    __slots__ = ("_cache", "_cls")

    def __init__(self, context_class=Context):
        object.__setattr__(self, "_cache", None)
        object.__setattr__(self, "_cls", context_class)

    def _context(self) -> Context:
        """Return the live Context modict (cached)."""
        cached = self._cache
        if cached is not None:
            return cached
        c = ss.get_or_init(ss.RUNTIME, self._cls)
        object.__setattr__(self, "_cache", c)
        return c

    def _invalidate(self):
        object.__setattr__(self, "_cache", None)

    def reset(self):
        """Replace the context with a fresh instance (defaults from schema)."""
        ss.put(ss.RUNTIME, self._cls())
        self._invalidate()

    # ── Stack operations ─────────────────────────────────────────────────

    def push(self, name: str, value):
        """Push *value* onto the named stack."""
        ctx = self._context()
        stack = ctx.get(name)
        if isinstance(stack, list):
            stack.append(value)
        else:
            ctx[name] = [value]

    def pop(self, name: str):
        """Pop the top value from the named stack."""
        stack = self._context().get(name)
        return stack.pop() if isinstance(stack, list) and stack else None

    def current(self, name: str, default=None):
        """Return the current (top) value, or *default*."""
        stack = self._context().get(name)
        return stack[-1] if isinstance(stack, list) and stack else default

    def replace(self, name: str, values: list) -> list:
        """Replace an entire stack.  Returns the previous content."""
        ctx = self._context()
        previous = ctx.get(name, [])
        ctx[name] = list(values)
        return previous if isinstance(previous, list) else []

    def stack(self, name: str) -> list:
        """Return a reference to the named stack (created if absent)."""
        ctx = self._context()
        s = ctx.get(name)
        if not isinstance(s, list):
            s = []
            ctx[name] = s
        return s

    def snapshot(self) -> dict[str, object]:
        """Return ``{name: top_value}`` for every non-empty named stack.

        Internal stacks (context provider values keyed by ``context:*``)
        are excluded — use :func:`get_context_value` to read those.
        """
        return {
            name: stack[-1]
            for name, stack in self._context().items()
            if isinstance(stack, list) and stack and not name.startswith("context:")
        }


# ── Module-level singleton ───────────────────────────────────────────────────

ctx = ContextOrchestrator(context_class=Context)


def _reset_runtime_context():
    """Reset all context stacks.  Called by ``begin_render_cycle()``."""
    ctx.reset()


# ── Public API ───────────────────────────────────────────────────────────────

_UNSET = object()


@contextmanager
def set_context(**kwargs):
    """Push values onto named context stacks for the duration of the block.

    - ``key``  — pushed onto the key stack.
    - ``keys`` — **replaces** the entire key stack (restored on exit).
    - Any other name — pushed onto the corresponding stack.

    Admissibility of keys is governed by the Context modict's config
    (``extra="forbid"`` rejects unknown keys, default accepts them).

    ``callback`` dicts are auto-wrapped in :class:`CallbackState`.
    """
    keys_val = kwargs.pop("keys", _UNSET)
    key_val = kwargs.pop("key", _UNSET)

    prev_keys = None
    pushed_key = False
    pushed = []

    try:
        if keys_val is not _UNSET:
            prev_keys = list(ctx.stack("key"))
            ctx.replace("key", list(keys_val))

        if key_val is not _UNSET:
            ctx.push("key", key_val)
            pushed_key = True

        for name, value in kwargs.items():
            if name == "callback" and isinstance(value, dict) and not isinstance(value, CallbackState):
                value = CallbackState(value)
            ctx.push(name, value)
            pushed.append(name)

        yield

    finally:
        for name in reversed(pushed):
            ctx.pop(name)
        if pushed_key:
            ctx.pop("key")
        if prev_keys is not None:
            ctx.replace("key", prev_keys)


def get_context() -> CurrentContext:
    """Return a snapshot of all active context stacks."""
    snap = ctx.snapshot()
    key_stack = list(ctx.stack("key"))
    callback = snap.get("callback")
    snap["key_stack"] = key_stack
    snap["element_path"] = (
        ".".join(key_stack) if key_stack
        else (callback.element_path if isinstance(callback, CallbackState) else None)
    )
    return CurrentContext(snap)


# ── Context value scopes (ContextData providers) ─────────────────────────────
# Provider values are just named stacks keyed by context._id — same mechanism.

@contextmanager
def context_value_scope(context, value):
    """Push a provider value onto the context's stack."""
    ctx.push(context._id, value)
    try:
        yield value
    finally:
        ctx.pop(context._id)


def get_context_value(context):
    """Return the nearest provider's value, or the context's default."""
    return ctx.current(context._id, context.default)


# ── Query helpers ────────────────────────────────────────────────────────────

def get_key_stack():
    """Return a copy of the current key stack (list of ancestor keys)."""
    return list(ctx.stack("key"))


def get_active_page_namespace():
    """Return the active Page namespace, or ``None`` outside a page."""
    return ctx.current("page")


def get_rendering_component():
    """Return the Component/Element currently being rendered, or ``None``."""
    return ctx.current("component")


def get_element_path():
    """Return the dotted element path from the key stack, or from the callback context."""
    stack = ctx.stack("key")
    if stack:
        return ".".join(stack)
    cb = ctx.current("callback")
    return cb.element_path if isinstance(cb, CallbackState) else None


def KEY(key):
    """Build the full dotted fiber path by appending *key* to the current stack."""
    return ".".join([*ctx.stack("key"), key])


def reset_context_runtime():
    """Public alias for ``_reset_runtime_context()``."""
    _reset_runtime_context()
