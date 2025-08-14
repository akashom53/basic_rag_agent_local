#!/usr/bin/env python3
"""
Test script for enhanced LLM-driven ticket analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.orchestrator import SupportAgent
from app.rag.vectorstore import PostgreSQLVectorStore
from app.core.config import settings

def test_enhanced_ticket_analysis():
    """Test the enhanced ticket analysis capabilities"""
    
    print("🚀 Testing Enhanced LLM-Driven Ticket Analysis")
    print("=" * 60)
    
    # Create vector store and agent
    vector_store = PostgreSQLVectorStore(settings.database_url)
    agent = SupportAgent(vector_store)
    
    print(f"✅ Agent created with LLM: {agent.llm.is_available() if agent.llm else 'Fallback mode'}")
    print()
    
    # Test 1: Specific ticket analysis
    print("=== Test 1: Specific Ticket Analysis ===")
    message = "What's the status of ticket T-B2F2DBB0 and what should we do next?"
    response = agent.handle_message(message)
    print(f"Query: {message}")
    print(f"🎯 Intent: {response.get('analysis_params', 'N/A')}")
    print(f"Reply: {response['reply']}")
    print(f"Tool Calls: {len(response.get('tool_calls', []))}")
    print()
    
    # Test 2: Complex analysis without specific ticket
    print("=== Test 2: Complex Ticket Analysis ===")
    message = "Can you analyze our high priority tickets and identify any patterns?"
    response = agent.handle_message(message)
    print(f"Query: {message}")
    print(f"🎯 Intent: {response.get('analysis_params', 'N/A')}")
    print(f"Reply: {response['reply']}")
    print()
    
    # Test 3: Pattern analysis
    print("=== Test 3: Pattern Analysis ===")
    message = "What trends do you see in our open tickets this week?"
    response = agent.handle_message(message)
    print(f"Query: {message}")
    print(f"🎯 Intent: {response.get('analysis_params', 'N/A')}")
    print(f"Reply: {response['reply']}")
    print()
    
    # Test 4: Recommendation request
    print("=== Test 4: Recommendation Request ===")
    message = "Should we escalate any of our pending tickets based on their current status?"
    response = agent.handle_message(message)
    print(f"Query: {message}")
    print(f"🎯 Intent: {response.get('analysis_params', 'N/A')}")
    print(f"Reply: {response['reply']}")
    print()
    
    # Test 5: Backlog analysis
    print("=== Test 5: Backlog Analysis ===")
    message = "Can you analyze our ticket backlog and suggest prioritization strategies?"
    response = agent.handle_message(message)
    print(f"Query: {message}")
    print(f"🎯 Intent: {response.get('analysis_params', 'N/A')}")
    print(f"Reply: {response['reply']}")
    print()
    
    print("✅ Enhanced ticket analysis testing completed!")

if __name__ == "__main__":
    test_enhanced_ticket_analysis()
