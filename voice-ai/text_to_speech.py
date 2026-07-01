"""
text_to_speech.py
-----------------
Text-to-Speech module using pyttsx3 (fully offline, no API key needed).
Saves synthesized audio to the outputs/ directory as WAV files.
"""

import os
import uuid
import logging
import threading
from pathlib import Path
from typing import Optional

import pyttsx3

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# pyttsx3 is NOT thread-safe; use a lock when synthesizing.
# ---------------------------------------------------------------------------
_TTS_LOCK = threading.Lock()


def _build_engine(rate: int = 175, volume: float = 1.0) -> pyttsx3.Engine:
    """
    Create and configure a fresh pyttsx3 engine.

    Parameters
    ----------
    rate   : words-per-minute (default 175)
    volume : 0.0 – 1.0 (default 1.0)
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    # Try to pick the first available English voice
    voices = engine.getProperty("voices")
    for voice in voices:
        if "english" in voice.name.lower() or "en" in (voice.id or "").lower():
            engine.setProperty("voice", voice.id)
            break

    return engine


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize_speech(
    text: str,
    filename: Optional[str] = None,
    rate: int = 175,
    volume: float = 1.0,
) -> dict:
    """
    Convert *text* to speech and save it as a WAV file inside ``outputs/``.

    Parameters
    ----------
    text     : The text to synthesize.
    filename : Optional output filename (without extension).
               If omitted, a UUID-based name is generated.
    rate     : Speech rate in words-per-minute (default 175).
    volume   : Volume level 0.0–1.0 (default 1.0).

    Returns
    -------
    dict
        {
            "success": bool,
            "audio_path": str,   # absolute path to WAV file (empty on error)
            "filename": str,     # basename of the WAV file
            "text_length": int,  # number of characters synthesized
            "error": str | None
        }

    Notes
    -----
    All exceptions are caught and returned as ``success=False``.
    """
    result = {
        "success": False,
        "audio_path": "",
        "filename": "",
        "text_length": 0,
        "error": None,
    }

    # ── Input validation ────────────────────────────────────────────────────
    if not text or not text.strip():
        result["error"] = "Text must not be empty."
        logger.error(result["error"])
        return result

    text = text.strip()

    if len(text) > 5_000:
        result["error"] = "Text exceeds the 5,000-character limit."
        logger.error(result["error"])
        return result

    # ── Determine output path ───────────────────────────────────────────────
    stem = filename or f"tts_{uuid.uuid4().hex}"
    # Sanitise: keep only alphanumeric, dash, and underscore
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)
    output_path = OUTPUTS_DIR / f"{safe_stem}.wav"

    # ── Synthesize (thread-safe) ────────────────────────────────────────────
    try:
        with _TTS_LOCK:
            logger.info("Synthesizing %d chars → %s", len(text), output_path.name)
            engine = _build_engine(rate=rate, volume=volume)

            # save_to_file works reliably across platforms for WAV output
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            engine.stop()

        # Verify the file was actually written
        if not output_path.exists() or output_path.stat().st_size == 0:
            result["error"] = "TTS engine ran but produced no output file."
            logger.error(result["error"])
            return result

        result.update(
            {
                "success": True,
                "audio_path": str(output_path.resolve()),
                "filename": output_path.name,
                "text_length": len(text),
            }
        )
        logger.info("Speech saved: %s (%.1f KB)", output_path.name, output_path.stat().st_size / 1024)

    except RuntimeError as exc:
        result["error"] = f"pyttsx3 runtime error: {exc}"
        logger.exception("RuntimeError during TTS synthesis")

    except OSError as exc:
        result["error"] = f"OS error writing audio file: {exc}"
        logger.exception("OSError during TTS synthesis")

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Unexpected TTS error: {exc}"
        logger.exception("Unexpected error during TTS synthesis")

    return result


def list_available_voices() -> list[dict]:
    """
    Return metadata for all TTS voices installed on the current system.

    Returns
    -------
    list[dict]
        Each dict: {"id": str, "name": str, "languages": list[str]}
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.stop()
        return [
            {
                "id": v.id,
                "name": v.name,
                "languages": list(v.languages) if v.languages else [],
            }
            for v in voices
        ]
    except Exception as exc:  # noqa: BLE001
        logger.exception("Could not list voices: %s", exc)
        return []
