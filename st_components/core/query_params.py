"""
Typed query parameter management via modict.

Wraps ``st.query_params`` with a modict schema so that URL parameters
are coerced to the declared types on read and serialized on write.

::

    class PageParams(QueryParams):
        page: str = "home"
        tab: str = "overview"
        debug: bool = False

    params = app.query_params(PageParams)
    params.page          # "dashboard" (from URL, coerced to str)
    params.debug         # True (from "true" in URL, coerced to bool)
    params.tab = "settings"  # updates URL immediately
"""
import streamlit as st
from modict import modict


class QueryParams(modict):
    """Base class for typed query parameter schemas.

    Subclass to declare expected parameters with types and defaults::

        class MyParams(QueryParams):
            page: str = "home"
            sort: str = "date"
            limit: int = 20
            desc: bool = True
    """
    _config = modict.config(require_all="never")


class _QueryParamsProxy:
    """Live proxy that syncs a modict schema with ``st.query_params``."""

    def __init__(self, schema_cls):
        object.__setattr__(self, "_cls", schema_cls)
        object.__setattr__(self, "_instance", None)

    def _sync(self):
        """Read current URL params and merge into a fresh schema instance."""
        cls = object.__getattribute__(self, "_cls")
        instance = cls()

        # Merge URL values (strings) into the modict — coercion handles types
        try:
            raw = st.query_params.to_dict()
        except Exception:
            raw = {}

        for key, value in raw.items():
            try:
                instance[key] = value
            except (TypeError, KeyError):
                pass  # unknown key or wrong type — skip

        object.__setattr__(self, "_instance", instance)
        return instance

    def _get(self):
        inst = object.__getattribute__(self, "_instance")
        if inst is None:
            inst = self._sync()
        return inst

    def __getattr__(self, name):
        return getattr(self._get(), name)

    def __setattr__(self, name, value):
        inst = self._get()
        inst[name] = value
        # Push to URL
        try:
            st.query_params[name] = value
        except Exception:
            pass

    def __getitem__(self, key):
        return self._get()[key]

    def __setitem__(self, key, value):
        self._get()[key] = value
        try:
            st.query_params[key] = value
        except Exception:
            pass

    def __contains__(self, key):
        return key in self._get()

    def __repr__(self):
        return f"QueryParams({dict(self._get())})"

    def update(self, **kwargs):
        """Update multiple params at once."""
        inst = self._get()
        inst.update(**kwargs)
        try:
            st.query_params.update(**{k: str(v) for k, v in kwargs.items()})
        except Exception:
            pass

    def clear(self):
        """Reset to schema defaults and clear URL params."""
        cls = object.__getattribute__(self, "_cls")
        object.__setattr__(self, "_instance", cls())
        try:
            st.query_params.clear()
        except Exception:
            pass

    def to_dict(self):
        """Return a plain dict of current values."""
        return dict(self._get())


def query_params(schema=None):
    """Create a typed query params proxy.

    Args:
        schema: A :class:`QueryParams` subclass. If ``None``, uses a
                plain ``QueryParams`` (accepts any key).

    ::

        class PageParams(QueryParams):
            page: str = "home"
            tab: str = "overview"

        params = query_params(PageParams)
        params.page       # from URL or default
        params.tab = "x"  # updates URL
    """
    cls = schema or QueryParams
    return _QueryParamsProxy(cls)
