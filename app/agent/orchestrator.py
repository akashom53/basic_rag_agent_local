from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from .intent_router import LLMIntentRouter, Intent
from .tools import create_langchain_tools
from .memory import LangChainMemoryService
from ..rag.ingestion import IngestionService
from ..services.ticket_service import TicketService
from ..rag.embedder import Embedder
from ..rag.vectorstore import PostgreSQLVectorStore
from ..llm.langchain_provider import LangChainLLMProvider
from ..llm.prompts import PromptTemplates
from ..core.config import settings
from datetime import datetime

class SupportAgent:
    def __init__(self, vector_store: PostgreSQLVectorStore):
        # Initialize LLM provider first
        self.llm = LangChainLLMProvider(settings.llm_model, num_gpu=settings.gpu_layers)
        if not self.llm.is_available():
            print("⚠️  Ollama not available, using fallback")
            self.llm = None
        
        # Initialize LLM-based intent router
        self.intent_router = LLMIntentRouter(self.llm)
        self.ticket_service = TicketService()
        self.embedder = Embedder()
        self.vector_store = vector_store
        
        # Initialize LangChain tools
        self.tools = create_langchain_tools(self.ticket_service)
        
        # Initialize LangChain memory service
        self.memory_service = LangChainMemoryService()
    
    def handle_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Main method to handle user messages"""
        print(f" Processing message: {message}")
        
        # Generate session ID if none provided
        if not session_id:
            session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Add user message to LangChain memory
        self.memory_service.add_user_message(session_id, message)
        
        # Get conversation history from LangChain memory
        memory_variables = self.memory_service.get_memory_variables(session_id)
        chat_history = memory_variables.get("chat_history", [])
        
        # Classify intent using LLM-based router
        intent, params = self.intent_router.classify_intent(message)
        print(f"🎯 Intent: {intent.value}, Params: {params}")
        
        # Handle the message based on intent
        if intent == Intent.GET_TICKET_STATUS:
            response = self._handle_ticket_status(params)
        elif intent == Intent.CREATE_TICKET:
            response = self._handle_create_ticket(params)
        elif intent == Intent.ANALYZE_TICKETS:
            response = self._handle_ticket_analysis(message, params)
        else:
            response = self._handle_rag_question(message, chat_history)
        
        # Add assistant response to LangChain memory
        self.memory_service.add_ai_message(session_id, response['reply'])
        
        # Add session_id to response
        response['session_id'] = session_id
        
        return response
    
    def _handle_ticket_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ticket status requests using LangChain tool"""
        ticket_id = params.get('ticket_id')
        
        # Use LangChain tool
        tool = next((t for t in self.tools if t.name == "get_ticket_status"), None)
        if tool:
            result = tool.func(ticket_id)
            return {
                'reply': result,
                'tool_calls': [{
                    'name': 'get_ticket_status',
                    'args': {'ticket_id': ticket_id},
                    'result': result
                }]
            }
        else:
            return {
                'reply': f"Sorry, I couldn't find ticket {ticket_id}. Please check the ticket ID and try again.",
                'tool_calls': []
            }
    
    def _handle_create_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ticket creation requests using LangChain tool"""
        description = params.get('description', 'No description provided')
        priority = params.get('priority', 'medium')
        
        # Use LangChain tool
        tool = next((t for t in self.tools if t.name == "create_support_ticket"), None)
        if tool:
            result = tool.func(description, priority)
            return {
                'reply': result,
                'tool_calls': [{
                    'name': 'create_support_ticket',
                    'args': {'description': description, 'priority': priority},
                    'result': result
                }]
            }
        else:
            return {
                'reply': "Sorry, I encountered an error creating the ticket.",
                'tool_calls': []
            }
    
    def _handle_ticket_analysis(self, message: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex ticket analysis with LLM reasoning"""
        
        # Get ticket details if ticket_id is provided
        ticket_info = ""
        if 'ticket_id' in params:
            tool = next((t for t in self.tools if t.name == "get_ticket_details"), None)
            if tool:
                ticket_info = tool.func(params['ticket_id'])
        
        # Create enhanced prompt for LLM reasoning
        system_prompt = f"""You are analyzing support tickets. Use the ticket information provided to answer user questions intelligently.

Available ticket information:
{ticket_info if ticket_info else "No specific ticket ID provided"}

Analysis parameters: {params}

User question: {message}

Provide a comprehensive analysis including:
1. Current ticket status and details (if specific ticket)
2. Analysis of the situation based on available information
3. Recommendations or next steps
4. Any patterns or insights you notice
5. Suggestions for improving ticket management

Be helpful, professional, and provide actionable advice. If you need more information, ask clarifying questions."""

        user_prompt = f"Ticket Info: {ticket_info}\n\nUser Question: {message}\n\nAnalysis Parameters: {params}"
        
        if self.llm:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            try:
                llm_response = self.llm.generate(messages)
            except Exception as e:
                print(f"❌ LLM analysis failed: {e}")
                llm_response = self._generate_fallback_analysis(ticket_info, params, message)
        else:
            llm_response = self._generate_fallback_analysis(ticket_info, params, message)
        
        return {
            'reply': llm_response,
            'ticket_info': ticket_info,
            'analysis_params': params,
            'tool_calls': [{
                'name': 'get_ticket_details',
                'args': params,
                'result': ticket_info
            }] if ticket_info else []
        }
    
    def _generate_fallback_analysis(self, ticket_info: str, params: Dict[str, Any], message: str) -> str:
        """Generate fallback analysis when LLM is not available"""
        if ticket_info:
            return f"Based on the ticket information: {ticket_info}\n\nThis appears to be a {params.get('priority', 'medium')} priority ticket that is currently {params.get('status', 'open')}. Please review the details and take appropriate action."
        else:
            return f"I can help analyze tickets based on your parameters: {params}. However, I need more specific information to provide detailed analysis. Could you please specify which tickets you'd like me to analyze?"
    
    def _handle_rag_question(self, message: str, chat_history: List = None) -> Dict[str, Any]:
        """Handle RAG questions using document retrieval + LLM generation with LangChain memory"""
        # Generate query embedding
        query_embedding = self.embedder.embed_query(message)
        
        # Retrieve relevant chunks
        results = self.vector_store.similarity_search(query_embedding, k=3)
        
        if not results:
            return {
                'reply': "I couldn't find relevant information in the documentation. Could you please rephrase your question?",
                'sources': []
            }
        
        # Build context from retrieved chunks
        context = "\n\n".join([result['content'] for result in results])
        
        if self.llm:
            # Use LangChain LLM for enhanced response with memory context
            system_prompt = PromptTemplates.rag_system_prompt()
            
            # Enhanced user prompt with LangChain memory context
            enhanced_context = self._build_enhanced_context(context, chat_history, message)
            user_prompt = PromptTemplates.rag_user_prompt(enhanced_context, message)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            llm_response = self.llm.generate(messages)
        else:
            # Fallback response with context awareness
            if chat_history:
                llm_response = f"Based on our conversation and the documentation, here's what I found:\n\n{context[:500]}...\n\nI'm maintaining context from our previous discussion."
            else:
                llm_response = f"Based on the documentation, here's what I found:\n\n{context[:500]}..."
        
        return {
            'reply': llm_response,
            'sources': [{
                'content': result['content'][:200],
                'score': result['score'],
                'metadata': result['metadata']
            } for result in results],
            'chat_history_length': len(chat_history) if chat_history else 0
        }
    
    def _build_enhanced_context(self, document_context: str, chat_history: List, current_message: str) -> str:
        """Build enhanced context combining documents and conversation history"""
        context_parts = [f"Documentation Context:\n{document_context}"]
        
        if chat_history:
            # Convert LangChain messages to readable format
            conversation_summary = []
            for msg in chat_history[-5:]:  # Last 5 messages
                if hasattr(msg, 'content'):
                    if hasattr(msg, 'type') and msg.type == 'human':
                        conversation_summary.append(f"User: {msg.content}")
                    else:
                        conversation_summary.append(f"Assistant: {msg.content}")
            
            if conversation_summary:
                context_parts.append(f"Recent Conversation:\n" + "\n".join(conversation_summary))
        
        context_parts.append(f"Current Question: {current_message}")
        
        return "\n\n".join(context_parts)