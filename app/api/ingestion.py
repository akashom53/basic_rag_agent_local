from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..rag.ingestion import IngestionService
from ..rag.vectorstore import PostgreSQLVectorStore
from ..core.config import settings
import os
import tempfile
import shutil

router = APIRouter()

class IngestionRequest(BaseModel):
    file_path: Optional[str] = None
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class IngestionResponse(BaseModel):
    success: bool
    message: str
    document_ingested: int
    chunks_created: int
    file_path: Optional[str] = None
    processing_time: Optional[float] = None

class IngestionStatusResponse(BaseModel):
    total_documents: int
    total_chunks: int
    last_ingestion: Optional[str] = None  # Optional since not available in current schema
    available_documents: List[Dict[str, Any]]

# Initialize services
vector_store = PostgreSQLVectorStore(settings.database_url)
ingestion_service = IngestionService(vector_store)

@router.post("/ingest/file", response_model=IngestionResponse)
async def ingest_file(
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200)
):
    """
    Ingest a document file (PDF, MD, TXT, etc.) into the vector database
    
    - **file**: Document file to ingest
    - **chunk_size**: Size of text chunks (default: 1000)
    - **chunk_overlap**: Overlap between chunks (default: 200)
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.md', '.txt', '.docx', '.doc']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Process the document
            import time
            start_time = time.time()
            
            result = ingestion_service.ingest_document(temp_file_path)
            
            processing_time = time.time() - start_time
            
            return IngestionResponse(
                success=True,
                message=f"Successfully ingested {file.filename}",
                document_ingested=result['document_ingested'],
                chunks_created=result['chunks'],
                file_path=file.filename,
                processing_time=round(processing_time, 2)
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@router.post("/ingest/path", response_model=IngestionResponse)
async def ingest_document_path(request: IngestionRequest):
    """
    Ingest a document from a file path (useful for server-side documents)
    
    - **file_path**: Path to the document file
    - **chunk_size**: Size of text chunks (default: 1000)
    - **chunk_overlap**: Overlap between chunks (default: 200)
    """
    try:
        if not request.file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Update chunking parameters if provided
        if request.chunk_size is not None:
            ingestion_service.chunker.chunk_size = request.chunk_size
        if request.chunk_overlap is not None:
            ingestion_service.chunker.chunk_overlap = request.chunk_overlap
        
        import time
        start_time = time.time()
        
        result = ingestion_service.ingest_document(request.file_path)
        
        processing_time = time.time() - start_time
        
        return IngestionResponse(
            success=True,
            message=f"Successfully ingested {request.file_path}",
            document_ingested=result['document_ingested'],
            chunks_created=result['chunks'],
            file_path=request.file_path,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@router.get("/ingest/status", response_model=IngestionStatusResponse)
async def get_ingestion_status():
    """
    Get the current status of ingested documents and chunks
    """
    try:
        # Get statistics from vector store
        stats = vector_store.get_statistics()
        
        return IngestionStatusResponse(
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_chunks', 0),
            last_ingestion=stats.get('last_ingestion'),  # Will be None for current schema
            available_documents=stats.get('documents', [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ingestion status: {str(e)}")

@router.delete("/ingest/clear")
async def clear_all_documents():
    """
    Clear all ingested documents and chunks from the vector database
    """
    try:
        result = vector_store.clear_all()
        return JSONResponse(
            content={
                "success": True,
                "message": "All documents and chunks cleared successfully",
                "cleared_chunks": result.get('cleared_chunks', 0)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@router.delete("/ingest/document/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a specific document and its chunks from the vector database
    """
    try:
        result = vector_store.delete_document(document_id)
        return JSONResponse(
            content={
                "success": True,
                "message": f"Document {document_id} deleted successfully",
                "deleted_chunks": result.get('deleted_chunks', 0)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/ingest/batch")
async def ingest_batch_documents(files: List[UploadFile] = File(...)):
    """
    Ingest multiple documents in a single request
    
    - **files**: List of document files to ingest
    """
    try:
        results = []
        total_chunks = 0
        
        for file in files:
            try:
                # Process each file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                    shutil.copyfileobj(file.file, temp_file)
                    temp_file_path = temp_file.name
                
                try:
                    result = ingestion_service.ingest_document(temp_file_path)
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "chunks": result['chunks']
                    })
                    total_chunks += result['chunks']
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Batch ingestion completed. {len([r for r in results if r['success']])} files processed",
                "total_chunks_created": total_chunks,
                "results": results
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch ingestion: {str(e)}")
