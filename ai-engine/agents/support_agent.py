import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from .agent_base import BaseAgent
from typing import Dict, Any

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SupportAgent",
            description="Agent responsible for handling general customer support queries."
        )
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="You are a helpful customer support agent.\n\nContext:\n{context}\n\nCustomer: {query}\nAgent:"
        )

    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
        
        context_str = str(context)
        formatted_prompt = self.prompt.format(query=query, context=context_str)
        
        response = await self.llm.ainvoke(formatted_prompt)
        return response.content
