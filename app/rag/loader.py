import os
from typing import Dict, Any
import pypdf

class DocumentLoader:
    def __init__(self):
        self.supported_extensions = {'.pdf', '.md', '.txt'}
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Load a document and return its content and metadata"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._load_pdf(file_path)
        elif ext == '.md':
            return self._load_markdown(file_path)
        elif ext == '.txt':
            return self._load_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _load_pdf(self, file_path: str) -> Dict[str, Any]:
        """Load PDF file using pypdf"""
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return {
                'content': text,
                'metadata': {
                    'source': file_path,
                    'type': 'pdf',
                    'pages': len(reader.pages)
                }
            }
    
    def _load_markdown(self, file_path: str) -> Dict[str, Any]:
        """Load Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            return {
                'content': content,
                'metadata': {
                    'source': file_path,
                    'type': 'markdown'
                }
            }
    
    def _load_text(self, file_path: str) -> Dict[str, Any]:
        """Load text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            return {
                'content': content,
                'metadata': {
                    'source': file_path,
                    'type': 'text'
                }
            }