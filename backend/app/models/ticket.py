# ASSIGNED TO: BE-2
# Pydantic models for Tickets
# Schemas needed:
# - TicketCreate: user_id, subject, description, priority
# - TicketResponse: ticket_id, status, assigned_agent, created_at
# - TicketStatus: ticket_id, status, resolution_time

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# TODO: Define Ticket models
class TicketCreate(BaseModel):
    user_id: str
    subject: str
    description: str
    priority: Optional[str] = "medium"

class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    assigned_agent: Optional[str] = None
    created_at: datetime
