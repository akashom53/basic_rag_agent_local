# Trantor AI Support Bot - Product Documentation

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Security](#security)
9. [Performance](#performance)
10. [Deployment](#deployment)

## Overview

The Trantor AI Support Bot is an intelligent assistant designed to help support teams answer product-related queries and manage support tickets efficiently. Built with modern AI technologies including Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs), the system provides accurate, context-aware responses based on internal documentation.

### Key Features

- **Document-based QA**: Answer questions using ingested product documentation
- **Intelligent Ticket Management**: Create and track support tickets automatically
- **Context-Aware Conversations**: Maintain conversation history and context
- **Multi-format Support**: Handle PDF, Markdown, Word, and text documents
- **GPU Acceleration**: Optional GPU support for faster inference
- **RESTful API**: Easy integration with existing systems

### Use Cases

- **Support Agent Assistance**: Quick answers to common product questions
- **Documentation Search**: Find relevant information across multiple documents
- **Ticket Automation**: Streamlined ticket creation and management
- **Knowledge Base**: Centralized access to product information
- **Training Support**: Help new team members learn product details

## System Architecture

### Core Components

The AI Support Bot consists of several interconnected components:

1. **FastAPI Backend**: RESTful API layer with automatic documentation
2. **RAG Pipeline**: Document processing, embedding, and retrieval system
3. **Agent Orchestrator**: Intelligent routing between RAG and tool-based responses
4. **Vector Database**: PostgreSQL with pgvector for semantic search
5. **LLM Integration**: Ollama-based local models with GPU acceleration
6. **Memory Management**: Session-based conversation history

### Data Flow

```
User Query → Intent Classification → Route Decision → Execute Action → Compose Response
     ↓              ↓                    ↓              ↓              ↓
  Chat API    Intent Router        Orchestrator    RAG/Tools      Response
  /api/v1/chat  (LLM/Pattern)       (Decision)      (Execute)      (Format)
```

### Technology Stack

- **Backend Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 16 with pgvector extension
- **Vector Embeddings**: BAAI/bge-small-en-v1.5
- **LLM Provider**: Ollama with local models
- **Containerization**: Docker with Docker Compose
- **Memory Management**: LangChain integration

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- NVIDIA Docker runtime (for GPU support)
- Minimum 8GB RAM (16GB recommended)
- 10GB+ free disk space

### Quick Start

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd tantorinc
   ```

2. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start Services**
   ```bash
   # Linux/macOS
   chmod +x start.sh
   ./start.sh
   
   # Windows
   start.bat
   ```

4. **Verify Deployment**
   ```bash
   curl http://localhost:8000/health
   open http://localhost:8000/docs
   ```

### Local Development Setup

For developers who prefer local development:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (if not using Docker)
docker run -d --name pgvector -e POSTGRES_PASSWORD=password -p 5432:5432 pgvector/pgvector:pg16

# Run application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://trantor:trantor_pass@db:5432/trantor_db` |
| `EMBED_MODEL` | Embedding model name | `BAAI/bge-small-en-v1.5` |
| `LLM_MODEL` | LLM model identifier | `ollama:qwen2.5:7b-instruct` |
| `GPU_LAYERS` | Number of GPU layers for Ollama | `20` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

### Database Configuration

The system uses PostgreSQL with the pgvector extension for vector operations:

```sql
-- Core documents table
CREATE TABLE ai.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id TEXT,                    -- Source document identifier
    chunk_id INT,                   -- Chunk sequence number
    content TEXT NOT NULL,          -- Text content
    metadata JSONB,                 -- Document metadata
    embedding vector(384)           -- Normalized embedding vector
);

-- Support tickets table
CREATE TABLE ai.tickets (
    id TEXT PRIMARY KEY,            -- Ticket identifier
    description TEXT NOT NULL,      -- Issue description
    priority TEXT NOT NULL,         -- Priority level
    status TEXT NOT NULL,           -- Current status
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Model Configuration

#### Embedding Models

- **BAAI/bge-small-en-v1.5**: Fast, lightweight (384 dimensions)
- **BAAI/bge-base-en-v1.5**: Higher quality, slower (768 dimensions)
- **BAAI/bge-m3**: Multilingual support (1024 dimensions)

#### LLM Models

- **qwen2.5:7b-instruct**: Balanced performance and quality
- **qwen2.5:3b-instruct**: Fast inference, smaller memory footprint
- **llama3.1:8b-instruct-q4**: Quantized for efficiency
- **qwen2.5:14b-instruct**: Higher quality, requires more resources

## API Reference

### Authentication

Currently, the API operates without authentication for development purposes. Production deployments should implement proper authentication mechanisms.

### Rate Limiting

Default rate limits:
- **Chat API**: 100 requests per minute per session
- **Ingestion API**: 10 requests per minute
- **Ticket API**: 50 requests per minute

### Endpoints

#### Chat Interface

**POST** `/api/v1/chat`
Main chat endpoint for user interactions.

**Request Body:**
```json
{
  "message": "What is the deployment process?",
  "session_id": "user_session_123"
}
```

**Response:**
```json
{
  "reply": "The deployment process involves...",
  "sources": [
    {
      "id": "uuid-123",
      "content": "Deployment process includes...",
      "metadata": {
        "source": "deployment_guide.pdf",
        "chunk_id": 5
      },
      "score": 0.95
    }
  ],
  "tool_calls": [],
  "session_id": "user_session_123"
}
```

**GET** `/api/v1/chat/session/{session_id}/history`
Retrieve conversation history for a session.

**DELETE** `/api/v1/chat/session/{session_id}`
Clear conversation history for a session.

#### Document Ingestion

**POST** `/api/v1/ingest/file`
Upload and ingest a document file.

**Form Data:**
- `file`: Document file (PDF, MD, TXT, DOCX)
- `chunk_size`: Size of text chunks (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)

**POST** `/api/v1/ingest/path`
Ingest a document from a server path.

**Request Body:**
```json
{
  "file_path": "/path/to/document.pdf",
  "chunk_size": 800,
  "chunk_overlap": 120
}
```

**GET** `/api/v1/ingest/status`
Get ingestion statistics and status.

#### Ticket Management

**POST** `/api/v1/tickets`
Create a new support ticket.

**Request Body:**
```json
{
  "description": "Database connection timeout issues",
  "priority": "high"
}
```

**GET** `/api/v1/tickets/{ticket_id}`
Get ticket details by ID.

### Response Formats

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {
    // Response-specific data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

Error responses include:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "message",
      "issue": "Field is required"
    }
  },
  "timestamp": "2024-12-15T10:30:00Z"
}
```

## Troubleshooting

### Common Issues

#### 1. Service Startup Problems

**Database Connection Failed**
```bash
# Check database status
docker-compose exec db pg_isready -U trantor

# Verify environment variables
docker-compose exec app env | grep DATABASE

# Check database logs
docker-compose logs db
```

**Ollama Service Unavailable**
```bash
# Check Ollama status
docker-compose exec ollama ollama list

# Verify model download
docker-compose exec ollama ollama pull qwen2.5:7b-instruct

# Check Ollama logs
docker-compose logs ollama
```

#### 2. Performance Issues

**Slow Response Times**
- Reduce chunk sizes for faster processing
- Enable GPU acceleration if available
- Optimize database indexes
- Use quantized models

**Memory Issues**
```bash
# Check resource usage
docker stats

# Reduce GPU layers
export GPU_LAYERS=10

# Use smaller models
export LLM_MODEL=ollama:qwen2.5:3b-instruct
```

#### 3. Document Ingestion Problems

**File Format Not Supported**
- Ensure file has supported extension (.pdf, .md, .txt, .docx)
- Check file is not corrupted
- Verify file permissions

**Chunking Issues**
- Adjust chunk size and overlap parameters
- Check document encoding (UTF-8 recommended)
- Verify document contains extractable text

### Debug Commands

```bash
# System health check
curl http://localhost:8000/health

# Service status
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f ollama
docker-compose logs -f db

# Database queries
docker-compose exec db psql -U trantor -d trantor_db -c "SELECT COUNT(*) FROM ai.documents;"
docker-compose exec db psql -U trantor -d trantor_db -c "SELECT * FROM ai.tickets LIMIT 5;"

# Model verification
docker-compose exec ollama ollama list
docker-compose exec ollama ollama show qwen2.5:7b-instruct
```

## Best Practices

### Document Management

1. **File Organization**
   - Use descriptive filenames
   - Group related documents together
   - Maintain consistent naming conventions
   - Version control important documents

2. **Chunking Strategy**
   - Technical docs: 800-1000 characters
   - User manuals: 600-800 characters
   - API docs: 1000-1200 characters
   - Overlap: 15-20% of chunk size

3. **Content Quality**
   - Ensure documents are up-to-date
   - Use clear, concise language
   - Include relevant examples
   - Maintain consistent terminology

### API Usage

1. **Session Management**
   - Use descriptive session IDs
   - Keep sessions focused on specific topics
   - Clear old sessions regularly
   - Reuse sessions for related conversations

2. **Query Formulation**
   - Be specific and clear
   - Use natural language
   - Provide context when needed
   - Ask follow-up questions

3. **Error Handling**
   - Implement proper retry logic
   - Handle rate limiting gracefully
   - Log errors for debugging
   - Provide user-friendly error messages

### Performance Optimization

1. **System Tuning**
   - Enable GPU acceleration when available
   - Optimize database settings
   - Use appropriate model sizes
   - Monitor resource usage

2. **Caching Strategy**
   - Cache frequently accessed documents
   - Implement response caching
   - Use CDN for static assets
   - Optimize database queries

## Security

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

### Network Security

- **Firewall Configuration**: Restrict access to necessary ports
- **SSL/TLS**: Enable for production deployments
- **VPN Access**: Consider VPN for remote access
- **IP Whitelisting**: Restrict access to known IP ranges

## Performance

### Benchmarks

**Response Times (CPU Mode):**
- RAG queries: 2-4 seconds
- Tool execution: 200-500ms
- Intent classification: 500ms-1s
- Document ingestion: 20-40s per MB

**Response Times (GPU Mode):**
- RAG queries: 1-2 seconds
- Tool execution: 100-300ms
- Intent classification: 200-500ms
- Document ingestion: 10-25s per MB

### Resource Requirements

**CPU Mode:**
- RAM: 16GB minimum, 32GB recommended
- CPU: 4+ cores, 8+ cores recommended
- Storage: 10GB+ for models and data

**GPU Mode:**
- VRAM: 8GB+ minimum, 16GB+ recommended
- RAM: 16GB+ minimum, 32GB+ recommended
- Storage: 20GB+ for models and data

### Scaling Considerations

- **Horizontal Scaling**: Stateless API services
- **Database Scaling**: Read replicas for vector search
- **Model Scaling**: Multiple Ollama instances
- **Memory Scaling**: Redis backend for session storage

## Deployment

### Production Deployment

1. **Environment Preparation**
   ```bash
   # Set production environment variables
   export NODE_ENV=production
   export DATABASE_URL=postgresql://user:pass@prod-db:5432/ai_support
   export LLM_MODEL=ollama:qwen2.5:7b-instruct-q4
   ```

2. **Security Hardening**
   - Enable authentication
   - Configure SSL/TLS certificates
   - Set up firewall rules
   - Implement monitoring

3. **Performance Tuning**
   - Optimize database settings
   - Configure load balancing
   - Set up caching layers
   - Monitor system metrics

### Cloud Deployment

**Google Cloud Platform:**
```bash
# Create GPU instance
gcloud compute instances create ai-support-bot \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator="type=nvidia-tesla-t4,count=1" \
  --image-family=debian-11-gpu

# Deploy application
gcloud compute scp --recurse ./ tantorinc:~/app
gcloud compute ssh tantorinc --zone=us-central1-a
cd ~/app && docker-compose up -d
```

**AWS EC2:**
```bash
# Launch GPU instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type p3.2xlarge \
  --key-name your-key-pair

# Deploy application
scp -r ./ ec2-user@your-instance-ip:~/app
ssh ec2-user@your-instance-ip
cd ~/app && docker-compose up -d
```

### Monitoring & Maintenance

1. **Health Monitoring**
   - Application health checks
   - Database performance monitoring
   - LLM service availability
   - Resource usage tracking

2. **Backup & Recovery**
   - Regular database backups
   - Model file backups
   - Configuration backups
   - Disaster recovery procedures

3. **Updates & Upgrades**
   - Regular security updates
   - Model updates
   - Application updates
   - Dependency updates

---

This documentation provides comprehensive information about the Trantor AI Support Bot. For additional support or questions, please refer to the troubleshooting section or contact the development team.

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: Production Ready
