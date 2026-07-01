"""
tests/test_stt.py
-----------------
Unit tests for speech_to_text.py

Run:
    cd voice-ai
    pytest tests/test_stt.py -v
"""

import sys
import os
from pathlib import Path

# Allow importing from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from speech_to_text import transcribe_audio, SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_DIR = Path(__file__).parent / "sample_audio"


def _sample(name: str) -> str:
    return str(SAMPLE_DIR / name)


# ---------------------------------------------------------------------------
# Tests — Error handling (no real audio files needed)
# ---------------------------------------------------------------------------


class TestTranscribeAudioErrors:
    """Tests that verify error handling without requiring real audio."""

    def test_returns_dict(self):
        """transcribe_audio always returns a dict."""
        result = transcribe_audio("/nonexistent/path/audio.wav")
        assert isinstance(result, dict)

    def test_missing_file_returns_failure(self):
        """A non-existent path must return success=False with an error."""
        result = transcribe_audio("/tmp/does_not_exist_xyzzy.wav")
        assert result["success"] is False
        assert result["error"] is not None
        assert result["transcription"] == ""

    def test_unsupported_format_returns_failure(self, tmp_path):
        """A file with an unsupported extension must fail gracefully."""
        bad_file = tmp_path / "audio.xyz"
        bad_file.write_bytes(b"fake data")
        result = transcribe_audio(str(bad_file))
        assert result["success"] is False
        assert "Unsupported" in (result["error"] or "")

    def test_empty_path_string(self):
        """An empty path string must return success=False."""
        result = transcribe_audio("")
        assert result["success"] is False
        assert result["error"] is not None

    def test_result_has_required_keys(self):
        """Result dict always contains all expected keys."""
        result = transcribe_audio("/tmp/fake.wav")
        for key in ("success", "transcription", "language", "language_probability", "segments", "error"):
            assert key in result, f"Missing key: {key}"

    def test_supported_formats_constant(self):
        """SUPPORTED_FORMATS should include common audio types."""
        assert ".wav" in SUPPORTED_FORMATS
        assert ".mp3" in SUPPORTED_FORMATS
        assert ".webm" in SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Tests — Live transcription (only runs if sample files exist)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (SAMPLE_DIR / "sample.wav").exists(),
    reason="sample_audio/sample.wav not found — see README for how to add test audio",
)
class TestTranscribeLive:
    """Live transcription tests — require actual audio files."""

    def test_wav_transcription(self):
        result = transcribe_audio(_sample("sample.wav"))
        assert result["success"] is True
        assert isinstance(result["transcription"], str)
        assert len(result["transcription"]) > 0
        assert result["language"] != ""
        assert 0.0 <= result["language_probability"] <= 1.0

    def test_segments_are_list(self):
        result = transcribe_audio(_sample("sample.wav"))
        assert isinstance(result["segments"], list)

    def test_segment_structure(self):
        result = transcribe_audio(_sample("sample.wav"))
        for seg in result["segments"]:
            assert "start" in seg
            assert "end" in seg
            assert "text" in seg
            assert seg["end"] >= seg["start"]
