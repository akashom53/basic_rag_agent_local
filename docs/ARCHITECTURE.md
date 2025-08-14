# Architecture Documentation

## System Overview

The AI Support Bot is built as a microservices architecture with the following key components:

- **FastAPI Backend**: RESTful API layer with automatic OpenAPI documentation
- **RAG Pipeline**: Document processing, embedding, and retrieval system
- **Agent Orchestrator**: Intelligent routing between RAG and tool-based responses
- **Vector Database**: PostgreSQL with pgvector extension for semantic search
- **LLM Integration**: Ollama-based local models with GPU acceleration
- **Memory Management**: Session-based conversation history using LangChain

## Component Architecture

### 1. API Layer (`app/api/`)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat API      │    │  Ingestion API  │    │  Tickets API    │
│   /api/v1/chat  │    │ /api/v1/ingest  │    │ /api/v1/tickets │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI App   │
                    │   (app/main.py) │
                    └─────────────────┘
```

**Key Features:**
- Automatic request/response validation with Pydantic
- CORS middleware for cross-origin requests
- Health check endpoints for monitoring
- Structured error handling and logging

### 2. RAG Pipeline (`app/rag/`)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Document   │    │  Document   │    │  Embedding  │    │  Vector     │
│   Loader    │───▶│  Chunker    │───▶│  Generator  │───▶│   Store     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**Document Loader (`loader.py`):**
- Supports multiple file formats: PDF, Markdown, TXT, DOCX
- Automatic format detection and appropriate parser selection
- Metadata extraction and preservation

**Document Chunker (`chunker.py`):**
- Recursive text splitting with configurable chunk size and overlap
- Sentence-aware boundary detection
- Metadata preservation across chunks

**Embedding Generator (`embedder.py`):**
- Uses BAAI/bge-small-en-v1.5 model via sentence-transformers
- Automatic normalization for cosine similarity
- Batch processing for efficiency

**Vector Store (`vectorstore.py`):**
- PostgreSQL + pgvector for production-ready vector operations
- Efficient similarity search with ANN indexes
- Upsert operations for document updates

### 3. Agent System (`app/agent/`)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Intent Router  │    │   Orchestrator  │    │     Tools       │
│                 │    │                 │    │                 │
│ • LLM-based     │───▶│ • RAG Handler   │───▶│ • Ticket Service│
│ • Pattern-based │    │ • Tool Handler  │    │ • Status Check  │
│ • Fallback      │    │ • Memory Mgmt   │    │ • Creation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Intent Router (`intent_router.py`):**
- Primary: LLM-based intent classification with structured output
- Fallback: Pattern-based heuristics for reliability
- Intent types: RAG_QUESTION, CREATE_TICKET, GET_TICKET_STATUS, ANALYZE_TICKETS

**Orchestrator (`orchestrator.py`):**
- Main coordination point for all agent operations
- Handles message routing and response composition
- Integrates RAG, tools, and memory services

**Tools (`tools.py`):**
- LangChain tool definitions for ticket operations
- Automatic parameter extraction and validation
- Structured response formatting

### 4. LLM Integration (`app/llm/`)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  LangChain      │    │     Ollama      │    │   Fallback      │
│   Provider      │───▶│   Integration   │───▶│   Provider      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**LangChain Provider (`langchain_provider.py`):**
- Ollama integration via langchain_ollama
- GPU layer configuration for performance
- Structured output for intent classification

**Prompt Templates (`prompts.py`):**
- System prompts for different use cases
- Context-aware user prompts
- Memory integration templates

### 5. Memory Management (`app/agent/memory.py`)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Session Store  │    │  LangChain      │    │  Memory         │
│                 │    │   Memory        │    │  Variables      │
│ • Session ID    │───▶│ • Buffer        │───▶│ • Chat History  │
│ • User Messages │    │ • Window        │    │ • Context       │
│ • AI Responses  │    │ • Persistence   │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Features:**
- Session-based conversation isolation
- Configurable memory window size
- Automatic cleanup for old sessions
- Integration with LangChain memory systems

## Data Flow

### 1. Document Ingestion Flow

```
1. File Upload → 2. Load & Parse → 3. Chunk Text → 4. Generate Embeddings → 5. Store in Vector DB
     ↓                    ↓              ↓              ↓                    ↓
  API Endpoint      Document Loader   Chunker      Embedder           PostgreSQL
  /ingest/file      (PDF/MD/TXT)    (800+120)    (bge-small)       + pgvector
```

### 2. Chat Query Flow

```
1. User Message → 2. Intent Classification → 3. Route Decision → 4. Execute Action → 5. Compose Response
      ↓                    ↓                    ↓              ↓              ↓
   Chat API          Intent Router        Orchestrator    RAG/Tools      Response
   /api/v1/chat      (LLM/Pattern)       (Decision)      (Execute)      (Format)
```

### 3. RAG Query Flow

```
1. Query → 2. Embed Query → 3. Vector Search → 4. Retrieve Context → 5. LLM Generation → 6. Response
   ↓           ↓              ↓              ↓              ↓              ↓
User Input  Embedder    Similarity      Top-k Results   Context +      Formatted
           (bge-small)   Search         (k=3)           Query → LLM    Response
