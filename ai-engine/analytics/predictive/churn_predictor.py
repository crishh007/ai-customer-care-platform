import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import json

class ChurnPredictor:
    def __init__(self):
        # We use a fast Groq model for real-time predictive analytics
        self.llm = ChatGroq(temperature=0.1, model_name="llama3-8b-8192")
        self.prompt = PromptTemplate(
            input_variables=["customer_data", "recent_interactions"],
            template=(
                "You are an AI predictive analytics engine specializing in customer retention.\n"
                "Analyze the following CRM data and recent support interactions to determine the customer's churn risk.\n\n"
                "Customer CRM Data:\n"
                "{customer_data}\n\n"
                "Recent Interactions:\n"
                "{recent_interactions}\n\n"
                "Provide a JSON response with exactly two keys:\n"
                "1. 'risk_score': an integer from 0 to 100 representing the probability of churn.\n"
                "2. 'reason': a brief, 1-sentence explanation of why.\n\n"
                "Output ONLY valid JSON."
            )
        )
        self.chain = self.prompt | self.llm
        
    async def predict_churn(self, customer_data: str, recent_interactions: str) -> Dict[str, Any]:
        try:
            result = await self.chain.ainvoke({
                "customer_data": customer_data,
                "recent_interactions": recent_interactions
            })
            
            # Parse the JSON output from the LLM
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            return json.loads(content)
        except Exception as e:
            print(f"Error predicting churn: {e}")
            return {"risk_score": 0, "reason": "Failed to compute churn risk."}
