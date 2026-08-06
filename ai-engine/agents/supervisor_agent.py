import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from .agent_base import BaseAgent
from .sentiment_agent import SentimentAgent
from typing import Dict, Any

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SupervisorAgent",
            description="Master orchestrator that routes user queries to the appropriate sub-agent."
        )
        self.llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")
        self.sentiment_agent = SentimentAgent()
        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=(
                "You are the Supervisor Agent for an AI Customer Care platform.\n"
                "Your job is to analyze the user's query and route it to the correct department.\n"
                "Available departments: BILLING, SUPPORT, ESCALATION.\n\n"
                "Context: {context}\n"
                "Query: {query}\n\n"
                "Respond with ONLY the department name in uppercase."
            )
        )

    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
            
        # 1. Analyze Sentiment First
        sentiment = await self.sentiment_agent.process(query)
        
        # 2. Auto-escalate if angry
        if sentiment in ["ANGRY", "NEGATIVE"]:
            return "ESCALATION"
        
        # 3. Standard Routing
        context_str = str(context)
        formatted_prompt = self.prompt.format(query=query, context=context_str)
        
        response = await self.llm.ainvoke(formatted_prompt)
        department = response.content.strip().upper()
        
        return department
