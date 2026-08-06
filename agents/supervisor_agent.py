# ASSIGNED TO: AI-1 + AI-2
# Supervisor Agent — Full multi-agent orchestrator
# Routes queries to specialized agents, validates responses, handles re-routing

import re
import os
import logging
from typing import Optional

from agents.agent_base import BaseAgent
from agents.support_agent import SupportAgent
from agents.billing_agent import BillingAgent
from agents.technical_agent import TechnicalAgent
from agents.escalation_agent import EscalationAgent
from agents.sentiment_agent import SentimentAgent
from agents.safety_filter import SafetyFilter

logger = logging.getLogger(__name__)

# ── Configurable Confidence Thresholds ─────────────────────────────────────
# These can be tuned via environment variables without code changes.
CONFIDENCE_HIGH = float(os.getenv("CONFIDENCE_HIGH", "0.85"))
CONFIDENCE_MEDIUM = float(os.getenv("CONFIDENCE_MEDIUM", "0.65"))
CONFIDENCE_LOW = float(os.getenv("CONFIDENCE_LOW", "0.45"))
RE_ROUTE_THRESHOLD = float(os.getenv("RE_ROUTE_THRESHOLD", "0.55"))
MAX_RE_ROUTES = int(os.getenv("MAX_RE_ROUTES", "1"))

# ── Intent Detection Keywords ──────────────────────────────────────────────
INTENT_KEYWORDS = {
    "billing": [
        "pay", "payment", "card", "billing", "invoice", "charge", "price",
        "cost", "subscription", "upgrade", "plan", "visa", "mastercard",
        "amex", "refund", "charged", "deducted", "transaction", "receipt"
    ],
    "technical": [
        "bug", "error", "crash", "crashing", "slow", "broken", "issue",
        "technical", "not working", "loading", "freeze", "update", "install",
        "download", "login error", "page not found", "500 error", "timeout"
    ],
    "account": [
        "password", "reset", "login", "register", "email", "account",
        "signup", "sign in", "profile", "settings", "username", "locked out",
        "verify", "verification", "two factor", "2fa"
    ],
    "greeting": [
        "hi", "hello", "hey", "greet", "greetings", "good morning",
        "good afternoon", "good evening", "howdy", "what's up"
    ],
}


