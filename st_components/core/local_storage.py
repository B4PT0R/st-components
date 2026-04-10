"""
Browser localStorage persistence via a Streamlit v2 component bridge.

Provides typed, modict-backed namespaces that persist in the browser's
``localStorage``.  Each namespace is a modict subclass — fields define the
schema, types, and defaults.  Values are serialized as JSON and coerced
back through modict on read.

::

    class UserPrefs(LocalStore):
        theme: str = "light"
        sidebar_open: bool = True
        font_size: int = 14

    prefs = local_storage("prefs", UserPrefs)
    prefs.theme           # "dark" (read from localStorage, coerced to str)
    prefs.theme = "light" # writes to localStorage immediately
    prefs.save()          # explicit flush (also happens on each assignment)

The bridge component is invisible (zero-height HTML) and communicates
bidirectionally via ``setStateValue`` / ``setTriggerValue``.
"""
import json

import streamlit as st
from modict import modict

from . import _session as ss
from .errors import LocalStoreError

# ── JS bridge ────────────────────────────────────────────────────────────────

_BRIDGE_JS = """
export default function({ parentElement, data, setStateValue }) {
    const ns = data.namespace;
    const prefix = data.prefix || "_stc.";
    const storageKey = prefix + ns;

    // Handle write commands from Python
    if (data.command === "write") {
        localStorage.setItem(storageKey, JSON.stringify(data.payload));
        setStateValue("ack", { namespace: ns, written: true });
        return;
    }

    if (data.command === "delete") {
        localStorage.removeItem(storageKey);
        setStateValue("ack", { namespace: ns, deleted: true });
        return;
    }

    // Default: read and return current value
    const raw = localStorage.getItem(storageKey);
    let parsed = null;
    try {
        parsed = raw ? JSON.parse(raw) : null;
    } catch (e) {
        parsed = null;
    }
    setStateValue("data", { namespace: ns, value: parsed });
}
"""

_bridge = None


def _get_bridge():
    global _bridge
    if _bridge is None:
        _bridge = st.components.v2.component(
            "_stc_local_storage",
            js=_BRIDGE_JS,
            html="",
            css="div { display: none; }",
        )
    return _bridge


# ── Session cache for pending writes ─────────────────────────────────────────

_WRITES_KEY = "_stc.local_storage.writes"


def _pending_writes():
    return ss.get_or_init(_WRITES_KEY, dict)


# ── LocalStore base class ────────────────────────────────────────────────────

class LocalStore(modict):
    """Typed, modict-backed namespace persisted in browser localStorage.

    Subclass to declare your schema::

        class UserPrefs(LocalStore):
            theme: str = "light"
            sidebar_open: bool = True
            font_size: int = 14

    Then use :func:`local_storage` to instantiate and sync::

        prefs = local_storage("prefs", UserPrefs)
        prefs.theme = "dark"   # queues a write
    """
    _config = modict.config(require_all="never")

    def __init__(self, *args, _namespace=None, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_ls_namespace", _namespace)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        # Queue a write to localStorage on any field change
        ns = object.__getattribute__(self, "_ls_namespace")
        if ns is not None and not key.startswith("_"):
            _queue_write(ns, self)

    def save(self):
        """Explicitly flush the current state to localStorage."""
        ns = object.__getattribute__(self, "_ls_namespace")
        if ns is not None:
            _queue_write(ns, self)


def _queue_write(namespace, store):
    """Queue a write — flushed to the browser by ``render_local_storage()``."""
    writes = _pending_writes()
    # Serialize only the public fields
    writes[namespace] = {k: v for k, v in store.items() if not k.startswith("_")}


# ── Public API ───────────────────────────────────────────────────────────────

_STORES_KEY = "_stc.local_storage.stores"


def _stores():
    return ss.get_or_init(_STORES_KEY, dict)


def local_storage(namespace, schema=None):
    """Declare a typed localStorage namespace (creates if absent).

    Same pattern as ``declare_shared_state``::

        app.create_local_store("prefs", UserPrefs)

    Args:
        namespace: String key. Stored under ``_stc.<namespace>`` in the browser.
        schema:    A :class:`LocalStore` subclass. ``None`` → plain ``LocalStore``.

    Returns:
        The live ``LocalStore`` instance.
    """
    if not isinstance(namespace, str):
        from .errors import StcTypeError
        raise StcTypeError(
            f"Local store namespace must be a str, got {type(namespace).__name__!r}."
        )
    stores = _stores()
    if namespace in stores:
        return stores[namespace]

    cls = schema or LocalStore
    if not (isinstance(cls, type) and issubclass(cls, LocalStore)):
        from .errors import StcTypeError
        raise StcTypeError(
            f"Local store schema must be a LocalStore subclass, got {type(cls).__name__!r}."
        )
    store = cls(_namespace=namespace)
    stores[namespace] = store
    return store


def get_local_store(namespace):
    """Return an existing localStorage namespace.

    Raises ``RuntimeError`` if the namespace was not declared.
    Same pattern as ``get_shared_state``::

        prefs = get_local_store("prefs")
        prefs.theme = "dark"
    """
    stores = _stores()
    if namespace not in stores:
        raise LocalStoreError(
            f"Local store {namespace!r} is not declared. "
            f"Declare it first with app.create_local_store({namespace!r}, MyStoreSchema)."
        )
    return stores[namespace]


def render_local_storage():
    """Render the invisible localStorage bridge components.

    Call this once in your app (``App.render()`` calls it automatically).
    It handles:
    1. Reading stored values from the browser into the Python stores
    2. Flushing pending writes to the browser
    """
    bridge = _get_bridge()
    stores = _stores()
    writes = _pending_writes()

    # For each registered store, render a read bridge
    for namespace, store in stores.items():
        if namespace in writes:
            # Pending write — send it to the browser
            payload = writes.pop(namespace)
            bridge(
                data={"namespace": namespace, "command": "write", "payload": payload},
                default={"ack": None},
                key=f"_stc_ls_w_{namespace}",
            )
        else:
            # Read from browser
            result = bridge(
                data={"namespace": namespace, "command": "read"},
                default={"data": None},
                key=f"_stc_ls_r_{namespace}",
            )
            if result and hasattr(result, "data") and result.data:
                browser_data = result.data
                if isinstance(browser_data, dict) and browser_data.get("value"):
                    # Merge browser values into the store (modict coerces types)
                    for k, v in browser_data["value"].items():
                        if k in store or not hasattr(type(store), k):
                            store[k] = v


def clear_local_storage(namespace):
    """Delete a namespace from browser localStorage."""
    bridge = _get_bridge()
    bridge(
        data={"namespace": namespace, "command": "delete"},
        default={"ack": None},
        key=f"_stc_ls_d_{namespace}",
    )
    stores = _stores()
    if namespace in stores:
        del stores[namespace]
