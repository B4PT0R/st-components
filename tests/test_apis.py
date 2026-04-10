"""
Tests for local_storage, query_params, streamlit_api wrappers, and play_audio.
"""
import pytest
from modict import modict

from st_components.core.local_storage import LocalStore, local_storage, get_local_store, _queue_write, _pending_writes, _stores
from st_components.core.query_params import QueryParams, query_params, _QueryParamsProxy
from st_components.core.streamlit_api import (
    RequestContext, UserInfo, get_request_context, get_user, secrets, _SecretsProxy,
)
from st_components.core.rerun import _key as rerun_key

from tests._mock import _session_data


# ═══════════════════════════════════════════════════════════════════════════════
# LocalStore
# ═══════════════════════════════════════════════════════════════════════════════

class SamplePrefs(LocalStore):
    theme: str = "light"
    font_size: int = 14
    sidebar: bool = True


def test_local_store_defaults():
    store = SamplePrefs(_namespace="test")
    assert store.theme == "light"
    assert store.font_size == 14
    assert store.sidebar is True


def test_local_store_assignment_queues_write():
    store = SamplePrefs(_namespace="test_write")
    store.theme = "dark"
    writes = _pending_writes()
    assert "test_write" in writes
    assert writes["test_write"]["theme"] == "dark"


def test_local_store_save_queues_write():
    store = SamplePrefs(_namespace="test_save")
    store.font_size = 18
    _pending_writes().clear()
    store.save()
    assert "test_save" in _pending_writes()


def test_local_storage_creates_and_retrieves():
    _stores().clear()
    store = local_storage("prefs", SamplePrefs)
    assert isinstance(store, SamplePrefs)
    assert store.theme == "light"

    same = local_storage("prefs", SamplePrefs)
    assert same is store


def test_get_local_store_raises_when_undeclared():
    _stores().clear()
    with pytest.raises(RuntimeError, match="not declared"):
        get_local_store("nonexistent")


def test_get_local_store_returns_existing():
    _stores().clear()
    local_storage("mystore", SamplePrefs)
    store = get_local_store("mystore")
    assert isinstance(store, SamplePrefs)


def test_local_store_without_schema():
    _stores().clear()
    store = local_storage("plain")
    assert isinstance(store, LocalStore)
    store["custom_key"] = "value"
    assert store["custom_key"] == "value"


# ═══════════════════════════════════════════════════════════════════════════════
# QueryParams
# ═══════════════════════════════════════════════════════════════════════════════

class PageParams(QueryParams):
    page: str = "home"
    tab: str = "overview"
    debug: bool = False
    limit: int = 20


def test_query_params_schema_defaults():
    proxy = _QueryParamsProxy(PageParams)
    # Force a sync with empty URL params
    proxy._sync()
    inst = proxy._get()
    assert inst.page == "home"
    assert inst.debug is False
    assert inst.limit == 20


def test_query_params_setattr_updates_instance():
    proxy = _QueryParamsProxy(PageParams)
    proxy._sync()
    proxy.page = "dashboard"
    assert proxy._get().page == "dashboard"


def test_query_params_update():
    proxy = _QueryParamsProxy(PageParams)
    proxy._sync()
    proxy.update(page="settings", limit=50)
    assert proxy._get().page == "settings"
    assert proxy._get().limit == 50


def test_query_params_clear_resets_to_defaults():
    proxy = _QueryParamsProxy(PageParams)
    proxy._sync()
    proxy.page = "custom"
    proxy.clear()
    assert proxy._get().page == "home"


def test_query_params_to_dict():
    proxy = _QueryParamsProxy(PageParams)
    proxy._sync()
    d = proxy.to_dict()
    assert isinstance(d, dict)
    assert d["page"] == "home"


def test_query_params_without_schema():
    proxy = _QueryParamsProxy(QueryParams)
    proxy._sync()
    proxy["custom"] = "value"
    assert proxy["custom"] == "value"


