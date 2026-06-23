# ASSIGNED TO: BE-2
# Pydantic models for Chat
# Schemas needed:
# - ChatQuery: user_id, message, session_id
# - ChatResponse: reply, sentiment, confidence_score, agent_used
# - Message: role (user/assistant), content, timestamp, sentiment

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# TODO: Define Chat models
class ChatQuery(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    sentiment: Optional[str] = "neutral"
    confidence_score: Optional[float] = 1.0
    agent_used: Optional[str] = "support_agent"
