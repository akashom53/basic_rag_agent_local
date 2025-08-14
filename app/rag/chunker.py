from typing import List, Dict, Any
import re

class DocumentChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split document into overlapping chunks"""
        content = document['content']
        metadata = document['metadata']
        
        # Simple text splitting by sentences and paragraphs
        chunks = []
        sentences = self._split_into_sentences(content)
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append({
                        'id': chunk_id,
                        'content': current_chunk.strip(),
                        'metadata': {
                            **metadata,
                            'chunk_id': chunk_id,
                            'chunk_size': len(current_chunk)
                        }
                    })
                    chunk_id += 1
                
                # Start new chunk with overlap
                current_chunk = sentence + " "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'id': chunk_id,
                'content': current_chunk.strip(),
                'metadata': {
                    **metadata,
                    'chunk_id': chunk_id,
                    'chunk_size': len(current_chunk)
                }
            })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be improved
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]