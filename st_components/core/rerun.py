"""
Scoped rerun control for st-components apps.

Each scoped fragment maintains its own independent rerun timeline.
``rerun()`` and ``wait()`` automatically target the **current scope**
(read from the context stack via ``rerun_scope``).  Scoped fragments
call ``check_rerun()`` at the end of their own render, and ``App.render()``
calls it for the app scope.

::

    # Inside a scoped fragment:
    rerun(wait=1)       # reruns THIS fragment after 1s
    wait(0.5)           # delays THIS fragment's next rerun

    # Outside any fragment:
    rerun(wait=2)       # reruns the full app after 2s

    # Explicit scope override:
    rerun(scope="app")  # always targets app, even inside a fragment
"""
import time

import streamlit as st

from . import _session as ss


def _key(scope):
    return f"_stc.rerun.{scope}"


def _current_scope():
    """Return the rerun scope from context, or ``'app'``."""
    from .context import ctx as _ctx
    return _ctx.current("rerun_scope", "app")


def _st_rerun(scope):
    """Call the real st.rerun, clearing that scope's pending state.

    Falls back to an app-scope rerun if Streamlit rejects the fragment-scope
    one — which can happen e.g. after a long ``time.sleep()`` in
    ``check_rerun()`` invalidates the current fragment context.
    """
    ss.delete(_key(scope))
    st_scope = "fragment" if scope != "app" else "app"
    kwargs = {"scope": st_scope} if st_scope == "fragment" else {}
    fn = st.rerun._original if hasattr(st.rerun, "_patched") else st.rerun
    try:
        return fn(**kwargs)
    except Exception:
        if kwargs:
            # Fragment-scope rerun rejected — fall back to plain rerun so
            # the app keeps working (slightly wider re-render, but no crash).
            return fn()
        raise


def _merge(scope, delay, requested):
    """Merge a rerun/wait request into the pending state for *scope*."""
    now = time.time()
    key = _key(scope)
    pending = ss.get(key)

    if pending:
        prev_exec_at = pending["requested_at"] + pending["delay"]
        new_exec_at = now + delay
        if new_exec_at > prev_exec_at:
            pending.update(requested_at=now, delay=delay)
        else:
            elapsed = now - pending["requested_at"]
            pending.update(requested_at=now, delay=max(0, pending["delay"] - elapsed))
        if requested:
            pending["requested"] = True
    else:
        ss.put(key, {"requested_at": now, "delay": delay, "requested": requested})


# ── Public API ───────────────────────────────────────────────────────────────

def rerun(scope=None, wait=True):
    """Request a scoped rerun with optional delay.

    *scope* defaults to the current rerun scope from the context stack:
    inside a scoped ``fragment``, that's the fragment; otherwise the app.

    ::

        rerun()                     # current scope, ASAP
        rerun(wait=1.5)             # current scope, after 1.5s
        rerun(scope="app")          # force app scope
        rerun(wait=False)           # immediate hard rerun
    """
    if scope is None:
        scope = _current_scope()

    if wait is False:
        try:
            _st_rerun(scope)
        except Exception:
            rerun(scope=scope, wait=True)
        return

    _merge(scope, 0.0 if wait is True else float(wait), requested=True)


def wait(delay=True, scope=None):
    """Request a minimum delay before the next rerun of the current scope.

    ::

        st.toast("Saved!")
        wait(1.5)           # current scope gets 1.5s
    """
    if scope is None:
        scope = _current_scope()

    if delay is False:
        pending = ss.get(_key(scope))
        if pending and pending.get("requested"):
            _st_rerun(scope)
        return

    if delay is True or delay == 0:
        return

    _merge(scope, float(delay), requested=False)


def check_rerun(scope=None):
    """Execute a pending rerun for *scope* if requested.

    Each scoped fragment calls this at the end of its own render.
    ``App.render()`` calls it for the app scope.

    """
    if scope is None:
        scope = _current_scope()

    pending = ss.get(_key(scope))
    if not pending:
        return

    if pending.get("requested"):
        remaining = pending["delay"] - (time.time() - pending["requested_at"])
        if remaining > 0:
            time.sleep(remaining)
        _st_rerun(scope)
    else:
        ss.delete(_key(scope))
