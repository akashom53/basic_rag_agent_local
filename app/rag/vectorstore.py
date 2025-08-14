import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import json
from datetime import datetime

class PostgreSQLVectorStore:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Insert or update chunks with their embeddings"""
        conn = psycopg2.connect(self.connection_string)
        
        try:
            with conn.cursor() as cur:
                for chunk, embedding in zip(chunks, embeddings):
                    cur.execute("""
                        INSERT INTO ai.documents (doc_id, chunk_id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (doc_id, chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                    """, (
                        chunk['metadata']['source'],
                        chunk['id'],
                        chunk['content'],
                        json.dumps(chunk['metadata']),
                        embedding
                    ))
            
            conn.commit()
            print(f"✅ Inserted {len(chunks)} chunks into vector store")
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using cosine similarity"""
        conn = psycopg2.connect(self.connection_string)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, content, metadata, 1 - (embedding <#> %s::vector) AS score
                    FROM ai.documents
                    ORDER BY embedding <#> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, k))
                
                results = cur.fetchall()
                return [dict(row) for row in results]
                
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about ingested documents and chunks"""
        conn = psycopg2.connect(self.connection_string)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get total chunks count
                cur.execute("SELECT COUNT(*) as total_chunks FROM ai.documents")
                total_chunks = cur.fetchone()['total_chunks']
                
                # Get unique documents count
                cur.execute("SELECT COUNT(DISTINCT doc_id) as total_documents FROM ai.documents")
                total_documents = cur.fetchone()['total_documents']
                
                # Get list of available documents (compatible with existing schema)
                cur.execute("""
                    SELECT 
                        doc_id,
                        COUNT(*) as chunk_count
                    FROM ai.documents 
                    GROUP BY doc_id
                    ORDER BY doc_id
                """)
                documents = [dict(row) for row in cur.fetchall()]
                
                return {
                    'total_chunks': total_chunks,
                    'total_documents': total_documents,
                    'last_ingestion': None,  # Not available in current schema
                    'documents': documents
                }
                
        finally:
            conn.close()
    
    def clear_all(self) -> Dict[str, Any]:
        """Clear all documents and chunks from the vector store"""
        conn = psycopg2.connect(self.connection_string)
        
        try:
            with conn.cursor() as cur:
                # Get count before deletion
                cur.execute("SELECT COUNT(*) as count FROM ai.documents")
                count_before = cur.fetchone()[0]
                
                # Delete all documents
                cur.execute("DELETE FROM ai.documents")
                
                conn.commit()
                
                return {
                    'cleared_chunks': count_before,
                    'message': f'Cleared {count_before} chunks'
                }
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a specific document and all its chunks"""
        conn = psycopg2.connect(self.connection_string)
        
        try:
            with conn.cursor() as cur:
                # Get count before deletion
                cur.execute("SELECT COUNT(*) as count FROM ai.documents WHERE doc_id = %s", (document_id,))
                count_before = cur.fetchone()[0]
                
                if count_before == 0:
                    return {
                        'deleted_chunks': 0,
                        'message': f'Document {document_id} not found'
                    }
                
                # Delete all chunks for this document
                cur.execute("DELETE FROM ai.documents WHERE doc_id = %s", (document_id,))
                
                conn.commit()
                
                return {
                    'deleted_chunks': count_before,
                    'message': f'Deleted {count_before} chunks for document {document_id}'
                }
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()