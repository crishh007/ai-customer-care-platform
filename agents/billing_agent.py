# ASSIGNED TO: AI-2 (structure) + AI-1 (LLM integration)
# Billing Agent - handles payment, refund, and subscription queries

from agents.agent_base import BaseAgent

BILLING_PROMPT = """You are a specialized billing and payment support agent.

Your responsibilities:
- Handle payment-related issues with care and precision
- Guide users through billing troubleshooting
- Explain charges, refund policies, and subscription details
- Ask for transaction details when needed (but NEVER ask for full card numbers)
- Be reassuring when customers report payment problems

Security rules:
- NEVER ask for full credit card numbers, CVV, or passwords
- Only reference the last 4 digits of a card if needed
- Direct sensitive payment disputes to the escalation team

Response style:
- Professional and reassuring
- Step-by-step when troubleshooting
- Always confirm next steps clearly
"""


class BillingAgent(BaseAgent):
    def __init__(self):
        super().__init__("BillingAgent", BILLING_PROMPT)

    async def handle(self, query: str, context: dict) -> dict:
        """Handle billing and payment queries using LLM + RAG context."""
        self.log(f"Handling billing query: {query[:80]}...")

        llm_response = await self.call_llm(
            query, context,
            extra_instructions=(
                "You are the billing agent. Help the customer with their payment issue.\n"
                "If they mention a double charge, ask for the transaction date and amount.\n"
                "If they want a refund, explain the refund policy from the knowledge base."
            )
        )

        if llm_response:
            return {
                "reply": llm_response,
                "confidence": 0.90,
                "metadata": {"agent": self.name, "used_llm": True}
            }

        # Rule-based fallback
        return {
            "reply": (
                "I understand you have a billing concern. "
                "We accept Visa, MasterCard, American Express, UPI, and Net Banking. "
                "Could you please confirm whether the payment amount was deducted from your account? "
                "I'll help resolve this right away."
            ),
            "confidence": 0.70,
            "metadata": {"agent": self.name, "used_llm": False}
        }
