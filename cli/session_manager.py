import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from .config import cli_config
from .utils import load_json_file, save_json_file, print_info, print_warning

class ChatSession:
    """Represents a single chat session"""
    
    def __init__(self, session_id: str, created_at: Optional[datetime] = None):
        self.session_id = session_id
        self.created_at = created_at or datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.last_activity = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the session"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent messages"""
        return self.messages[-count:] if self.messages else []
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def is_active(self, max_idle_hours: int = 24) -> bool:
        """Check if session is still active"""
        idle_threshold = datetime.now() - timedelta(hours=max_idle_hours)
        return self.last_activity > idle_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'messages': self.messages,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary"""
        session = cls(
            session_id=data['session_id'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
        session.messages = data.get('messages', [])
        session.last_activity = datetime.fromisoformat(data['last_activity'])
        session.metadata = data.get('metadata', {})
        return session

class SessionManager:
    """Manages chat sessions and persistence"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None
        self.session_file = cli_config.get_session_file_path()
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file"""
        data = load_json_file(self.session_file, {})
        sessions_data = data.get('sessions', {})
        
        for session_id, session_data in sessions_data.items():
            try:
                session = ChatSession.from_dict(session_data)
                # Only load active sessions
                if session.is_active():
                    self.sessions[session_id] = session
                else:
                    print_warning(f"Session {session_id} expired, skipping")
            except Exception as e:
                print_warning(f"Could not load session {session_id}: {e}")
    
    def _save_sessions(self):
        """Save sessions to file"""
        if not cli_config.auto_save_history:
            return
        
        data = {
            'sessions': {
                session_id: session.to_dict()
                for session_id, session in self.sessions.items()
            },
            'last_saved': datetime.now().isoformat()
        }
        save_json_file(self.session_file, data)
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new chat session"""
        if not session_id:
            session_id = f"cli_{uuid.uuid4().hex[:8]}"
        
        session = ChatSession(session_id)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        print_info(f"Created new session: {session_id}")
        self._save_sessions()
        return session_id
    
    def get_session(self, session_id: Optional[str] = None) -> Optional[ChatSession]:
        """Get a session by ID or current session"""
        target_id = session_id or self.current_session_id
        if not target_id:
            return None
        return self.sessions.get(target_id)
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        if not self.current_session_id:
            return None
        return self.sessions.get(self.current_session_id)
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        if session_id not in self.sessions:
            print_warning(f"Session {session_id} not found")
            return False
        
        self.current_session_id = session_id
        session = self.sessions[session_id]
        print_info(f"Switched to session: {session_id}")
        print_info(f"Session has {session.get_message_count()} messages")
        return True
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions with metadata"""
        sessions_info = []
        for session_id, session in self.sessions.items():
            sessions_info.append({
                'session_id': session_id,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'message_count': session.get_message_count(),
                'is_current': session_id == self.current_session_id,
                'is_active': session.is_active()
            })
        
        # Sort by last activity (most recent first)
        sessions_info.sort(key=lambda x: x['last_activity'], reverse=True)
        return sessions_info
    
    def add_message(self, role: str, content: str, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to a session"""
        target_id = session_id or self.current_session_id
        if not target_id:
            print_warning("No active session, creating new one")
            target_id = self.create_session()
        
        session = self.sessions[target_id]
        session.add_message(role, content, metadata)
        self._save_sessions()
    
    def get_conversation_history(self, session_id: Optional[str] = None, max_messages: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return session.get_recent_messages(max_messages)
    
    def clear_session(self, session_id: Optional[str] = None) -> bool:
        """Clear messages from a session"""
        target_id = session_id or self.current_session_id
        if not target_id:
            return False
        
        if target_id in self.sessions:
            session = self.sessions[target_id]
            session.messages.clear()
            self._save_sessions()
            print_info(f"Cleared session {target_id}")
            return True
        
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # If we deleted the current session, clear it
            if self.current_session_id == session_id:
                self.current_session_id = None
            
            self._save_sessions()
            print_info(f"Deleted session {session_id}")
            return True
        
        return False
    
    def cleanup_expired_sessions(self, max_idle_hours: int = 24):
        """Remove expired sessions"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if not session.is_active(max_idle_hours):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None
        
        if expired_sessions:
            print_info(f"Cleaned up {len(expired_sessions)} expired sessions")
            self._save_sessions()
    
    def get_session_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session.session_id,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'total_messages': session.get_message_count(),
            'user_messages': len([m for m in session.messages if m['role'] == 'user']),
            'assistant_messages': len([m for m in session.messages if m['role'] == 'assistant']),
            'is_active': session.is_active()
        }