class SupervisorAgent:
    """
    Multi-agent orchestrator that:
    1. Checks input safety
    2. Detects sentiment
    3. Detects intent
    4. Routes to the correct specialized agent
    5. Validates the agent's response
    6. Re-routes if confidence is too low
    7. Checks output safety
    """

    def __init__(self):
        self.support = SupportAgent()
        self.billing = BillingAgent()
        self.technical = TechnicalAgent()
        self.escalation = EscalationAgent()
        self.sentiment_analyzer = SentimentAgent()
        self.safety = SafetyFilter()

        logger.info("SupervisorAgent initialized with all sub-agents")
        logger.info(
            "Confidence thresholds — HIGH: %.2f, MEDIUM: %.2f, LOW: %.2f, RE-ROUTE: %.2f",
            CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW, RE_ROUTE_THRESHOLD
        )

    def detect_intent(self, message: str) -> str:
        """Detect user intent using keyword matching with whole-word boundaries."""
        msg = message.lower()

        def has_keyword(keywords):
            return any(re.search(r'\b' + re.escape(kw) + r'\b', msg) for kw in keywords)

        def keyword_count(keywords):
            return sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', msg))

        # Score each intent by keyword density
        scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            count = keyword_count(keywords)
            if count > 0:
                scores[intent] = count

        if not scores:
            return "general"

        # Return the intent with the most keyword matches
        return max(scores, key=scores.get)

    def select_agent(self, intent: str, sentiment_result: dict) -> BaseAgent:
        """Select the appropriate agent based on intent and sentiment."""
        # Escalation takes priority if sentiment warrants it
        if sentiment_result.get("needs_escalation", False):
            logger.info("Routing to EscalationAgent (sentiment: %s)", sentiment_result["sentiment"])
            return self.escalation

        agent_map = {
            "billing": self.billing,
            "technical": self.technical,
            "account": self.technical,  # Account issues → technical agent
            "greeting": self.support,
            "general": self.support,
        }

        agent = agent_map.get(intent, self.support)
        logger.info("Routing to %s (intent: %s)", agent.name, intent)
        return agent

    def score_confidence(self, agent_result: dict, intent: str,
                          sentiment_result: dict, rag_chunks: list) -> float:
        """
        Calculate a refined confidence score based on multiple signals.

        Factors:
        - Agent's self-reported confidence
        - Whether RAG context was available
        - Sentiment intensity
        - Intent clarity
        """
        base_confidence = agent_result.get("confidence", 0.70)

        # Boost if RAG context supported the response
        if rag_chunks and len(rag_chunks) >= 2:
            base_confidence = min(1.0, base_confidence + 0.05)
        elif not rag_chunks and intent not in ["greeting"]:
            base_confidence = max(0.0, base_confidence - 0.10)

        # Reduce confidence for angry/frustrated sentiments (harder to satisfy)
        if sentiment_result.get("sentiment") in ("angry", "frustrated"):
            base_confidence = max(0.0, base_confidence - 0.15)

        # Boost for clear greetings (easy to handle)
        if intent == "greeting":
            base_confidence = max(base_confidence, 0.90)

        return round(base_confidence, 2)

    async def validate_response(self, result: dict, confidence: float) -> bool:
        """
        Validate an agent's response quality.

        Returns True if the response is acceptable, False if re-routing is needed.
        """
        reply = result.get("reply", "")

        # Empty or very short responses are suspicious
        if not reply or len(reply.strip()) < 10:
            logger.warning("Response too short (%d chars) — may need re-routing", len(reply))
            return False

        # Confidence below re-route threshold
        if confidence < RE_ROUTE_THRESHOLD:
            logger.warning("Confidence %.2f < re-route threshold %.2f", confidence, RE_ROUTE_THRESHOLD)
            return False

        return True

    async def route(self, query: str, context: dict) -> dict:
        """
        Full orchestration pipeline:

        1. Safety check (input)
        2. Sentiment analysis
        3. Intent detection
        4. Agent selection & execution
        5. Response validation (re-route if needed)
        6. Confidence scoring
        7. Safety check (output)
        8. Return final response
        """
        # ── Step 1: Input Safety Check ──────────────────────────────────
        safety_result = self.safety.check_input(query)
        if not safety_result["safe"]:
            logger.warning("Input blocked: reason=%s", safety_result["reason"])
            blocked_reply = self.safety.get_blocked_response(safety_result["reason"])
            return {
                "reply": blocked_reply,
                "sentiment": "neutral",
                "confidence_score": 1.0,
                "agent_used": "safety_filter",
                "intent": "blocked",
                "metadata": {"blocked_reason": safety_result["reason"]}
            }

        cleaned_query = safety_result["filtered_text"]

        # ── Step 2: Sentiment Analysis ──────────────────────────────────
        sentiment_result = await self.sentiment_analyzer.analyze(cleaned_query)
        sentiment = sentiment_result["sentiment"]
        logger.info("Sentiment: %s (score: %.2f, escalation: %s)",
                     sentiment, sentiment_result["score"], sentiment_result["needs_escalation"])

        # ── Step 3: Intent Detection ────────────────────────────────────
        intent = self.detect_intent(cleaned_query)
        logger.info("Intent detected: %s", intent)

        # ── Step 4: Agent Selection & Execution ─────────────────────────
        agent = self.select_agent(intent, sentiment_result)
        rag_chunks = context.get("rag_chunks", [])

        agent_context = {
            **context,
            "sentiment": sentiment,
            "intent": intent,
            "rag_chunks": rag_chunks,
        }

        agent_result = await agent.handle(cleaned_query, agent_context)

        # ── Step 5: Response Validation + Re-routing ────────────────────
        confidence = self.score_confidence(agent_result, intent, sentiment_result, rag_chunks)

        is_valid = await self.validate_response(agent_result, confidence)

        if not is_valid and agent.name != "EscalationAgent":
            logger.info("Re-routing to EscalationAgent (validation failed)")
            agent = self.escalation
            agent_result = await agent.handle(cleaned_query, agent_context)
            confidence = self.score_confidence(agent_result, intent, sentiment_result, rag_chunks)

        # ── Step 6: Output Safety Check ─────────────────────────────────
        output_check = self.safety.check_output(agent_result.get("reply", ""))
        final_reply = output_check["cleaned_text"]  # PII-redacted version

        if output_check["has_hallucination_markers"]:
            logger.warning("Hallucination markers found in response — flagging")

        # ── Step 7: Build Final Response ────────────────────────────────
        # Map sentiment for backward compatibility
        sentiment_map = {
            "angry": "negative",
            "frustrated": "negative",
            "positive": "positive",
            "urgent": "neutral",
            "neutral": "neutral",
        }

        return {
            "reply": final_reply,
            "sentiment": sentiment_map.get(sentiment, "neutral"),
            "confidence_score": confidence,
            "agent_used": agent.name.lower().replace("agent", "_agent"),
            "intent": intent,
            "metadata": {
                "raw_sentiment": sentiment,
                "sentiment_score": sentiment_result["score"],
                "escalated": agent_result.get("metadata", {}).get("escalated", False),
                "requires_human": agent_result.get("metadata", {}).get("requires_human", False),
                "used_llm": agent_result.get("metadata", {}).get("used_llm", False),
                "rag_chunks_count": len(rag_chunks),
                "safety_input_passed": True,
                "safety_output_pii_found": output_check["pii_detected"],
                "hallucination_warning": output_check["has_hallucination_markers"],
            }
        }
