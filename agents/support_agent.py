# ASSIGNED TO: AI-2
# General Support Agent - handles common customer queries
# Inherits from BaseAgent
# Implement:
#   - handle(query, context): Use LLM + RAG context to answer general questions
#   - Covers: order status, product info, account queries

from agents.agent_base import BaseAgent

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupportAgent")

    async def handle(self, query: str, context: dict) -> str:
        # TODO: Build prompt with context
        # TODO: Call OpenAI API
        # TODO: Return response
        pass
