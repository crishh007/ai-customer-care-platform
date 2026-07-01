"""
speech_to_text.py
-----------------
Speech-to-Text module using Faster-Whisper (free, offline).
Supports: mp3, wav, webm audio formats.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported audio formats
# ---------------------------------------------------------------------------
SUPPORTED_FORMATS = {".mp3", ".wav", ".webm", ".m4a", ".ogg", ".flac"}

# ---------------------------------------------------------------------------
# Model — loaded once at module level for performance
# ---------------------------------------------------------------------------
# "base" is a solid balance of speed vs accuracy; change to "small" or "medium"
# for higher accuracy if your machine supports it.
_MODEL: Optional[WhisperModel] = None


def _get_model() -> WhisperModel:
    """Lazy-load and cache the Whisper model."""
    global _MODEL
    if _MODEL is None:
        logger.info("Loading Faster-Whisper model (base, cpu)…")
        _MODEL = WhisperModel(
            model_size_or_path="base",
            device="cpu",           # Use "cuda" if a GPU is available
            compute_type="int8",    # int8 is fast & low-memory on CPU
        )
        logger.info("Faster-Whisper model loaded successfully.")
    return _MODEL


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transcribe_audio(audio_file_path: str) -> dict:
    """
    Transcribe an audio file to text using Faster-Whisper.

    Parameters
    ----------
    audio_file_path : str
        Absolute or relative path to the audio file.

    Returns
    -------
    dict
        {
            "success": bool,
            "transcription": str,          # full transcript (empty on error)
            "language": str,               # detected language code, e.g. "en"
            "language_probability": float, # confidence 0–1
            "segments": list[dict],        # word-level segments
            "error": str | None            # error message if success=False
        }

    Raises
    ------
    Does **not** raise — all exceptions are caught and returned as
    ``success=False`` with an ``error`` message.
    """
    result = {
        "success": False,
        "transcription": "",
        "language": "",
        "language_probability": 0.0,
        "segments": [],
        "error": None,
    }

    try:
        # ── Validate path ──────────────────────────────────────────────────
        path = Path(audio_file_path)
        if not path.exists():
            result["error"] = f"Audio file not found: {audio_file_path}"
            logger.error(result["error"])
            return result

        if path.suffix.lower() not in SUPPORTED_FORMATS:
            result["error"] = (
                f"Unsupported format '{path.suffix}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )
            logger.error(result["error"])
            return result

        # ── Transcribe ─────────────────────────────────────────────────────
        logger.info("Transcribing: %s", path.name)
        model = _get_model()

        segments_gen, info = model.transcribe(
            str(path),
            beam_size=5,
            language=None,          # auto-detect
            vad_filter=True,        # skip silence
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        segments_list = []
        full_text_parts = []

        for seg in segments_gen:
            segments_list.append(
                {
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                }
            )
            full_text_parts.append(seg.text.strip())

        transcription = " ".join(full_text_parts).strip()

        result.update(
            {
                "success": True,
                "transcription": transcription,
                "language": info.language,
                "language_probability": round(info.language_probability, 4),
                "segments": segments_list,
            }
        )
        logger.info(
            "Transcription complete. Language=%s (%.0f%%) | Text: %.80s…",
            info.language,
            info.language_probability * 100,
            transcription,
        )

    except FileNotFoundError as exc:
        result["error"] = f"File not found: {exc}"
        logger.exception("FileNotFoundError during transcription")

    except PermissionError as exc:
        result["error"] = f"Permission denied reading file: {exc}"
        logger.exception("PermissionError during transcription")

    except RuntimeError as exc:
        result["error"] = f"Whisper runtime error: {exc}"
        logger.exception("RuntimeError during transcription")

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Unexpected error during transcription: {exc}"
        logger.exception("Unexpected error during transcription")

    return result
