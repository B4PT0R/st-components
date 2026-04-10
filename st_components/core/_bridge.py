"""Bridge between the component model and the Streamlit rendering API.

This module is the **only** place where the component layer (base.py, store.py)
calls Streamlit rendering functions.  Keeping these calls here rather than
scattered across model code makes it easy to:

- audit the coupling surface between the component engine and Streamlit,
- swap or mock the renderer for testing or alternative backends,
- evolve alongside Streamlit API changes without touching model internals.

Everything else in ``core/`` accesses Streamlit only through ``_session.py``
(for session_state persistence) — never for rendering.
"""
import streamlit as st


def write(obj):
    """Render a plain Python object via ``st.write()``."""
    st.write(obj)


def get_widget_value(widget_key):
    """Read a raw widget value from ``st.session_state``.

    Returns ``None`` if the key is not registered.
    """
    return st.session_state.get(widget_key)
