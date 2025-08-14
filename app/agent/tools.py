from langchain.tools import Tool
from ..services.ticket_service import TicketService

def get_ticket_status(ticket_id: str, ticket_service: TicketService) -> str:
    """Get ticket status"""
    ticket = ticket_service.get_ticket_status(ticket_id)
    if ticket:
        return f"Ticket {ticket_id} is {ticket['status']} (Priority: {ticket['priority']})"
    else:
        return f"Ticket {ticket_id} not found"

def create_ticket(description: str, priority: str, ticket_service: TicketService) -> str:
    """Create ticket"""
    ticket_id = ticket_service.create_ticket(description, priority)
    return f"Created ticket {ticket_id} with {priority} priority"

def get_ticket_details(ticket_id: str, ticket_service: TicketService) -> str:
    """Get comprehensive ticket details for LLM reasoning"""
    ticket = ticket_service.get_ticket_status(ticket_id)
    if ticket:
        return f"Ticket {ticket_id}: Status={ticket['status']}, Priority={ticket['priority']}, Description={ticket['description']}, Created={ticket['created_at']}"
    else:
        return f"Ticket {ticket_id} not found"

def create_langchain_tools(ticket_service: TicketService):
    """Create LangChain tools"""
    return [
        Tool(
            name="get_ticket_status",
            description="Get the status of a support ticket by ID",
            func=lambda ticket_id: get_ticket_status(ticket_id, ticket_service)
        ),
        Tool(
            name="create_support_ticket",
            description="Create a new support ticket with description and priority",
            func=lambda description, priority="medium": create_ticket(description, priority, ticket_service)
        ),
        Tool(
            name="get_ticket_details",
            description="Get comprehensive details about a support ticket for analysis and reasoning",
            func=lambda ticket_id: get_ticket_details(ticket_id, ticket_service)
        )
    ]