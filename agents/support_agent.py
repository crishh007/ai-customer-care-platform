# ASSIGNED TO: AI-2 (structure) + AI-1 (LLM integration)
# General Support Agent - handles common customer queries
# Covers: order status, product info, general help, greetings

from agents.agent_base import BaseAgent

SUPPORT_PROMPT = """You are a friendly and professional customer support agent.

Your responsibilities:
- Answer general customer questions clearly and accurately
- Help with order status, product information, and account queries
- Keep responses concise and easy to understand
- Ask follow-up questions if the user's request is unclear
- Maintain a warm, supportive tone throughout

Response style:
- Human-like and conversational
- 2-4 sentences maximum for simple queries
- Use bullet points for multi-step instructions
- Always end with an offer to help further
"""


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupportAgent", SUPPORT_PROMPT)

    async def handle(self, query: str, context: dict) -> dict:
        """Handle general support queries using LLM + RAG context."""
        self.log(f"Handling query: {query[:80]}...")

        # Try LLM first
        llm_response = await self.call_llm(
            query, context,
            extra_instructions="You are the general support agent. Answer the customer's question helpfully."
        )

        if llm_response:
            return {
                "reply": llm_response,
                "confidence": 0.90,
                "metadata": {"agent": self.name, "used_llm": True}
            }

        # Rule-based fallback
        rag_chunks = context.get("rag_chunks", [])
        if rag_chunks:
            return {
                "reply": (
                    f"Based on our knowledge base: \"{rag_chunks[0]}\"\n\n"
                    f"Is there anything else I can help you with?"
                ),
                "confidence": 0.75,
                "metadata": {"agent": self.name, "used_llm": False}
            }

        return {
            "reply": "Hello! How can I assist you today? I'm here to help with any questions you might have.",
            "confidence": 0.85,
            "metadata": {"agent": self.name, "used_llm": False}
        }
