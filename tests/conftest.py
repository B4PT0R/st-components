"""
Pytest configuration for st_components tests.

Installs the Streamlit mock into sys.modules before any test module is loaded,
so that st_components imports find the mock rather than the real Streamlit.
"""
import sys
import pytest

from tests._mock import _mock_st, _session_data

sys.modules["streamlit"] = _mock_st


@pytest.fixture(autouse=True)
def reset_state():
    """Reset shared mock state before each test."""
    _session_data.clear()
    _mock_st.reset_mock()
