# Document Ingestion API Guide

This guide explains how to use the new document ingestion API endpoints for the AI Support Bot.

## 🚀 **Available Endpoints**

### **1. Ingest Document from File Path**
**POST** `/api/v1/ingest/path`

Ingest a document from a server-side file path.

**Request Body:**
```json
{
  "file_path": "/path/to/document.pdf",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully ingested document.pdf",
  "document_ingested": 1,
  "chunks_created": 15,
  "file_path": "/path/to/document.pdf",
  "processing_time": 2.45
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/path" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "samples/api_testing_guide.md",
    "chunk_size": 800,
    "chunk_overlap": 150
  }'
```

### **2. Ingest Document via File Upload**
**POST** `/api/v1/ingest/file`

Upload and ingest a document file directly.

**Form Data:**
- `file`: Document file (PDF, MD, TXT, DOCX, DOC)
- `chunk_size`: Chunk size in characters (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@document.pdf" \
  -F "chunk_size=800" \
  -F "chunk_overlap=150"
```

### **3. Batch Document Ingestion**
**POST** `/api/v1/ingest/batch`

Ingest multiple documents in a single request.

**Form Data:**
- `files`: Array of document files

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.md" \
  -F "files=@doc3.txt"
```

### **4. Get Ingestion Status**
**GET** `/api/v1/ingest/status`

Get statistics about ingested documents and chunks.

**Response:**
```json
{
  "total_documents": 5,
  "total_chunks": 127,
  "last_ingestion": null,
  "available_documents": [
    {
      "doc_id": "api_testing_guide.md",
      "chunk_count": 25
    }
  ]
}
```

**Note:** `last_ingestion` will be `null` in the current schema as it doesn't include timestamp tracking. To enable this feature, you would need to add a `created_at` column to the `ai.documents` table.

**Example Usage:**
```bash
curl "http://localhost:8000/api/v1/ingest/status"
```

### **5. Clear All Documents**
**DELETE** `/api/v1/ingest/clear`

Remove all ingested documents and chunks from the vector database.

**Response:**
```json
{
  "success": true,
  "message": "All documents and chunks cleared successfully",
  "cleared_chunks": 127
}
```

**Example Usage:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/ingest/clear"
```

### **6. Delete Specific Document**
**DELETE** `/api/v1/ingest/document/{document_id}`

Remove a specific document and all its chunks.

**Response:**
```json
{
  "success": true,
  "message": "Document api_testing_guide.md deleted successfully",
  "deleted_chunks": 25
}
```

**Example Usage:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/ingest/document/api_testing_guide.md"
```

## 📁 **Supported File Types**

- **PDF** (`.pdf`)
- **Markdown** (`.md`)
- **Text** (`.txt`)
- **Word Document** (`.docx`, `.doc`)

## ⚙️ **Configuration Options**

### **Chunking Parameters**

- **chunk_size**: Number of characters per text chunk (default: 1000)
- **chunk_overlap**: Number of overlapping characters between chunks (default: 200)

### **Recommended Settings**

| Document Type | chunk_size | chunk_overlap | Use Case |
|---------------|------------|---------------|----------|
| **Technical Docs** | 800-1000 | 150-200 | Detailed information retrieval |
| **General Text** | 1000-1500 | 200-300 | Broader context |
| **Code/Logs** | 500-800 | 100-150 | Precise code snippets |

## 🔄 **Complete Workflow Example**

### **Step 1: Check Current Status**
```bash
curl "http://localhost:8000/api/v1/ingest/status"
```

### **Step 2: Ingest Documents**
```bash
# Ingest a markdown file
curl -X POST "http://localhost:8000/api/v1/ingest/path" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "samples/api_testing_guide.md"}'

# Upload a PDF file
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@user_manual.pdf"
```

### **Step 3: Verify Ingestion**
```bash
curl "http://localhost:8000/api/v1/ingest/status"
```

### **Step 4: Test RAG Queries**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is API testing?"}'
```

## 🧪 **Testing the API**

### **Run the Test Suite**
```bash
# Run all ingestion tests
python -m pytest tests/test_ingestion_api.py -v

# Run specific test
python tests/test_ingestion_api.py
```

### **Manual Testing with Sample Documents**
```bash
# Test with the existing sample document
curl -X POST "http://localhost:8000/api/v1/ingest/path" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "samples/api_testing_guide.md"}'
```

## ⚠️ **Important Notes**

1. **File Paths**: Use absolute paths or paths relative to the container working directory
2. **Memory Usage**: Large documents may consume significant memory during processing
3. **Processing Time**: Depends on document size and chunking parameters
4. **Cleanup**: Temporary files are automatically cleaned up after processing
5. **Error Handling**: All endpoints return appropriate HTTP status codes and error messages

## 🔍 **Troubleshooting**

### **Common Issues**

1. **File Not Found**: Ensure the file path is correct and accessible
2. **Permission Denied**: Check file permissions and container access
3. **Memory Errors**: Reduce chunk size for very large documents
4. **Processing Failures**: Check container logs for detailed error information

### **Debug Commands**
```bash
# Check container logs
docker-compose logs app

# Check database connection
docker-compose exec app python -c "from app.rag.vectorstore import PostgreSQLVectorStore; print('DB connection OK')"

# Verify file access
docker-compose exec app ls -la samples/
```

## 📚 **Integration with Existing Features**

The ingestion API integrates seamlessly with:
- **Chat API**: Ingested documents are automatically available for RAG queries
- **Vector Store**: Documents are stored in PostgreSQL with pgvector
- **Embedding Service**: Automatic text embedding generation
- **Chunking Service**: Intelligent document segmentation

## 🔧 **Schema Compatibility**

### **Current Schema (ai.documents table)**
```sql
CREATE TABLE ai.documents (
    id UUID PRIMARY KEY,
    doc_id TEXT,
    chunk_id INT,
    content TEXT,
    metadata JSONB,
    embedding vector(384)
);
```

### **Features Available**
- ✅ Document ingestion and storage
- ✅ Chunking and embedding
- ✅ RAG queries and retrieval
- ✅ Document management (delete, clear)
- ✅ Basic statistics (counts, document lists)

### **Features Not Available (Schema Limitations)**
- ❌ Timestamp tracking (created_at, updated_at)
- ❌ Ingestion history
- ❌ Document age information

### **To Enable Additional Features**
If you want timestamp tracking, you can add:
```sql
ALTER TABLE ai.documents ADD COLUMN created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE ai.documents ADD COLUMN updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP;
```

This creates a complete document processing and retrieval pipeline for your AI Support Bot!
