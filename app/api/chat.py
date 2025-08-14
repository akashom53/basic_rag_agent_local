from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..agent.orchestrator import SupportAgent
from ..core.config import settings
from ..rag.vectorstore import PostgreSQLVectorStore

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    chat_history_length: Optional[int] = None

# Initialize services
vector_store = PostgreSQLVectorStore(settings.database_url)
support_agent = SupportAgent(vector_store)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages with LangChain memory"""
    try:
        response = support_agent.handle_message(request.message, request.session_id)
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/chat/session/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session using LangChain memory"""
    try:
        history = support_agent.memory_service.get_conversation_history(session_id)
        stats = support_agent.memory_service.get_session_stats(session_id)
        
        # Convert LangChain messages to readable format
        readable_history = []
        for msg in history:
            if hasattr(msg, 'content'):
                if hasattr(msg, 'type') and msg.type == 'human':
                    readable_history.append({
                        'role': 'user',
                        'content': msg.content
                    })
                else:
                    readable_history.append({
                        'role': 'assistant',
                        'content': msg.content
                    })
        
        return {
            "session_id": session_id,
            "history": readable_history,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.delete("/chat/session/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        support_agent.memory_service.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@router.get("/chat/sessions")
async def list_active_sessions():
    """List all active sessions with their stats"""
    try:
        # This would need to be implemented in memory service
        # For now, return basic info
        return {
            "message": "Active sessions endpoint - implement if needed",
            "note": "Use individual session endpoints for now"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")