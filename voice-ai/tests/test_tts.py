"""
tests/test_tts.py
-----------------
Unit tests for text_to_speech.py

Run:
    cd voice-ai
    pytest tests/test_tts.py -v
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from text_to_speech import synthesize_speech, list_available_voices, OUTPUTS_DIR


# ---------------------------------------------------------------------------
# Tests — Input validation (no audio hardware needed for error cases)
# ---------------------------------------------------------------------------


class TestSynthesizeSpeechValidation:
    """Validation tests — instant, no audio synthesis required."""

    def test_empty_text_fails(self):
        result = synthesize_speech("")
        assert result["success"] is False
        assert result["error"] is not None

    def test_whitespace_only_fails(self):
        result = synthesize_speech("   \n\t  ")
        assert result["success"] is False
        assert result["error"] is not None

    def test_text_too_long_fails(self):
        result = synthesize_speech("a" * 5001)
        assert result["success"] is False
        assert "5,000" in (result["error"] or "")

    def test_result_has_required_keys(self):
        result = synthesize_speech("")
        for key in ("success", "audio_path", "filename", "text_length", "error"):
            assert key in result, f"Missing key: {key}"

    def test_outputs_dir_exists(self):
        """The outputs directory must be created by the module."""
        assert OUTPUTS_DIR.exists()
        assert OUTPUTS_DIR.is_dir()


# ---------------------------------------------------------------------------
# Tests — Successful synthesis
# ---------------------------------------------------------------------------


class TestSynthesizeSpeechSuccess:
    """Synthesis tests — these actually call pyttsx3 and write a WAV file."""

    def test_short_text_produces_wav(self, tmp_path):
        """Basic synthesis should produce a WAV file on disk."""
        result = synthesize_speech("Hello, this is a test.")
        assert result["success"] is True, f"TTS failed: {result['error']}"
        assert result["audio_path"] != ""
        assert result["filename"].endswith(".wav")
        assert result["text_length"] > 0

        audio_path = Path(result["audio_path"])
        assert audio_path.exists(), "WAV file was not created"
        assert audio_path.stat().st_size > 0, "WAV file is empty"

        # Cleanup
        audio_path.unlink(missing_ok=True)

    def test_custom_filename_used(self):
        result = synthesize_speech("Custom filename test.", filename="my_custom_file")
        assert result["success"] is True, f"TTS failed: {result['error']}"
        assert "my_custom_file" in result["filename"]

        audio_path = Path(result["audio_path"])
        audio_path.unlink(missing_ok=True)

    def test_text_length_recorded(self):
        text = "Hello world from the TTS engine."
        result = synthesize_speech(text)
        assert result["success"] is True
        assert result["text_length"] == len(text)

        audio_path = Path(result["audio_path"])
        audio_path.unlink(missing_ok=True)

    def test_special_characters_in_text(self):
        result = synthesize_speech("Testing punctuation: Hello! How are you? Great, 100%.")
        assert result["success"] is True

        audio_path = Path(result["audio_path"])
        audio_path.unlink(missing_ok=True)

    def test_unicode_text(self):
        result = synthesize_speech("Caf\u00e9 and na\u00efve — simple unicode.")
        # pyttsx3 may or may not handle all unicode well, but should not crash
        assert isinstance(result["success"], bool)
        if result["success"]:
            audio_path = Path(result["audio_path"])
            audio_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Tests — list_available_voices
# ---------------------------------------------------------------------------


class TestListAvailableVoices:
    def test_returns_list(self):
        voices = list_available_voices()
        assert isinstance(voices, list)

    def test_voice_structure(self):
        voices = list_available_voices()
        for v in voices:
            assert "id" in v
            assert "name" in v
            assert "languages" in v