```

### 4. Tool Execution Flow

```
1. Tool Intent → 2. Parameter Extraction → 3. Tool Execution → 4. Result Formatting → 5. Response
      ↓                ↓                    ↓              ↓              ↓
Intent Router      LLM/Pattern         Tool Service    Result          Response
(Classification)   (Extraction)        (Function)      (Format)        (JSON)
```

## Database Schema

### Core Tables

**`ai.documents`** - RAG Document Storage
```sql
CREATE TABLE ai.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id TEXT,                    -- Source document identifier
    chunk_id INT,                   -- Chunk sequence number
    content TEXT NOT NULL,          -- Text content
    metadata JSONB,                 -- Document metadata
    embedding vector(384)           -- Normalized embedding vector
);

-- Index for efficient similarity search
CREATE INDEX documents_embedding_ivf
    ON ai.documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

**`ai.tickets`** - Support Ticket Storage
```sql
CREATE TABLE ai.tickets (
    id TEXT PRIMARY KEY,            -- Ticket identifier
    description TEXT NOT NULL,      -- Issue description
    priority TEXT NOT NULL,         -- Priority level
    status TEXT NOT NULL,           -- Current status
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Vector Search Optimization

- **Normalized Embeddings**: All vectors are L2-normalized for cosine similarity
- **IVFFlat Index**: Approximate nearest neighbor search for performance
- **Index Tuning**: `lists` parameter optimized for dataset size
- **Query Optimization**: Efficient similarity search with `embedding <#> query_vector`

## Performance Characteristics

### Latency Targets

- **RAG Query**: < 3s (CPU), < 1.2s (GPU)
- **Tool Execution**: < 500ms
- **Intent Classification**: < 1s
- **Document Ingestion**: < 30s per MB

### Resource Requirements

- **CPU Mode**: 16GB RAM, 4+ CPU cores
- **GPU Mode**: 8GB+ VRAM, 16GB+ RAM
- **Database**: 4GB+ RAM for vector operations
- **Storage**: 10GB+ for models and data

### Scalability Considerations

- **Horizontal Scaling**: Stateless API services
- **Database Scaling**: Read replicas for vector search
- **Model Scaling**: Multiple Ollama instances
- **Memory Scaling**: Redis backend for session storage

## Security & Privacy

### Data Protection

- **Local Processing**: All data processed locally, no external API calls
- **Session Isolation**: User sessions are completely isolated
- **No Data Persistence**: Chat history stored in memory only
- **Secure Configuration**: Environment-based configuration management

### Access Control

- **API Authentication**: Ready for JWT/OAuth integration
- **Rate Limiting**: Configurable request throttling
- **Input Validation**: Comprehensive Pydantic validation
- **Error Handling**: No sensitive information in error messages

## Monitoring & Observability

### Health Checks

- **Application Health**: `/health` endpoint with service status
- **Database Health**: Connection and query performance monitoring
- **LLM Health**: Ollama service availability and model status
- **Vector Store Health**: Index performance and storage metrics

### Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Request Tracing**: Unique request IDs for debugging
- **Performance Metrics**: Response time and resource usage tracking
- **Error Tracking**: Detailed error logs with context

### Metrics

- **API Metrics**: Request count, response time, error rates
- **RAG Metrics**: Query performance, retrieval accuracy
- **Tool Metrics**: Execution time, success rates
- **Resource Metrics**: Memory usage, CPU/GPU utilization

## Deployment Architecture

### Container Structure

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │     Ollama      │
│                 │    │   + pgvector    │    │   LLM Service   │
│ • Python 3.12   │    │ • pg16 + vector │    │ • qwen2.5:7b    │
│ • Uvicorn       │    │ • Persistent    │    │ • GPU Support   │
│ • Health Check  │    │ • Health Check  │    │ • Health Check  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Network Configuration

- **Internal Communication**: Docker network for service discovery
- **External Access**: Port 8000 for API, 5432 for database
- **GPU Access**: NVIDIA Docker runtime for GPU acceleration
- **Health Monitoring**: Built-in health checks for all services

### Environment Management

- **Configuration**: Environment variables for all settings
- **Secrets**: Secure credential management
- **Environment Files**: `.env` for local development
- **Production**: Environment variable injection in containers

## Integration Points

### External Systems

- **Document Sources**: File uploads, web scraping, API feeds
- **LLM Models**: Ollama, Hugging Face, OpenAI compatibility
- **Vector Databases**: PostgreSQL + pgvector, Pinecone, Weaviate
- **Monitoring**: Prometheus, Grafana, ELK stack

### API Extensibility

- **Plugin System**: Tool-based architecture for easy extension
- **Webhook Support**: Event-driven integrations
- **Custom Models**: Pluggable LLM and embedding providers
- **Custom Tools**: Extensible tool definition system

## Future Enhancements

### Planned Features

- **Streaming Responses**: Real-time response generation
- **Advanced Memory**: Long-term memory with summarization
- **Multi-modal Support**: Image and document processing
- **Advanced RAG**: Hybrid search with keyword + semantic
- **Performance Optimization**: Model quantization and caching

### Scalability Improvements

- **Microservices**: Service decomposition for better scaling
- **Message Queues**: Async processing for high throughput
- **Distributed Storage**: Multi-node vector database support
- **Load Balancing**: Multiple API instances with load distribution
