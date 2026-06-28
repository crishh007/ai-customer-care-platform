# ASSIGNED TO: AI-3 (structure) + AI-1 (LLM integration)
# Escalation Agent - handles angry customers and unresolvable issues
# Decides when to transfer to a human agent

import os
from agents.agent_base import BaseAgent

ESCALATION_PROMPT = """You are a specialized escalation agent for handling frustrated or upset customers.

Your responsibilities:
- Stay calm, empathetic, and professional at all times
- Acknowledge the customer's frustration sincerely
- Apologize for the inconvenience
- Focus on what CAN be done to help
- Offer to connect with a human agent if needed
- NEVER argue, deflect blame, or make excuses

Response style:
- Lead with empathy ("I understand how frustrating this must be...")
- Apologize sincerely
- Offer a concrete next step
- Keep the tone warm but professional
- 3-5 sentences maximum
"""

# Configurable thresholds (via env vars)
ESCALATION_CONFIDENCE_THRESHOLD = float(os.getenv("ESCALATION_CONFIDENCE_THRESHOLD", "0.60"))
ESCALATION_SENTIMENTS = {"angry", "frustrated", "negative"}


class EscalationAgent(BaseAgent):
    def __init__(self):
        super().__init__("EscalationAgent", ESCALATION_PROMPT)

    def should_escalate(self, confidence: float, sentiment: str, intent: str = "") -> bool:
        """
        Determine if a query should be escalated to a human agent.

        Rules:
        - Confidence below threshold → escalate
        - Negative/angry sentiment → escalate
        - Repeated failures (future: check chat history) → escalate
        """
        if confidence < ESCALATION_CONFIDENCE_THRESHOLD:
            self.log(f"Escalation triggered: confidence {confidence:.2f} < {ESCALATION_CONFIDENCE_THRESHOLD}")
            return True

        if sentiment.lower() in ESCALATION_SENTIMENTS:
            self.log(f"Escalation triggered: sentiment='{sentiment}'")
            return True

        return False

    async def handle(self, query: str, context: dict) -> dict:
        """Handle escalation — de-escalate with empathy, offer human handoff."""
        self.log(f"Handling escalation for: {query[:80]}...")

        llm_response = await self.call_llm(
            query, context,
            extra_instructions=(
                "The customer is frustrated or the previous response was inadequate.\n"
                "Lead with empathy, apologize sincerely, and offer to connect them with "
                "a human support specialist. Do NOT try to solve the technical problem — "
                "just de-escalate and hand off."
            )
        )

        if llm_response:
            return {
                "reply": llm_response,
                "confidence": 0.50,
                "metadata": {
                    "agent": self.name,
                    "used_llm": True,
                    "escalated": True,
                    "requires_human": True
                }
            }

        # Rule-based fallback
        return {
            "reply": (
                "I sincerely apologize for the inconvenience you're experiencing. "
                "I can see this is frustrating, and I want to make sure you get the best help possible. "
                "I'm connecting you with a human support specialist who can resolve this for you directly. "
                "Your case has been flagged as priority."
            ),
            "confidence": 0.45,
            "metadata": {
                "agent": self.name,
                "used_llm": False,
                "escalated": True,
                "requires_human": True
            }
        }
