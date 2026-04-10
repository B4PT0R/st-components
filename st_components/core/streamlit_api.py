"""
Thin wrappers around Streamlit runtime APIs, exposed on App.

These don't add logic — they just provide a consistent, modict-typed
access point for Streamlit features that live outside the component tree.
"""
import streamlit as st
from modict import modict


# ── Secrets ──────────────────────────────────────────────────────────────────

class _SecretsProxy:
    """Read-only proxy to ``st.secrets`` with attribute access.

    ::

        app.secrets.openai_api_key     # reads [openai_api_key]
        app.secrets["db"]["host"]      # nested TOML sections
        app.secrets.to_dict()          # full snapshot as dict
    """

    def __getattr__(self, name):
        try:
            return st.secrets[name]
        except Exception as e:
            raise AttributeError(f"Secret {name!r} not found") from e

    def __getitem__(self, key):
        return st.secrets[key]

    def __contains__(self, key):
        try:
            st.secrets[key]
            return True
        except Exception:
            return False

    def get(self, key, default=None):
        try:
            return st.secrets[key]
        except Exception:
            return default

    def to_dict(self):
        """Return all secrets as a plain dict."""
        try:
            return dict(st.secrets)
        except Exception:
            return {}

    def __repr__(self):
        return f"Secrets({list(self.to_dict().keys())})"


secrets = _SecretsProxy()


# ── User ─────────────────────────────────────────────────────────────────────

class UserInfo(modict):
    """Typed snapshot of the current Streamlit Cloud user.

    Available when the app runs on Streamlit Cloud with auth enabled.
    All fields are ``None`` when running locally or without auth.
    """
    _config = modict.config(require_all="never")

    email: str | None = None
    name: str | None = None
    is_logged_in: bool = False


def get_user() -> UserInfo:
    """Return the current user info as a typed modict.

    ::

        user = app.user
        user.email         # "alice@example.com" or None
        user.is_logged_in  # True / False
    """
    try:
        raw = st.user
        return UserInfo(
            email=getattr(raw, "email", None),
            name=getattr(raw, "name", None),
            is_logged_in=getattr(raw, "is_logged_in", False),
        )
    except Exception:
        return UserInfo()


# ── Auth ─────────────────────────────────────────────────────────────────────

def login(provider="google", **kwargs):
    """Trigger Streamlit Cloud login.

    ::

        app.login()                    # default provider
        app.login(provider="google")
    """
    try:
        st.login(provider=provider, **kwargs)
    except AttributeError:
        raise RuntimeError(
            "st.login() is not available in this Streamlit version. "
            "Requires Streamlit Cloud with auth enabled."
        )


def logout():
    """Trigger Streamlit Cloud logout.

    ::

        app.logout()
    """
    try:
        st.logout()
    except AttributeError:
        raise RuntimeError(
            "st.logout() is not available in this Streamlit version. "
            "Requires Streamlit Cloud with auth enabled."
        )


# ── Cache helpers ────────────────────────────────────────────────────────────
# Re-export Streamlit's cache decorators for convenience — no wrapping needed,
# but having them on App keeps the API surface consistent.

cache_data = st.cache_data
cache_resource = st.cache_resource


# ── Connection ───────────────────────────────────────────────────────────────

def connection(name, type=None, **kwargs):
    """Create or retrieve a Streamlit connection.

    Thin wrapper around ``st.connection()``::

        db = app.connection("mydb", type="sql")
        df = db.query("SELECT * FROM users")
    """
    return st.connection(name, type=type, **kwargs)


# ── Stop ─────────────────────────────────────────────────────────────────────

def stop():
    """Stop script execution immediately.

    ::

        if not app.user.is_logged_in:
            st.warning("Please log in.")
            app.stop()
    """
    st.stop()


# ── Context ──────────────────────────────────────────────────────────────────

class RequestContext(modict):
    """Typed snapshot of the Streamlit runtime request context.

    Sub-dicts are lazy-wrapped by modict — full attribute access at any depth::

        ctx = app.request_context
        ctx.headers.Host            # "myapp.streamlit.app"
        ctx.cookies.session_id      # "abc123"
    """
    _config = modict.config(require_all="never")

    headers: dict = modict.factory(dict)
    cookies: dict = modict.factory(dict)


def get_request_context() -> RequestContext:
    """Return the current Streamlit request context as a typed modict."""
    try:
        raw = st.context
        return RequestContext(
            headers=dict(getattr(raw, "headers", {})),
            cookies=dict(getattr(raw, "cookies", {})),
        )
    except Exception:
        return RequestContext()
