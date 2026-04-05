"""
Shared Streamlit mock objects used across all test modules.

conftest.py installs _mock_st into sys.modules['streamlit'] before any
st_components import. Test modules that need to configure side effects or
inspect calls import _mock_st and _session_data directly from here.
"""
from unittest.mock import MagicMock
from modict import modict


_session_data = modict()


class MockSessionState:
    def __contains__(self, item):
        return item in _session_data

    def __getitem__(self, key):
        return _session_data[key]

    def __setitem__(self, key, value):
        _session_data[key] = value

    def __delitem__(self, key):
        del _session_data[key]

    def __getattr__(self, name):
        if name in _session_data:
            return _session_data[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        _session_data[name] = value

    def __delattr__(self, name):
        if name in _session_data:
            del _session_data[name]
            return
        raise AttributeError(name)

    def get(self, key, default=None):
        return _session_data.get(key, default)


_mock_st = MagicMock()
_mock_st.session_state = MockSessionState()


def fake_ctx(key):
    """Identity helper: a fake context stack entry is just its key string."""
    return key
