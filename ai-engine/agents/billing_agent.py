import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from .agent_base import BaseAgent
from typing import Dict, Any

class BillingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="BillingAgent",
            description="Agent responsible for handling payment, refund, and subscription queries."
        )
        self.llm = ChatGroq(temperature=0.2, model_name="llama3-70b-8192")
        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=(
                "You are the Billing Support Agent.\n"
                "You handle questions about invoices, payments, refunds, and subscriptions.\n\n"
                "Context (Customer Details & Billing History):\n{context}\n\n"
                "Customer: {query}\n"
                "Billing Agent:"
            )
        )

    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
        
        context_str = str(context)
        formatted_prompt = self.prompt.format(query=query, context=context_str)
        
        response = await self.llm.ainvoke(formatted_prompt)
        return response.content
