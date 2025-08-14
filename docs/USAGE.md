# Usage Guide

## Getting Started

### 1. System Access

Once your AI Support Bot is running, you can access it through:

- **API Endpoints**: RESTful API at `http://localhost:8000/api/v1/`
- **Interactive Documentation**: Swagger UI at `http://localhost:8000/docs`
- **Health Check**: System status at `http://localhost:8000/health`

### 2. First Steps

1. **Check System Health**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Ingest a Sample Document**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ingest/file" \
     -F "file=@samples/sample_doc.pdf" \
     -F "chunk_size=1000" \
     -F "chunk_overlap=200"
   ```

3. **Start a Chat Session**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello! What can you help me with?", "session_id": "my_session_123"}'
   ```

## Core Features Usage

### 1. Document-based QA (RAG)

The system can answer questions based on ingested documentation using Retrieval-Augmented Generation.

#### Example RAG Queries

**Basic Question:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is API testing?",
    "session_id": "test_session"
  }'
```

**Expected Response:**
```json
{
  "reply": "API testing is a type of software testing that validates the functionality, reliability, performance, and security of application programming interfaces (APIs). It involves testing APIs directly and as part of integration testing to ensure they meet expectations for functionality, reliability, performance, and security.",
  "sources": [
    {
      "id": "uuid-123",
      "content": "API testing involves testing APIs directly and as part of integration testing...",
      "metadata": {
        "source": "sample_doc.pdf",
        "chunk_id": 15,
        "chunk_size": 856
      },
      "score": 0.95
    }
  ],
  "tool_calls": [],
  "session_id": "test_session"
}
```

**Follow-up Question:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best practices for API testing?",
    "session_id": "test_session"
  }'
```

**Expected Response:**
```json
{
  "reply": "Based on our conversation about API testing, here are the best practices: 1) Test all endpoints and methods, 2) Validate response formats and status codes, 3) Test error handling and edge cases, 4) Use appropriate authentication and authorization, 5) Monitor performance and response times.",
  "sources": [
    {
      "id": "uuid-456",
      "content": "Best practices for API testing include comprehensive endpoint coverage...",
      "metadata": {
        "source": "sample_doc.pdf",
        "chunk_id": 23,
        "chunk_size": 892
      },
      "score": 0.87
    }
  ],
  "tool_calls": [],
  "session_id": "test_session"
}
```

#### Advanced RAG Features

**Context-Aware Responses:**
The system maintains conversation context, so you can ask follow-up questions like:
- "Tell me more about that"
- "What are the alternatives?"
- "How does this compare to other approaches?"

**Source Citations:**
Every RAG response includes:
- Source document information
- Chunk ID and size
- Similarity score
- Metadata for traceability

### 2. Tool Integration (Support Actions)

The system can perform specific support-related tasks using integrated tools.

#### Ticket Management Tools

**Create a Support Ticket:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a high priority ticket for login authentication issues",
    "session_id": "support_session"
  }'
```

**Expected Response:**
```json
{
  "reply": "I've created a high priority ticket for login authentication issues. Your ticket ID is TKT-2024-001. The ticket has been assigned to our support team and will be addressed according to the priority level.",
  "sources": [],
  "tool_calls": [
    {
      "name": "create_support_ticket",
      "args": {
        "description": "login authentication issues",
        "priority": "high"
      },
      "result": "Created ticket TKT-2024-001 with high priority"
    }
  ],
  "session_id": "support_session"
}
```

**Check Ticket Status:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of ticket TKT-2024-001?",
    "session_id": "support_session"
  }'
```

**Expected Response:**
```json
{
  "reply": "Ticket TKT-2024-001 is currently Open with high priority. It was created for login authentication issues and is awaiting assignment to a support engineer.",
  "sources": [],
  "tool_calls": [
    {
      "name": "get_ticket_status",
      "args": {
        "ticket_id": "TKT-2024-001"
      },
      "result": "Ticket TKT-2024-001 is Open (Priority: high)"
    }
  ],
  "session_id": "support_session"
}
```

**Get Detailed Ticket Information:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all details for ticket TKT-2024-001",
    "session_id": "support_session"
  }'
