# ASSIGNED TO: AI-3 (structure) + AI-1 (LLM integration)
# Sentiment Agent - analyzes customer emotion from text
# Hybrid approach: keyword-based fast detection + optional LLM refinement

import re
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)

SENTIMENT_PROMPT = """You are a sentiment analysis specialist. Analyze the customer's emotional state."""

# ── Keyword dictionaries for fast sentiment detection ──────────────────────
ANGRY_KEYWORDS = [
    "angry", "furious", "outraged", "livid", "worst", "terrible", "horrible",
    "hate", "disgusted", "unacceptable", "ridiculous", "scam", "fraud",
    "stupid", "useless", "rubbish", "crap", "pathetic"
]

FRUSTRATED_KEYWORDS = [
    "frustrated", "annoyed", "disappointed", "fed up", "sick of", "tired of",
    "again", "still not", "keeps happening", "how many times", "wasting my time"
]

POSITIVE_KEYWORDS = [
    "thank", "thanks", "great", "awesome", "excellent", "perfect", "love",
    "amazing", "wonderful", "fantastic", "appreciate", "helpful", "good job",
    "well done", "happy", "satisfied", "pleased"
]

URGENT_KEYWORDS = [
    "urgent", "emergency", "immediately", "asap", "right now", "critical",
    "can't wait", "deadline", "time sensitive"
]


class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("SentimentAgent", SENTIMENT_PROMPT)

    async def handle(self, query: str, context: dict) -> dict:
        """BaseAgent interface — delegates to analyze()."""
        result = await self.analyze(query)
        return {
            "reply": f"Sentiment detected: {result['sentiment']} (score: {result['score']:.2f})",
            "confidence": result["score"],
            "metadata": result
        }

    async def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of user text.

        Returns:
            {
                "sentiment": "angry" | "frustrated" | "positive" | "urgent" | "neutral",
                "score": 0.0 - 1.0  (intensity of detected emotion),
                "needs_escalation": bool
            }
        """
        msg = text.lower()

        def has_keyword(keywords):
            return any(re.search(r'\b' + re.escape(kw) + r'\b', msg) for kw in keywords)

        def count_keywords(keywords):
            return sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', msg))

        # Check for uppercase shouting (e.g., "THIS IS UNACCEPTABLE")
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        is_shouting = uppercase_ratio > 0.5 and len(text) > 10

        # Check for excessive punctuation (e.g., "!!!" or "???")
        has_exclamation_spam = bool(re.search(r'[!?]{3,}', text))

        # Detect sentiment
        if has_keyword(ANGRY_KEYWORDS) or is_shouting:
            angry_count = count_keywords(ANGRY_KEYWORDS)
            score = min(0.95, 0.70 + (angry_count * 0.08))
            if is_shouting:
                score = min(0.98, score + 0.10)
            return {"sentiment": "angry", "score": score, "needs_escalation": True}

        if has_keyword(FRUSTRATED_KEYWORDS):
            frustrated_count = count_keywords(FRUSTRATED_KEYWORDS)
            score = min(0.90, 0.60 + (frustrated_count * 0.10))
            if has_exclamation_spam:
                score = min(0.95, score + 0.10)
            return {"sentiment": "frustrated", "score": score, "needs_escalation": True}

        if has_keyword(URGENT_KEYWORDS):
            return {"sentiment": "urgent", "score": 0.80, "needs_escalation": False}

        if has_keyword(POSITIVE_KEYWORDS):
            positive_count = count_keywords(POSITIVE_KEYWORDS)
            score = min(0.95, 0.70 + (positive_count * 0.08))
            return {"sentiment": "positive", "score": score, "needs_escalation": False}

        # No strong signals → neutral
        return {"sentiment": "neutral", "score": 0.50, "needs_escalation": False}
