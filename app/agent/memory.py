from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from typing import Dict, List, Optional
import uuid

class LangChainMemoryService:
    def __init__(self):
        # Store multiple conversation memories by session_id
        self.session_memories: Dict[str, ConversationBufferMemory] = {}
    
    def get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """Get existing memory for session or create new one"""
        if session_id not in self.session_memories:
            self.session_memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
        return self.session_memories[session_id]
    
    def add_user_message(self, session_id: str, message: str):
        """Add user message to session memory"""
        memory = self.get_or_create_memory(session_id)
        memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, session_id: str, message: str):
        """Add AI message to session memory"""
        memory = self.get_or_create_memory(session_id)
        memory.chat_memory.add_ai_message(message)
    
    def get_conversation_history(self, session_id: str) -> List:
        """Get conversation history for a session"""
        memory = self.get_or_create_memory(session_id)
        return memory.chat_memory.messages
    
    def get_memory_variables(self, session_id: str) -> Dict:
        """Get memory variables for LangChain integration"""
        memory = self.get_or_create_memory(session_id)
        return memory.load_memory_variables({})
    
    def clear_session(self, session_id: str):
        """Clear memory for a specific session"""
        if session_id in self.session_memories:
            del self.session_memories[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        if session_id not in self.session_memories:
            return {'message_count': 0, 'last_activity': None}
        
        memory = self.session_memories[session_id]
        messages = memory.chat_memory.messages
        return {
            'message_count': len(messages),
            'last_activity': 'Active' if messages else 'None'
        }