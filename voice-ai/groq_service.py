"""
groq_service.py
---------------
Groq LLM integration for AI-powered responses.
Uses the latest free Llama model available on Groq.
API key is loaded from the .env file via python-dotenv.
"""

import os
import logging
from typing import Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

# Best free model on Groq as of 2024-2025 — update if Groq adds newer ones
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = os.getenv(
    "GROQ_SYSTEM_PROMPT",
    (
        "You are a helpful, friendly, and concise AI customer care assistant. "
        "Answer user questions clearly and professionally. "
        "Keep responses under 150 words unless more detail is genuinely needed. "
        "If you don't know something, say so honestly."
    ),
)

# ---------------------------------------------------------------------------
# Client — lazy-initialised so missing key gives a clear error at call time
# ---------------------------------------------------------------------------
_CLIENT: Optional[Groq] = None


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        if not GROQ_API_KEY:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file and restart the server."
            )
        _CLIENT = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client initialised (model=%s)", GROQ_MODEL)
    return _CLIENT


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ai_response(
    text: str,
    conversation_history: Optional[list[dict]] = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> dict:
    """
    Generate an AI response for *text* using the Groq LLM.

    Parameters
    ----------
    text                 : User's input text.
    conversation_history : Optional list of prior messages
                           [{"role": "user"|"assistant", "content": str}, …]
                           Pass None or [] for a single-turn interaction.
    max_tokens           : Maximum response tokens (default 512).
    temperature          : Sampling temperature 0–1 (default 0.7).

    Returns
    -------
    dict
        {
            "success": bool,
            "response": str,        # AI reply text (empty on error)
            "model": str,           # model used
            "usage": dict,          # token usage stats
            "error": str | None
        }
    """
    result = {
        "success": False,
        "response": "",
        "model": GROQ_MODEL,
        "usage": {},
        "error": None,
    }

    # ── Input validation ────────────────────────────────────────────────────
    if not text or not text.strip():
        result["error"] = "Input text must not be empty."
        logger.error(result["error"])
        return result

    # ── Build message list ──────────────────────────────────────────────────
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation_history:
        # Validate and append each history message
        for msg in conversation_history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": text.strip()})

    # ── Call Groq API ───────────────────────────────────────────────────────
    try:
        logger.info("Calling Groq API | model=%s | tokens≤%d", GROQ_MODEL, max_tokens)
        client = _get_client()

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )

        ai_text = completion.choices[0].message.content.strip()
        usage = {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        }

        result.update(
            {
                "success": True,
                "response": ai_text,
                "model": completion.model,
                "usage": usage,
            }
        )
        logger.info(
            "Groq response received | completion_tokens=%d | %.80s…",
            usage["completion_tokens"],
            ai_text,
        )

    except EnvironmentError as exc:
        result["error"] = str(exc)
        logger.error(result["error"])

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Groq API error: {type(exc).__name__}: {exc}"
        logger.exception("Error calling Groq API")

    return result


def get_model_info() -> dict:
    """Return current model and system prompt configuration."""
    return {
        "model": GROQ_MODEL,
        "system_prompt": SYSTEM_PROMPT,
        "api_key_set": bool(GROQ_API_KEY),
    }
