"""
Invisible audio autoplay via a Streamlit v2 component.

Provides ``play_audio(audio)`` — a fire-and-forget helper that plays audio
in the browser without any visible UI.  Works from callbacks, effects,
or render methods.

::

    from st_components.elements.media import play_audio

    # bytes or BytesIO
    play_audio(audio_bytes)
    play_audio(audio_bytes, format="mp3", volume=0.5)

    # With blocking wait
    play_audio(tts_bytes, wait=True)
"""
import base64
import io

import streamlit as st

# ── JS bridge ────────────────────────────────────────────────────────────────

_JS = """
export default function({ parentElement, data }) {
    if (!data || !data.src) return;

    const root = parentElement instanceof ShadowRoot
        ? parentElement.host : parentElement;
    if (!root) return;

    // Hide the component completely
    Object.assign(root.style, {
        display: 'none', height: '0', width: '0',
        overflow: 'hidden', position: 'absolute'
    });

    const container = root.closest('[data-testid="stElementContainer"]')
        || root.parentElement;
    if (container && container.style) {
        Object.assign(container.style, {
            display: 'none', height: '0', overflow: 'hidden'
        });
    }

    // Create or reuse audio element
    let audio = root.querySelector('audio[data-autoplay]');
    if (!audio) {
        audio = document.createElement('audio');
        audio.setAttribute('data-autoplay', '1');
        audio.setAttribute('preload', 'auto');
        audio.setAttribute('playsinline', '');
        Object.assign(audio.style, {
            display: 'none', position: 'absolute',
            width: '0', height: '0', opacity: '0'
        });
        root.appendChild(audio);
    }

    if (audio.src !== data.src) {
        audio.src = data.src;
        audio.load();
    }

    audio.volume = Math.max(0, Math.min(1, data.volume ?? 1.0));

    const attemptPlay = async () => {
        try {
            await audio.play();
        } catch (err) {
            // Autoplay blocked — unlock on next user interaction
            const unlock = () => {
                audio.play().catch(() => {});
                document.removeEventListener('click', unlock);
                document.removeEventListener('touchstart', unlock);
            };
            document.addEventListener('click', unlock, { once: true });
            document.addEventListener('touchstart', unlock, { once: true });
        }
    };

    if (audio.readyState >= 3) {
        attemptPlay();
    } else {
        audio.addEventListener('canplay', () => attemptPlay(), { once: true });
    }
}
"""

_component = None
_counter = 0


def _get_component():
    global _component
    if _component is None:
        _component = st.components.v2.component(
            "_stc_autoplay",
            js=_JS,
        )
    return _component


# ── MIME detection ───────────────────────────────────────────────────────────

_SIGNATURES = {
    b"\\xff\\xfb": "audio/mpeg",
    b"\\xff\\xf3": "audio/mpeg",
    b"\\xff\\xf2": "audio/mpeg",
    b"ID3": "audio/mpeg",
    b"RIFF": "audio/wav",
    b"OggS": "audio/ogg",
    b"fLaC": "audio/flac",
}


def _guess_mime(data: bytes, fallback="audio/wav") -> str:
    """Guess MIME type from magic bytes."""
    for sig, mime in _SIGNATURES.items():
        if data[:len(sig)] == sig:
            return mime
    if len(data) > 4 and data[4:8] == b"ftyp":
        return "audio/mp4"
    return fallback


# ── Public API ───────────────────────────────────────────────────────────────

_FORMAT_TO_MIME = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "opus": "audio/opus",
    "webm": "audio/webm",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
    "aac": "audio/aac",
}


def play_audio(
    audio,
    *,
    format=None,
    volume=1.0,
    wait=False,
    wait_lag=0.25,
):
    """Play audio in the browser without any visible UI.

    Args:
        audio:    ``bytes``, ``BytesIO``, file path (``str`` or ``Path``),
                  or ``None``.
        format:   Audio format hint (``"mp3"``, ``"wav"``, etc.).
                  Auto-detected from magic bytes or file extension if ``None``.
        volume:   Playback volume, 0.0 to 1.0.
        wait:     If ``True``, block until estimated playback completes.
        wait_lag: Extra seconds to add when *wait* is True.

    ::

        play_audio(tts_bytes)
        play_audio("alert.mp3")
        play_audio(Path("sounds/ding.wav"), volume=0.5)
        play_audio(response_audio, wait=True)
    """
    if audio is None:
        return

    from pathlib import Path

    # File path → read bytes + infer format from extension
    if isinstance(audio, (str, Path)):
        path = Path(audio)
        if format is None:
            ext = path.suffix.lstrip(".")
            if ext in _FORMAT_TO_MIME:
                format = ext
        audio = path.read_bytes()

    if isinstance(audio, io.BytesIO):
        audio.seek(0)
        audio = audio.read()

    if not isinstance(audio, bytes):
        raise TypeError(f"play_audio expects bytes, BytesIO, or file path, got {type(audio)}")

    # Determine MIME type
    if format is not None:
        mime = _FORMAT_TO_MIME.get(format.lower(), f"audio/{format}")
    else:
        mime = _guess_mime(audio)

    # Encode and render the invisible component
    b64 = base64.b64encode(audio).decode("ascii")
    src = f"data:{mime};base64,{b64}"

    global _counter
    _counter += 1

    _get_component()(
        data={"src": src, "volume": float(volume)},
        key=f"_stc_play_{_counter}",
    )

    if wait is not False and wait is not None:
        from ...core.rerun import wait as rerun_wait
        if isinstance(wait, (int, float)) and wait is not True:
            # Explicit duration
            rerun_wait(float(wait) + wait_lag)
        else:
            # Estimate: ~1 second per 16KB at 128kbps
            rerun_wait(max(0.5, len(audio) / 16000) + wait_lag)
