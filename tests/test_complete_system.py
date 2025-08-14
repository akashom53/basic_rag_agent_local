from app.core.config import settings
from app.rag.vectorstore import PostgreSQLVectorStore
from app.agent.orchestrator import SupportAgent

def test_complete_system():
    # Initialize services
    vector_store = PostgreSQLVectorStore(settings.database_url)
    support_agent = SupportAgent(vector_store)
    
    # Test RAG question
    print("=== Testing RAG Question ===")
    response = support_agent.handle_message("What is API testing?")
    print(f"Reply: {response['reply'][:200]}...")
    print(f"Sources: {len(response.get('sources', []))}")
    
    # Test ticket creation
    print("\n=== Testing Ticket Creation ===")
    response = support_agent.handle_message("Create a high priority ticket for login issues")
    print(f"Reply: {response['reply']}")
    print(f"Tool Calls: {response.get('tool_calls', [])}")
    
    # Test ticket status
    print("\n=== Testing Ticket Status ===")
    # Extract ticket ID from previous response
    if response.get('tool_calls'):
        ticket_id = response['tool_calls'][0]['result']['ticket_id']
        response = support_agent.handle_message(f"What's the status of ticket {ticket_id}?")
        print(f"Reply: {response['reply']}")

if __name__ == "__main__":
    test_complete_system()