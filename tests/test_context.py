"""
Tests for KEY() and the context path stack.
"""
from st_components.core import KEY, Context

from tests._mock import fake_ctx


def test_key_no_context():
    assert KEY("foo") == "foo"


def test_key_full_path():
    Context.key_stack[:] = [fake_ctx("a"), fake_ctx("b"), fake_ctx("c")]
    try:
        assert KEY("widget") == "a.b.c.widget"
    finally:
        Context.key_stack.clear()
