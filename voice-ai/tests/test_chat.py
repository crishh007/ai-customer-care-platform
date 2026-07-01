"""
tests/test_chat.py
------------------
Unit + integration tests for groq_service.py

Run (unit only — no API key needed):
    cd voice-ai
    pytest tests/test_chat.py -v -m "not integration"

Run all (requires GROQ_API_KEY in .env):
    pytest tests/test_chat.py -v
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import pytest
from groq_service import generate_ai_response, get_model_info, GROQ_MODEL

HAS_API_KEY = bool(os.getenv("GROQ_API_KEY"))


# ---------------------------------------------------------------------------
# Unit Tests — Input validation (no API call)
# ---------------------------------------------------------------------------


class TestGenerateAiResponseValidation:
    """Input validation — no API key or network required."""

    def test_empty_text_fails(self):
        result = generate_ai_response("")
        assert result["success"] is False
        assert result["error"] is not None

    def test_whitespace_only_fails(self):
        result = generate_ai_response("   ")
        assert result["success"] is False

    def test_result_has_required_keys(self):
        result = generate_ai_response("")
        for key in ("success", "response", "model", "usage", "error"):
            assert key in result, f"Missing key: {key}"

    def test_result_defaults(self):
        result = generate_ai_response("")
        assert result["response"] == ""
        assert result["usage"] == {}


class TestGetModelInfo:
    def test_returns_dict(self):
        info = get_model_info()
        assert isinstance(info, dict)

    def test_has_model_key(self):
        info = get_model_info()
        assert "model" in info
        assert isinstance(info["model"], str)
        assert len(info["model"]) > 0

    def test_has_api_key_set_key(self):
        info = get_model_info()
        assert "api_key_set" in info
        assert isinstance(info["api_key_set"], bool)

    def test_api_key_set_reflects_env(self):
        info = get_model_info()
        assert info["api_key_set"] == HAS_API_KEY


# ---------------------------------------------------------------------------
# Integration Tests — Real Groq API calls
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.skipif(not HAS_API_KEY, reason="GROQ_API_KEY not set in .env")
class TestGenerateAiResponseLive:
    """Live API tests — require GROQ_API_KEY."""

    def test_basic_response(self):
        result = generate_ai_response("Say hello in one short sentence.")
        assert result["success"] is True, f"API call failed: {result['error']}"
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0

    def test_model_name_returned(self):
        result = generate_ai_response("What is 2 + 2?")
        assert result["success"] is True
        assert result["model"] != ""

    def test_token_usage_returned(self):
        result = generate_ai_response("What is the capital of France?")
        assert result["success"] is True
        usage = result["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        assert usage["total_tokens"] > 0

    def test_customer_care_prompt(self):
        result = generate_ai_response(
            "My order hasn't arrived yet. It's been 10 days. Can you help?"
        )
        assert result["success"] is True
        assert len(result["response"]) > 10

    def test_conversation_history(self):
        history = [
            {"role": "user", "content": "My name is Alex."},
            {"role": "assistant", "content": "Hello Alex! How can I help you today?"},
        ]
        result = generate_ai_response("Do you remember my name?", conversation_history=history)
        assert result["success"] is True
        # The model should reference "Alex" in a multi-turn context
        assert isinstance(result["response"], str)

    def test_response_not_empty(self):
        result = generate_ai_response("Tell me a joke in one sentence.")
        assert result["success"] is True
        assert result["response"].strip() != ""
