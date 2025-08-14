from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.ticket_service import TicketService

router = APIRouter()

class TicketCreateRequest(BaseModel):
    description: str
    priority: str

class TicketResponse(BaseModel):
    ticket_id: str
    status: Optional[str] = None
    created_at: Optional[str] = None

# Initialize service
ticket_service = TicketService()

@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(request: TicketCreateRequest):
    """Create a new support ticket"""
    try:
        ticket_id = ticket_service.create_ticket(request.description, request.priority)
        ticket = ticket_service.get_ticket_status(ticket_id)
        return TicketResponse(
            ticket_id=ticket_id,
            status=ticket['status'],
            created_at=ticket['created_at']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str):
    """Get ticket status by ID"""
    try:
        ticket = ticket_service.get_ticket_status(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return TicketResponse(
            ticket_id=ticket['id'],
            status=ticket['status'],
            created_at=ticket['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket: {str(e)}")