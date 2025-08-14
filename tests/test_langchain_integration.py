from app.core.config import settings
from app.rag.vectorstore import PostgreSQLVectorStore
from app.agent.orchestrator import SupportAgent

def test_langchain_integration():
    # Initialize services
    vector_store = PostgreSQLVectorStore(settings.database_url)
    support_agent = SupportAgent(vector_store)
    
    # Test RAG question with LangChain LLM
    print("=== Testing RAG Question with LangChain LLM ===")
    response = support_agent.handle_message("What are the best practices for API testing?")
    print(f"Reply: {response['reply']}")
    print(f"Sources: {len(response.get('sources', []))}")
    
    # Test ticket creation with LangChain tools
    print("\n=== Testing Ticket Creation with LangChain Tools ===")
    response = support_agent.handle_message("Create a high priority ticket for security vulnerabilities")
    print(f"Reply: {response['reply']}")
    
    # Test ticket status with LangChain tools
    if response.get('tool_calls'):
        # Extract ticket ID from the response
        reply = response['reply']
        if 'Created ticket' in reply:
            ticket_id = reply.split('Created ticket ')[1].split(' ')[0]
            print(f"\n=== Testing Ticket Status for {ticket_id} ===")
            status_response = support_agent.handle_message(f"What's the status of ticket {ticket_id}?")
            print(f"Reply: {status_response['reply']}")

if __name__ == "__main__":
    test_langchain_integration()