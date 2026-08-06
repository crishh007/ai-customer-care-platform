import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from .agent_base import BaseAgent
from typing import Dict, Any

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SentimentAgent",
            description="Analyzes the sentiment of a customer's message and returns a single sentiment label."
        )
        self.llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
        self.prompt = PromptTemplate(
            input_variables=["query"],
            template=(
                "You are an AI Sentiment Analyzer for a customer care platform.\n"
                "Analyze the following customer message and return EXACTLY ONE of these labels: POSITIVE, NEUTRAL, NEGATIVE, or ANGRY.\n\n"
                "Customer message: {query}\n\n"
                "Label:"
            )
        )

    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        formatted_prompt = self.prompt.format(query=query)
        response = await self.llm.ainvoke(formatted_prompt)
        return response.content.strip().upper()
