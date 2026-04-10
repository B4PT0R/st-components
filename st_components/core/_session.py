"""
Centralized session_state namespace for st-components.

All keys are prefixed with ``_stc.`` to avoid collisions with user code or
Streamlit internals.  Every module that needs session-persisted data accesses
it through the helpers below — never by touching ``st.session_state`` directly
with a hard-coded key.
"""
from streamlit import session_state as _state


# ── Key catalogue ────────────────────────────────────────────────────────────
# Persistent (survive across reruns, scoped to the Streamlit session):
FIBERS = "_stc.fibers"
SHARED_STATES = "_stc.shared"
WIDGET_REVISIONS = "_stc.widget_revisions"
APP_THEME = "_stc.app.theme"
APP_CSS = "_stc.app.css"
APP_CONFIG = "_stc.app.config"
APP_COLOR_MODE = "_stc.app.color_mode"

CURRENT_APP = "_stc.app.instance"

# Transient (reset each render cycle):
RUNTIME = "_stc.runtime"
PAGE = "_stc.page"
CYCLE_FIBERS = "_stc.cycle.fibers"


# ── Accessors ────────────────────────────────────────────────────────────────

_SENTINEL = object()


def get(key, default=None):
    """Read a value from session_state."""
    return _state.get(key, default)


def get_or_init(key, factory):
    """Return the session_state value at *key*, creating it via *factory()* if absent."""
    val = _state.get(key, _SENTINEL)
    if val is _SENTINEL:
        val = factory()
        _state[key] = val
    return val


def put(key, value):
    """Write a value into session_state."""
    _state[key] = value


def pop(key, default=_SENTINEL):
    """Remove and return a value from session_state."""
    if default is _SENTINEL:
        val = _state[key]
        del _state[key]
        return val
    if key in _state:
        val = _state[key]
        del _state[key]
        return val
    return default


def has(key):
    """Check if a key exists in session_state."""
    return key in _state


def delete(key):
    """Remove a key from session_state if present."""
    if key in _state:
        del _state[key]


def put_or_delete(key, value):
    """Store *value* if not None, otherwise remove the key."""
    if value is None:
        delete(key)
    else:
        _state[key] = value
