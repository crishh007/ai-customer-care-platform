from fastapi import APIRouter, Depends, HTTPException
import random

router = APIRouter()

# Mock CRM Database
MOCK_CRM_DB = {
    "user_123": {
        "customer_id": "user_123",
        "name": "Acme Corp",
        "plan": "Enterprise",
        "mrr": 5000,
        "tenure_months": 24,
        "health_score": 85,
        "recent_tickets": [
            {"issue": "API Rate limit exceeded", "status": "resolved"},
            {"issue": "Billing question", "status": "resolved"}
        ]
    },
    "user_456": {
        "customer_id": "user_456",
        "name": "Startup Inc",
        "plan": "Pro",
        "mrr": 200,
        "tenure_months": 3,
        "health_score": 40,
        "recent_tickets": [
            {"issue": "Service downtime", "status": "open"},
            {"issue": "Data export failed", "status": "open"},
            {"issue": "Cannot log in", "status": "resolved"}
        ]
    }
}

@router.get("/customer/{customer_id}")
async def get_customer_crm_data(customer_id: str):
    """
    Mock endpoint to fetch customer data from a CRM (e.g., Salesforce/HubSpot)
    """
    data = MOCK_CRM_DB.get(customer_id)
    if not data:
        # Return a generic profile if not found to keep the demo running smoothly
        return {
            "customer_id": customer_id,
            "name": "Unknown Customer",
            "plan": "Free",
            "mrr": 0,
            "tenure_months": 1,
            "health_score": 50,
            "recent_tickets": []
        }
    return data