```

**Expected Response:**
```json
{
  "reply": "Here are the complete details for ticket TKT-2024-001:\n\n- **Ticket ID**: TKT-2024-001\n- **Description**: login authentication issues\n- **Priority**: high\n- **Status**: Open\n- **Created**: 2024-12-15 10:30:00 UTC\n\nThis ticket is currently in the Open status and will be processed according to its high priority level.",
  "sources": [],
  "tool_calls": [
    {
      "name": "get_ticket_details",
      "args": {
        "ticket_id": "TKT-2024-001"
      },
      "result": "Ticket TKT-2024-001: Status=Open, Priority=high, Description=login authentication issues, Created=2024-12-15 10:30:00 UTC"
    }
  ],
  "session_id": "support_session"
}
```

#### Natural Language Tool Usage

The system understands natural language requests and automatically extracts parameters:

**Implicit Priority:**
- "Create a ticket for server downtime" → Medium priority (default)
- "I need urgent help with database errors" → High priority
- "Minor UI bug report" → Low priority

**Context-Aware Requests:**
- "What's the status of that ticket?" → References previous ticket
- "Create another one for the same issue" → Uses context from previous request
- "Update the priority to critical" → Modifies existing ticket

### 3. Agent Orchestration

The system automatically determines whether to use RAG or tools based on user intent.

#### Intent Classification Examples

**RAG Intent (Document Questions):**
- "What is the deployment process?"
- "How do I configure the database?"
- "What are the system requirements?"
- "Explain the authentication flow"

**Tool Intent (Actions):**
- "Create a ticket for..."
- "Check the status of ticket..."
- "Show me ticket details..."
- "Raise an issue about..."

**Mixed Intent (Combined):**
- "What are the best practices for monitoring? Also create a ticket to track this discussion."

#### Response Composition

The system provides structured responses with:
- **Reply**: Human-readable response
- **Sources**: Relevant document chunks (for RAG)
- **Tool Calls**: Executed actions and results (for tools)
- **Session ID**: Conversation tracking

### 4. Memory Management

#### Session-Based Conversations

**Start New Session:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with our API integration",
    "session_id": "api_integration_help"
  }'
```

**Continue Session:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you elaborate on the authentication part?",
    "session_id": "api_integration_help"
  }'
```

**View Session History:**
```bash
curl "http://localhost:8000/api/v1/chat/session/api_integration_help/history"
```

**Clear Session:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/chat/session/api_integration_help"
```

#### Memory Features

- **Context Preservation**: System remembers previous questions and answers
- **Tool State**: Remembers created tickets and their IDs
- **Conversation Flow**: Maintains logical conversation progression
- **Session Isolation**: Different sessions don't interfere with each other

## Document Ingestion

### Supported Formats

- **PDF**: `.pdf` files (text extraction)
- **Markdown**: `.md` files
- **Text**: `.txt` files
- **Word**: `.docx` files
- **Rich Text**: `.rtf` files

### Ingestion Process

**Upload Document:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@path/to/your/document.pdf" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200"
```

**Ingest from Server Path:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/path" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/samples/product_manual.pdf",
    "chunk_size": 800,
    "chunk_overlap": 120
  }'
```

**Check Ingestion Status:**
```bash
curl "http://localhost:8000/api/v1/ingest/status"
```

### Chunking Configuration

**Optimal Settings by Document Type:**

- **Technical Documentation**: `chunk_size=1000, chunk_overlap=200`
- **User Manuals**: `chunk_size=800, chunk_overlap=150`
- **API Documentation**: `chunk_size=1200, chunk_overlap=250`
- **General Text**: `chunk_size=600, chunk_overlap=100`

## Advanced Usage Patterns

### 1. Multi-Step Workflows

**Document Analysis + Ticket Creation:**
```bash
# Step 1: Ask about a process
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the deployment process for our application?",
    "session_id": "deployment_workflow"
  }'

# Step 2: Create ticket for issues found
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a high priority ticket to track the deployment automation improvements mentioned",
    "session_id": "deployment_workflow"
  }'

# Step 3: Follow up on the ticket
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of that deployment ticket?",
    "session_id": "deployment_workflow"
  }'
```

### 2. Batch Operations

**Multiple Document Ingestion:**
```bash
# Create a script for batch ingestion
for file in docs/*.pdf; do
  echo "Ingesting $file..."
  curl -X POST "http://localhost:8000/api/v1/ingest/file" \
    -F "file=@$file" \
    -F "chunk_size=1000" \
    -F "chunk_overlap=200"
  echo "Done with $file"
done
```

**Bulk Ticket Creation:**
```bash
# Create multiple tickets from a list
issues=(
  "Database connection timeout issues"
  "API rate limiting configuration"
  "User authentication flow problems"
  "Performance monitoring setup"
)

for issue in "${issues[@]}"; do
  curl -X POST "http://localhost:8000/api/v1/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Create a medium priority ticket for: $issue\", \"session_id\": \"batch_creation\"}"
done
```

### 3. Integration Patterns

**Webhook Integration:**
```bash
# Set up webhook for ticket updates
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a ticket for the webhook integration issue reported by the monitoring system",
    "session_id": "monitoring_integration"
  }'
```

