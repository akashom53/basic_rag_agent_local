import json
import re
from typing import Dict, Any, Tuple, Optional
from enum import Enum
from langchain_core.messages import HumanMessage, SystemMessage

class Intent(Enum):
    RAG_QUESTION = "rag_question"
    GET_TICKET_STATUS = "get_ticket_status"
    CREATE_TICKET = "create_ticket"
    ANALYZE_TICKETS = "analyze_tickets"

class LLMIntentRouter:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        
        # Fallback patterns for when LLM is not available
        self.fallback_patterns = {
            'ticket_id': r'([A-Za-z]\-?[A-Za-z0-9]+)',
            'priority_keywords': {
                'high': ['high', 'urgent', 'critical', 'emergency', 'important'],
                'medium': ['medium', 'normal', 'standard', 'moderate'],
                'low': ['low', 'minor', 'trivial', 'non-urgent']
            }
        }
    
    def classify_intent(self, message: str, conversation_history: str = "") -> Tuple[Intent, Dict[str, Any]]:
        """Classify user intent using LLM with fallback to pattern matching"""
        if self.llm and self.llm.is_available():
            return self._classify_with_llm(message, conversation_history)
        else:
            return self._classify_with_patterns(message)
    
    def _classify_with_llm(self, message: str, conversation_history: str = "") -> Tuple[Intent, Dict[str, Any]]:
        """Use LLM to classify intent and extract parameters"""
        try:
            # Create system prompt for intent classification
            system_prompt = """You are an intent classification system for a support assistant. Your job is to:

1. Classify the user's intent into one of these categories:
   - rag_question: General questions about API testing, software development, or documentation
   - create_ticket: User wants to create a new support ticket
   - get_ticket_status: User wants to check the status of an existing ticket
   - analyze_tickets: User wants complex analysis of multiple tickets or patterns

2. Extract relevant parameters based on the intent:
   - For create_ticket: description and priority (low/medium/high)
   - For get_ticket_status: ticket_id
   - For analyze_tickets: analysis parameters
   - For rag_question: no parameters needed

3. Return ONLY a valid JSON object with the exact structure shown in examples.

Examples:
- "What are the best practices for API testing?" → {"intent": "rag_question"}
- "Create a high priority ticket for security vulnerabilities" → {"intent": "create_ticket", "description": "security vulnerabilities", "priority": "high"}
- "What's the status of ticket T-12345?" → {"intent": "get_ticket_status", "ticket_id": "T-12345"}
- "Analyze open tickets from this week" → {"intent": "analyze_tickets", "status": "open", "timeframe": "week"}

Be precise and only return valid JSON."""

            user_prompt = f"User message: {message}\nConversation history: {conversation_history if conversation_history else 'None'}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Use the specialized intent classification method
            result = self.llm.classify_intent(messages)
            
            if result:
                return self._parse_llm_result(result)
            else:
                # Fallback to pattern matching if LLM response is invalid
                print(f"⚠️ LLM response invalid, falling back to pattern matching")
                return self._classify_with_patterns(message)
            
        except Exception as e:
            print(f"❌ LLM intent classification failed: {e}")
            return self._classify_with_patterns(message)
    
    def _parse_llm_result(self, result: Dict[str, Any]) -> Tuple[Intent, Dict[str, Any]]:
        """Parse and validate LLM classification result"""
        intent_str = result.get('intent', '').lower()
        
        # Map intent string to Intent enum
        intent_map = {
            'rag_question': Intent.RAG_QUESTION,
            'create_ticket': Intent.CREATE_TICKET,
            'get_ticket_status': Intent.GET_TICKET_STATUS,
            'analyze_tickets': Intent.ANALYZE_TICKETS
        }
        
        intent = intent_map.get(intent_str, Intent.RAG_QUESTION)
        
        # Extract and validate parameters based on intent
        params = {}
        
        if intent == Intent.CREATE_TICKET:
            params['description'] = result.get('description', 'No description provided')
            priority = result.get('priority', 'medium').lower()
            if priority in ['low', 'medium', 'high']:
                params['priority'] = priority
            else:
                params['priority'] = 'medium'
                
        elif intent == Intent.GET_TICKET_STATUS:
            ticket_id = result.get('ticket_id')
            if ticket_id:
                params['ticket_id'] = ticket_id
            else:
                # If no ticket ID found, fall back to RAG question
                intent = Intent.RAG_QUESTION
                
        elif intent == Intent.ANALYZE_TICKETS:
            # Extract analysis parameters
            for key in ['priority', 'status', 'timeframe']:
                if key in result:
                    params[key] = result[key]
        
        return intent, params
    
    def _classify_with_patterns(self, message: str) -> Tuple[Intent, Dict[str, Any]]:
        """Fallback pattern-based intent classification"""
        message_lower = message.lower()
        
        # Check for ticket creation
        if any(word in message_lower for word in ['ticket', 'create', 'raise', 'open', 'submit', 'file']):
            priority = self._extract_priority(message_lower)
            description = self._extract_description(message, message_lower)
            return Intent.CREATE_TICKET, {
                'description': description,
                'priority': priority
            }
        
        # Check for ticket status
        ticket_id = self._extract_ticket_id(message)
        if ticket_id and any(word in message_lower for word in ['status', 'check', 'what']):
            return Intent.GET_TICKET_STATUS, {'ticket_id': ticket_id}
        
        # Check for analysis requests
        if any(word in message_lower for word in ['analyze', 'analysis', 'pattern', 'trend', 'backlog']):
            return Intent.ANALYZE_TICKETS, self._extract_analysis_params(message_lower)
        
        # Default to RAG question
        return Intent.RAG_QUESTION, {}
    
    def _extract_priority(self, message_lower: str) -> str:
        """Extract priority from message"""
        for priority, keywords in self.fallback_patterns['priority_keywords'].items():
            if any(keyword in message_lower for keyword in keywords):
                return priority
        return 'medium'
    
    def _extract_description(self, message: str, message_lower: str) -> str:
        """Extract ticket description from message"""
        description = message
        
        # Remove common ticket creation words
        for word in ['create', 'ticket', 'raise', 'open', 'submit', 'file', 'for', 'a', 'an']:
            description = re.sub(rf'\b{word}\b', '', description, flags=re.IGNORECASE)
        
        # Remove priority words
        for priority, keywords in self.fallback_patterns['priority_keywords'].items():
            for keyword in keywords:
                description = re.sub(rf'\b{keyword}\b', '', description, flags=re.IGNORECASE)
        
        return description.strip()
    
    def _extract_ticket_id(self, message: str) -> Optional[str]:
        """Extract ticket ID from message"""
        match = re.search(self.fallback_patterns['ticket_id'], message)
        return match.group(1) if match else None
    
    def _extract_analysis_params(self, message_lower: str) -> Dict[str, Any]:
        """Extract parameters for ticket analysis"""
        params = {}
        
        # Extract priority filter
        for priority, keywords in self.fallback_patterns['priority_keywords'].items():
            if any(keyword in message_lower for keyword in keywords):
                params['priority'] = priority
                break
        
        # Extract status filter
        if 'open' in message_lower:
            params['status'] = 'open'
        elif 'closed' in message_lower:
            params['status'] = 'closed'
        elif 'pending' in message_lower:
            params['status'] = 'pending'
        
        # Extract time filter
        if any(word in message_lower for word in ['week', 'month', 'today', 'recent']):
            if 'week' in message_lower:
                params['timeframe'] = 'week'
            elif 'month' in message_lower:
                params['timeframe'] = 'month'
            elif 'today' in message_lower:
                params['timeframe'] = 'today'
        
        return params

# Keep the old IntentRouter for backward compatibility, but mark as deprecated
class IntentRouter(LLMIntentRouter):
    """Deprecated: Use LLMIntentRouter instead"""
    def __init__(self):
        # Initialize without LLM provider for backward compatibility
        super().__init__(None)
        print("⚠️  IntentRouter is deprecated. Use LLMIntentRouter with an LLM provider instead.")