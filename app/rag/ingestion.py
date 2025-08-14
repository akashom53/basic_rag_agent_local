from .loader import DocumentLoader
from .chunker import DocumentChunker
from .embedder import Embedder
from .vectorstore import PostgreSQLVectorStore
from typing import Dict, Any

class IngestionService:
    def __init__(self, vector_store: PostgreSQLVectorStore):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embedder = Embedder()
        self.vector_store = vector_store
    
    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Complete ingestion pipeline: load → chunk → embed → store"""
        print(f"Loading document: {file_path}")
        document = self.loader.load_document(file_path)
        
        print(f"Chunking document...")
        chunks = self.chunker.chunk_document(document)
        print(f"Created {len(chunks)} chunks")
        
        print(f"Generating embeddings...")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        print(f"Storing in vector database...")
        self.vector_store.upsert_chunks(chunks, embeddings)
        
        return {
            'document_ingested': 1,
            'chunks': len(chunks),
            'file_path': file_path
        }