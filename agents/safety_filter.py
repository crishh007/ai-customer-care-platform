# ASSIGNED TO: AI-1
# AI Safety Filter — Input sanitization and output validation
# Prevents: prompt injection, harmful content, PII leaks, hallucination markers

import re
import logging

logger = logging.getLogger(__name__)


# ── Prompt Injection Patterns ──────────────────────────────────────────────
# These patterns detect attempts to override the system prompt or manipulate
# the AI into ignoring its instructions.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?)",
    r"forget\s+(everything|all)\s+(you|about)",
    r"you\s+are\s+now\s+(a|an|the)\s+",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"act\s+as\s+(a|an|if)\s+",
    r"new\s+instruction[s]?\s*:",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"\[\s*INST\s*\]",
    r"override\s+(safety|security|filters?|rules?)",
    r"jailbreak",
    r"DAN\s+mode",
    r"do\s+anything\s+now",
]

# ── Harmful Content Keywords ──────────────────────────────────────────────
# Block queries that request harmful, illegal, or dangerous content.
HARMFUL_KEYWORDS = [
    "how to hack", "how to steal", "how to kill", "make a bomb",
    "illegal drugs", "buy weapons", "child abuse", "exploit children",
    "self harm", "suicide method", "how to hurt",
]

# ── PII Patterns (for output validation) ──────────────────────────────────
# Detect if the AI accidentally outputs sensitive personal information.
PII_PATTERNS = {
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "api_key": r"\b(?:sk-|pk-|api[_-]?key[=:]\s*)[A-Za-z0-9_-]{20,}\b",
}

# ── Hallucination Markers ─────────────────────────────────────────────────
# Phrases that suggest the AI is making things up.
HALLUCINATION_MARKERS = [
    "as an ai language model",
    "i don't have access to real-time",
    "i cannot browse the internet",
    "my training data",
    "as of my last update",
    "i'm just an ai",
    "my knowledge cutoff",
]


class SafetyFilter:
    """
    AI Safety Filter for input sanitization and output validation.

    Input checks:
    - Prompt injection detection
    - Harmful content blocking
    - Input length limits

    Output checks:
    - PII leak detection
    - Hallucination marker detection
    - Response quality validation
    """

    MAX_INPUT_LENGTH = 2000  # characters
    MAX_OUTPUT_LENGTH = 3000  # characters

    @staticmethod
    def check_input(text: str) -> dict:
        """
        Validate user input before processing.

        Returns:
            {
                "safe": bool,
                "reason": str or None,
                "filtered_text": str  (cleaned version)
            }
        """
        if not text or not text.strip():
            return {
                "safe": False,
                "reason": "empty_input",
                "filtered_text": ""
            }

        # Length check
        if len(text) > SafetyFilter.MAX_INPUT_LENGTH:
            logger.warning("Input too long: %d chars (max %d)", len(text), SafetyFilter.MAX_INPUT_LENGTH)
            return {
                "safe": False,
                "reason": "input_too_long",
                "filtered_text": text[:SafetyFilter.MAX_INPUT_LENGTH]
            }

        text_lower = text.lower()

        # Prompt injection check
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning("Prompt injection detected: pattern='%s' in text='%s'", pattern, text[:100])
                return {
                    "safe": False,
                    "reason": "prompt_injection",
                    "filtered_text": text
                }

        # Harmful content check
        for keyword in HARMFUL_KEYWORDS:
            if keyword in text_lower:
                logger.warning("Harmful content detected: keyword='%s'", keyword)
                return {
                    "safe": False,
                    "reason": "harmful_content",
                    "filtered_text": text
                }

        return {
            "safe": True,
            "reason": None,
            "filtered_text": text.strip()
        }

    @staticmethod
    def check_output(text: str) -> dict:
        """
        Validate AI-generated output before sending to user.

        Returns:
            {
                "safe": bool,
                "reason": str or None,
                "pii_detected": list of PII types found,
                "has_hallucination_markers": bool,
                "cleaned_text": str
            }
        """
        if not text:
            return {
                "safe": True,
                "reason": None,
                "pii_detected": [],
                "has_hallucination_markers": False,
                "cleaned_text": ""
            }

        # PII detection
        pii_found = []
        cleaned = text
        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                pii_found.append(pii_type)
                # Redact PII from output
                cleaned = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", cleaned)
                logger.warning("PII detected in output: type=%s, count=%d", pii_type, len(matches))

        # Hallucination marker detection
        text_lower = text.lower()
        has_hallucination = any(marker in text_lower for marker in HALLUCINATION_MARKERS)

        if has_hallucination:
            logger.warning("Hallucination markers detected in AI output")

        # Length check
        if len(text) > SafetyFilter.MAX_OUTPUT_LENGTH:
            cleaned = cleaned[:SafetyFilter.MAX_OUTPUT_LENGTH] + "..."
            logger.warning("Output truncated: %d chars → %d", len(text), SafetyFilter.MAX_OUTPUT_LENGTH)

        is_safe = len(pii_found) == 0  # PII makes it unsafe; hallucination is a warning

        return {
            "safe": is_safe,
            "reason": "pii_leak" if pii_found else None,
            "pii_detected": pii_found,
            "has_hallucination_markers": has_hallucination,
            "cleaned_text": cleaned
        }

    @staticmethod
    def get_blocked_response(reason: str) -> str:
        """Return a safe response when input is blocked."""
        responses = {
            "prompt_injection": (
                "I appreciate your message, but I can only help with customer care questions. "
                "How can I assist you with your account, order, or billing today?"
            ),
            "harmful_content": (
                "I'm not able to help with that type of request. "
                "I'm here to assist with customer care queries — orders, billing, "
                "technical support, and account questions. How can I help?"
            ),
            "empty_input": "It looks like your message was empty. Could you please type your question?",
            "input_too_long": (
                "Your message is quite long. Could you please summarize your question "
                "in a shorter message? I'll do my best to help."
            ),
        }
        return responses.get(reason, "I'm sorry, I couldn't process that request. Please try again.")
