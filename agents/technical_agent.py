# ASSIGNED TO: AI-3 (structure) + AI-1 (LLM integration)
# Technical Agent - handles troubleshooting and technical queries

from agents.agent_base import BaseAgent

TECHNICAL_PROMPT = """You are a specialized technical support agent.

Your responsibilities:
- Diagnose technical problems step by step
- Provide clear, jargon-free troubleshooting instructions
- Use knowledge base articles for accurate solutions
- Ask targeted follow-up questions to narrow down issues
- Suggest escalation if the problem is beyond basic troubleshooting

Response style:
- Clear and methodical
- Use numbered steps for troubleshooting
- Explain WHY each step helps
- Keep technical jargon to a minimum
- Always ask the customer to report back after trying the fix
"""


class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("TechnicalAgent", TECHNICAL_PROMPT)

    async def handle(self, query: str, context: dict) -> dict:
        """Handle technical troubleshooting queries using LLM + RAG context."""
        self.log(f"Handling technical query: {query[:80]}...")

        llm_response = await self.call_llm(
            query, context,
            extra_instructions=(
                "You are the technical support agent. Diagnose the customer's technical issue.\n"
                "Provide step-by-step troubleshooting instructions.\n"
                "If the issue seems complex, recommend escalation to a specialist."
            )
        )

        if llm_response:
            return {
                "reply": llm_response,
                "confidence": 0.88,
                "metadata": {"agent": self.name, "used_llm": True}
            }

        # Rule-based fallback
        rag_chunks = context.get("rag_chunks", [])
        if rag_chunks:
            return {
                "reply": (
                    f"Based on our troubleshooting guide:\n\n\"{rag_chunks[0]}\"\n\n"
                    f"Please try these steps and let me know if the issue persists."
                ),
                "confidence": 0.72,
                "metadata": {"agent": self.name, "used_llm": False}
            }

        return {
            "reply": (
                "I'd be happy to help with your technical issue. "
                "Could you please describe the error you're seeing? "
                "Any error messages, screenshots, or steps to reproduce the problem "
                "would help me diagnose it faster."
            ),
            "confidence": 0.65,
            "metadata": {"agent": self.name, "used_llm": False}
        }