**API Client Integration:**
```python
import requests

class AISupportClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    def start_session(self):
        response = requests.post(f"{self.base_url}/api/v1/chat", json={
            "message": "Start new session",
            "session_id": f"client_{id(self)}"
        })
        self.session_id = response.json()["session_id"]
        return response.json()
    
    def ask_question(self, question):
        response = requests.post(f"{self.base_url}/api/v1/chat", json={
            "message": question,
            "session_id": self.session_id
        })
        return response.json()
    
    def create_ticket(self, description, priority="medium"):
        response = requests.post(f"{self.base_url}/api/v1/chat", json={
            "message": f"Create a {priority} priority ticket for: {description}",
            "session_id": self.session_id
        })
        return response.json()

# Usage
client = AISupportClient()
client.start_session()
response = client.ask_question("What are the system requirements?")
ticket = client.create_ticket("Need help with configuration", "high")
```

## Best Practices

### 1. Session Management

- **Use Descriptive Session IDs**: `user_john_api_integration`, `project_alpha_deployment`
- **Keep Sessions Focused**: One session per topic or project
- **Clear Sessions Regularly**: Remove old sessions to free memory
- **Reuse Sessions**: Continue conversations within the same context

### 2. Document Ingestion

- **Optimize Chunk Sizes**: Larger chunks for technical docs, smaller for general text
- **Use Descriptive Filenames**: `api_v2_integration_guide.pdf` vs `doc1.pdf`
- **Batch Process**: Ingest related documents together
- **Validate Content**: Check that important information is preserved after chunking

### 3. Query Formulation

- **Be Specific**: "What is the OAuth2 flow for user authentication?" vs "How does auth work?"
- **Use Natural Language**: The system understands conversational queries
- **Provide Context**: "Based on the deployment guide, what are the prerequisites?"
- **Ask Follow-ups**: Build on previous responses for deeper understanding

### 4. Tool Usage

- **Clear Descriptions**: "Create a ticket for database connection timeout issues" vs "Create ticket"
- **Specify Priority**: Always mention priority when creating tickets
- **Reference Context**: "Update the priority of that ticket to critical"
- **Verify Actions**: Check ticket status after creation

## Troubleshooting

### Common Issues

**1. No Relevant Results**
- Check if documents are properly ingested
- Verify chunk sizes are appropriate
- Try rephrasing the question
- Check ingestion status: `GET /api/v1/ingest/status`

**2. Tool Execution Errors**
- Verify ticket IDs exist
- Check tool parameter extraction
- Review system logs for errors
- Ensure proper session context

**3. Memory Issues**
- Clear old sessions
- Reduce chunk sizes
- Check system resource usage
- Restart services if needed

**4. Performance Issues**
- Optimize chunk sizes
- Use GPU acceleration if available
- Monitor database performance
- Check vector index optimization

### Debug Commands

```bash
# Check system health
curl http://localhost:8000/health

# View service logs
docker-compose logs -f app

# Check database status
docker-compose exec db pg_isready -U trantor

# Verify document ingestion
docker-compose exec db psql -U trantor -d trantor_db -c "SELECT COUNT(*) FROM ai.documents;"

# Check ticket status
docker-compose exec db psql -U trantor -d trantor_db -c "SELECT * FROM ai.tickets;"
```

## Performance Optimization

### 1. Query Optimization

- **Use Specific Keywords**: Include relevant terms from your documents
- **Limit Scope**: Ask focused questions rather than broad ones
- **Leverage Context**: Build on previous questions for better results

### 2. System Optimization

- **GPU Acceleration**: Enable GPU layers for faster LLM inference
- **Database Tuning**: Optimize PostgreSQL settings for vector operations
- **Model Selection**: Use appropriate model sizes for your use case
- **Chunk Optimization**: Balance chunk size vs. retrieval accuracy

### 3. Monitoring

- **Response Times**: Track query performance
- **Memory Usage**: Monitor system resources
- **Accuracy**: Evaluate response quality
- **User Feedback**: Collect usage patterns

## Future Enhancements

### Planned Features

- **Streaming Responses**: Real-time response generation
- **Advanced Memory**: Long-term memory with summarization
- **Multi-modal Support**: Image and document processing
- **Advanced RAG**: Hybrid search with keyword + semantic
- **Custom Tools**: Extensible tool definition system

### Customization Options

- **Prompt Engineering**: Customize system prompts
- **Model Selection**: Choose different LLM models
- **Embedding Models**: Select alternative embedding models
- **Tool Extensions**: Add custom support tools
- **Integration APIs**: Connect with external systems

---

This usage guide covers the core functionality of the AI Support Bot. For technical details, refer to the Architecture and Setup documentation. For support, check the troubleshooting section or review the system logs.