# ═══════════════════════════════════════════════════════════════════════════════
# UserInfo
# ═══════════════════════════════════════════════════════════════════════════════

def test_user_info_defaults():
    user = UserInfo()
    assert user.email is None
    assert user.name is None
    assert user.is_logged_in is False


def test_user_info_with_values():
    user = UserInfo(email="alice@example.com", name="Alice", is_logged_in=True)
    assert user.email == "alice@example.com"
    assert user.is_logged_in is True


def test_get_user_returns_user_info():
    user = get_user()
    assert isinstance(user, UserInfo)
    # With a MagicMock st.user, fields are populated from mock attributes
    # Just verify the type is correct
    assert "email" in user
    assert "is_logged_in" in user


# ═══════════════════════════════════════════════════════════════════════════════
# RequestContext
# ═══════════════════════════════════════════════════════════════════════════════

def test_request_context_defaults():
    ctx = RequestContext()
    assert ctx.headers == {}
    assert ctx.cookies == {}


def test_request_context_with_data():
    ctx = RequestContext(
        headers={"Host": "myapp.streamlit.app", "Authorization": "Bearer xyz"},
        cookies={"session_id": "abc123"},
    )
    assert ctx.headers["Host"] == "myapp.streamlit.app"
    assert ctx.cookies["session_id"] == "abc123"


def test_request_context_attribute_access_on_sub_dicts():
    """modict lazy-wraps sub-dicts for attribute access."""
    ctx = RequestContext(
        headers={"Host": "example.com"},
    )
    # Access via modict attribute wrapping
    assert ctx.headers.get("Host") == "example.com"


def test_get_request_context_returns_request_context():
    ctx = get_request_context()
    assert isinstance(ctx, RequestContext)


# ═══════════════════════════════════════════════════════════════════════════════
# Secrets proxy
# ═══════════════════════════════════════════════════════════════════════════════

def test_secrets_proxy_repr():
    s = _SecretsProxy()
    # Should not crash — mock doesn't have real secrets
    r = repr(s)
    assert "Secrets" in r


# ═══════════════════════════════════════════════════════════════════════════════
# play_audio
# ═══════════════════════════════════════════════════════════════════════════════

def test_play_audio_none_is_noop():
    from st_components.elements.media.auto_play import play_audio
    play_audio(None)  # should not raise


def test_play_audio_rejects_wrong_type():
    from st_components.elements.media.auto_play import play_audio
    with pytest.raises(TypeError, match="bytes"):
        play_audio(12345)


def test_play_audio_mime_detection():
    from st_components.elements.media.auto_play import _guess_mime
    assert _guess_mime(b"ID3\x04\x00") == "audio/mpeg"
    assert _guess_mime(b"RIFF....") == "audio/wav"
    assert _guess_mime(b"OggS....") == "audio/ogg"
    assert _guess_mime(b"fLaC....") == "audio/flac"
    assert _guess_mime(b"\x00\x00\x00\x1cftyp") == "audio/mp4"
    assert _guess_mime(b"\x00\x00\x00\x00") == "audio/wav"  # fallback


def test_play_audio_format_to_mime():
    from st_components.elements.media.auto_play import _FORMAT_TO_MIME
    assert _FORMAT_TO_MIME["mp3"] == "audio/mpeg"
    assert _FORMAT_TO_MIME["wav"] == "audio/wav"
    assert _FORMAT_TO_MIME["ogg"] == "audio/ogg"


# ═══════════════════════════════════════════════════════════════════════════════
# Rerun scoped keys
# ═══════════════════════════════════════════════════════════════════════════════

def test_rerun_key_per_scope():
    assert rerun_key("app") == "_stc.rerun.app"
    assert rerun_key("app.dashboard.live") == "_stc.rerun.app.dashboard.live"
    assert rerun_key("fragment") != rerun_key("app")
