from typing import Dict, List, Optional
import uuid
from datetime import datetime

class TicketService:
    def __init__(self):
        # In-memory ticket store
        self.tickets: Dict[str, Dict] = {}
    
    def create_ticket(self, description: str, priority: str) -> str:
        """Create a new support ticket"""
        ticket_id = f"T-{str(uuid.uuid4())[:8].upper()}"
        
        # Validate priority
        if priority.lower() not in ['low', 'medium', 'high']:
            priority = 'medium'  # Default to medium
        
        self.tickets[ticket_id] = {
            'id': ticket_id,
            'description': description,
            'priority': priority.lower(),
            'status': 'open',
            'created_at': datetime.now().isoformat()
        }
        
        return ticket_id
    
    def get_ticket_status(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket status by ID"""
        return self.tickets.get(ticket_id)
    
    def get_all_tickets(self) -> List[Dict]:
        """Get all tickets"""
        return list(self.tickets.values())
    
    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update ticket status"""
        if ticket_id in self.tickets:
            self.tickets[ticket_id]['status'] = status
            return True
        return False