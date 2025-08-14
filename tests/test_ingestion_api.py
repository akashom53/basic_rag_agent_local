import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import tempfile

client = TestClient(app)

class TestIngestionAPI:
    """Test cases for the document ingestion API"""
    
    def test_ingest_status_endpoint(self):
        """Test the ingestion status endpoint"""
        response = client.get("/api/v1/ingest/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_chunks" in data
        assert "available_documents" in data
        # last_ingestion will be None in current schema (no created_at column)
        assert "last_ingestion" in data
    
    def test_ingest_document_path(self):
        """Test ingesting a document from a file path"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for ingestion testing.")
            temp_file_path = f.name
        
        try:
            request_data = {
                "file_path": temp_file_path,
                "chunk_size": 500,
                "chunk_overlap": 100
            }
            
            response = client.post("/api/v1/ingest/path", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            assert data["chunks_created"] > 0
            assert data["file_path"] == temp_file_path
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_ingest_document_path_not_found(self):
        """Test ingesting a non-existent document path"""
        request_data = {
            "file_path": "/nonexistent/file.txt"
        }
        
        response = client.post("/api/v1/ingest/path", json=request_data)
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]
    
    def test_ingest_document_path_missing_path(self):
        """Test ingesting without providing a file path"""
        request_data = {}
        
        response = client.post("/api/v1/ingest/path", json=request_data)
        assert response.status_code == 400
        assert "file_path is required" in response.json()["detail"]
    
    def test_clear_all_documents(self):
        """Test clearing all documents"""
        response = client.delete("/api/v1/ingest/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "cleared" in data["message"]
    
    def test_delete_specific_document(self):
        """Test deleting a specific document"""
        # First ingest a document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document for deletion testing.")
            temp_file_path = f.name
        
        try:
            # Ingest the document
            request_data = {"file_path": temp_file_path}
            ingest_response = client.post("/api/v1/ingest/path", json=request_data)
            assert ingest_response.status_code == 200
            
            # Get the document ID from the ingested document
            status_response = client.get("/api/v1/ingest/status")
            assert status_response.status_code == 200
            
            documents = status_response.json()["available_documents"]
            if documents:
                doc_id = documents[0]["doc_id"]
                
                # Delete the document
                delete_response = client.delete(f"/api/v1/ingest/document/{doc_id}")
                assert delete_response.status_code == 200
                
                data = delete_response.json()
                assert data["success"] == True
                assert data["deleted_chunks"] > 0
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_delete_nonexistent_document(self):
        """Test deleting a non-existent document"""
        response = client.delete("/api/v1/ingest/document/nonexistent")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["deleted_chunks"] == 0

def test_ingestion_integration():
    """Integration test for the complete ingestion workflow"""
    # Test the complete flow: ingest → check status → clear
    
    # 1. Check initial status
    status_response = client.get("/api/v1/ingest/status")
    assert status_response.status_code == 200
    initial_chunks = status_response.json()["total_chunks"]
    
    # 2. Ingest a test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Integration test document with multiple sentences. This should create multiple chunks.")
        temp_file_path = f.name
    
    try:
        request_data = {"file_path": temp_file_path, "chunk_size": 300, "chunk_overlap": 50}
        ingest_response = client.post("/api/v1/ingest/path", json=request_data)
        assert ingest_response.status_code == 200
        
        # 3. Verify chunks were created
        status_response = client.get("/api/v1/ingest/status")
        assert status_response.status_code == 200
        final_chunks = status_response.json()["total_chunks"]
        
        # Should have more chunks after ingestion
        assert final_chunks > initial_chunks
        
        # 4. Clear all documents
        clear_response = client.delete("/api/v1/ingest/clear")
        assert clear_response.status_code == 200
        
        # 5. Verify everything was cleared
        status_response = client.get("/api/v1/ingest/status")
        assert status_response.status_code == 200
        assert status_response.json()["total_chunks"] == 0
        
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    # Run basic tests
    test_ingestion = TestIngestionAPI()
    
    print("🧪 Testing Ingestion API...")
    
    # Test status endpoint
    test_ingestion.test_ingest_status_endpoint()
    print("✅ Status endpoint test passed")
    
    # Test document path ingestion
    test_ingestion.test_ingest_document_path()
    print("✅ Document path ingestion test passed")
    
    # Test error handling
    test_ingestion.test_ingest_document_path_not_found()
    print("✅ Error handling test passed")
    
    # Test integration
    test_ingestion_integration()
    print("✅ Integration test passed")
    
    print("🎉 All ingestion API tests passed!")
