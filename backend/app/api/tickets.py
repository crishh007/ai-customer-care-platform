# ASSIGNED TO: BE-3
# Tickets API routes
# Endpoints to implement:
#   POST /api/tickets/create      → Create a new support ticket
#   GET  /api/tickets/status      → Get ticket status by ID
#   GET  /api/tickets/list        → List all tickets for a user
#   PUT  /api/tickets/update/{id} → Update ticket status

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from app.database import db

router = APIRouter()

class TicketCreate(BaseModel):
    user_id: str
    subject: str
    description: str
    priority: str = "medium"

class TicketResponse(BaseModel):
    ticket_id: str
    user_id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime

@router.post("/create", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: TicketCreate):
    new_ticket = {
        "ticket_id": str(uuid.uuid4()),
        "user_id": ticket.user_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": "open",
        "priority": ticket.priority,
        "created_at": datetime.now(timezone.utc)
    }
    await db.tickets.insert_one(new_ticket)
    return new_ticket

@router.get("/status/{ticket_id}", response_model=TicketResponse)
async def get_ticket_status(ticket_id: str):
    ticket = await db.tickets.find_one({"ticket_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/list/{user_id}", response_model=List[TicketResponse])
async def list_tickets(user_id: str):
    cursor = db.tickets.find({"user_id": user_id})
    tickets = await cursor.to_list(length=100)
    return tickets

@router.put("/update/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, status: str):
    result = await db.tickets.find_one_and_update(
        {"ticket_id": ticket_id},
        {"$set": {"status": status}},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result
