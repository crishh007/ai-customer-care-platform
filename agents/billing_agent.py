# ASSIGNED TO: AI-2
# Billing Agent - handles payment and refund queries
# Implement:
#   - handle(query, context): Process billing questions
#   - Check payment status, process refund requests
#   - Integrate with billing API (Phase 3)

from agents.agent_base import BaseAgent

class BillingAgent(BaseAgent):
    def __init__(self):
        super().__init__("BillingAgent")

    async def handle(self, query: str, context: dict) -> str:
        # TODO: Implement billing query logic
        pass
