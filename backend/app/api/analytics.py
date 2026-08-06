# ASSIGNED TO: BE-4
# Analytics API routes
# Endpoints to implement:
#   GET /api/analytics/dashboard  → KPI metrics summary
#   GET /api/analytics/sentiment  → Sentiment data over time
#   GET /api/analytics/tickets    → Ticket analytics (resolution time, CSAT)
#   GET /api/analytics/agents     → Per-agent performance metrics

from fastapi import APIRouter
from typing import Dict, Any

import sys
import os

# Ensure ai-engine is accessible
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "ai-engine"))
try:
    from analytics.predictive.churn_predictor import ChurnPredictor
    churn_agent = ChurnPredictor()
except ImportError:
    churn_agent = None

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    # Aggregate: active_conversations, csat_score, ticket_count, automation_rate
    # Return JSON with all KPIs (mock data for now)
    return {
        "active_conversations": 42,
        "csat_score": 94.5,
        "ticket_count": 156,
        "automation_rate": 82.1,
        "escalation_rate": 12.5,
        "response_time_sec": 1.2
    }

@router.get("/sentiment")
async def get_sentiment():
    """Returns dummy sentiment analysis data for the dashboard chart"""
    return {
        "positive": 65,
        "neutral": 20,
        "negative": 15,
        "trend": [
            {"date": "Mon", "score": 0.8},
            {"date": "Tue", "score": 0.75},
            {"date": "Wed", "score": 0.9},
            {"date": "Thu", "score": 0.6},
            {"date": "Fri", "score": 0.85},
        ]
    }

@router.get("/churn")
async def get_churn_risk():
    """Uses AI agent to predict churn risk for a sample user"""
    if churn_agent:
        try:
            # Mock data for demonstration
            customer_data = "Name: Acme Corp, Plan: Pro, Tenure: 3 months, MRR: $200"
            interactions = "User escalated 3 tickets in the last week regarding downtime."
            prediction = await churn_agent.predict_churn(customer_data, interactions)
            return prediction
        except Exception as e:
            pass
            
    # Fallback mock
    return {
        "risk_score": 85,
        "reason": "High volume of recent escalations and negative sentiment."
    }
