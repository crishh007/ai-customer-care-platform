import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from .agent_base import BaseAgent
from typing import Dict, Any

class EscalationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EscalationAgent",
            description="Agent responsible for handling angry customers or complex issues that require human escalation."
        )
        # Using a slightly higher temperature for empathetic responses
        self.llm = ChatGroq(temperature=0.2, model_name="llama3-70b-8192")
        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=(
                "You are the Escalation Specialist.\n"
                "The customer is frustrated or has a complex issue.\n"
                "Your goal is to de-escalate the situation with empathy, apologize for the inconvenience, and assure them that a human representative will review their case immediately.\n\n"
                "Context:\n{context}\n\n"
                "Customer: {query}\n"
                "Escalation Agent:"
            )
        )

    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
        
        context_str = str(context)
        formatted_prompt = self.prompt.format(query=query, context=context_str)
        
        response = await self.llm.ainvoke(formatted_prompt)
        
        # In a real system, this agent would also trigger an API call to flag the ticket for a human.
        return response.content
