from app.core.config import settings
from app.rag.vectorstore import PostgreSQLVectorStore
from app.rag.ingestion import IngestionService
from app.rag.embedder import Embedder

def test_ingestion():
    # Initialize vector store
    vector_store = PostgreSQLVectorStore(settings.database_url)
    
    # Initialize ingestion service
    ingestion_service = IngestionService(vector_store)
    
    # Test with your document
    result = ingestion_service.ingest_document("samples/api_testing_guide.md")
    print(f"Ingestion result: {result}")
    
    # Test retrieval
    test_query = "What is API testing?"
    embedder = Embedder()
    query_embedding = embedder.embed_query(test_query)
    
    results = vector_store.similarity_search(query_embedding, k=3)
    print(f"\nRetrieval results for '{test_query}':")
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result['score']:.3f}")
        print(f"   Content: {result['content'][:100]}...")
        print()

if __name__ == "__main__":
    test_ingestion()