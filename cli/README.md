# Tantor Inc AI Support Bot - CLI Interface

A powerful command-line interface for the Tantor Inc AI Support Bot, providing easy access to AI-powered support, document-based question answering, and support ticket management.

## Features

- 🤖 **AI Chat Interface** - Natural language conversations with the AI
- 📚 **Document Q&A** - Ask questions about your documentation using RAG
- 🎫 **Support Ticket Management** - Create and manage support tickets
- 💾 **Session Management** - Persistent conversation history across sessions
- 🎨 **Rich Terminal UI** - Colored output and emojis for better UX
- 🔧 **Command Shortcuts** - Quick access to common functions
- 📱 **Cross-platform** - Works on Windows, macOS, and Linux
- 📤 **Document Upload** - Easy document ingestion for RAG system

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Backend server running (optional, for full functionality)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the CLI:**
   ```bash
   # From the project root
   python cli/main.py
   
   # Or use the launcher
   python cli/run.py
   ```

3. **Upload documents:**
   ```bash
   # Upload a single file
   python cli/upload.py document.pdf
   
   # Upload all files in a directory
   python cli/upload.py --dir ./documents
   
   # Interactive upload mode
   python cli/upload.py
   ```

### First Run

When you first run the CLI, it will:
- Test connection to the backend (if available)
- Create a new chat session
- Display welcome message and help

## Usage

### Basic Chat

Simply type your message and press Enter to chat with the AI:

```
👤 You: How can I test my API endpoints?
🤖 I can help you with API testing! Here are some common approaches...
```

### Document Upload

The CLI includes a powerful document upload tool for ingesting documents into the RAG system:

#### Supported Formats
- **PDF** (.pdf)
- **Text** (.txt)
- **Markdown** (.md)
- **Word** (.docx, .doc)
- **HTML** (.html, .htm)
- **JSON** (.json)
- **XML** (.xml)
- **CSV** (.csv)

#### Upload Methods

1. **Single File Upload:**
   ```bash
   python cli/upload.py document.pdf
   ```

2. **Directory Upload:**
   ```bash
   python cli/upload.py --dir ./documents
   python cli/upload.py --dir ./documents --recursive
   ```

3. **Interactive Mode:**
   ```bash
   python cli/upload.py
   ```

4. **Check Upload Status:**
   ```bash
   python cli/upload.py --status <upload_id>
   ```

#### Upload Features
- **File Validation** - Checks file size (max 50MB) and format
- **Progress Tracking** - Shows upload progress for multiple files
- **Metadata Support** - Automatically adds file metadata
- **Batch Processing** - Upload entire directories at once
- **Error Handling** - Graceful handling of upload failures

### Special Commands

The CLI supports several special commands:

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/help` | `/h` | Show this help message |
| `/clear` | `/c` | Clear current session history |
| `/history` | `/hist` | Show conversation history |
| `/sessions` | `/s` | List all sessions |
| `/switch <id>` | - | Switch to a different session |
| `/delete <id>` | - | Delete a session |
| `/stats <id>` | - | Show session statistics |
| `/quit` | `/q` | Exit the CLI |

### Session Management

- **Multiple Sessions**: Create and switch between different conversation sessions
- **Persistent History**: All conversations are automatically saved
- **Session Switching**: Use `/sessions` to see all sessions and `/switch <id>` to change
- **Auto-cleanup**: Expired sessions are automatically cleaned up

## Configuration

### Environment Variables

You can customize the CLI behavior using environment variables:

```bash
# API Configuration
export API_HOST=localhost
export API_PORT=8000

# CLI Behavior
export CLI_COLORS=true
export CLI_SHOW_SOURCES=true
export CLI_SHOW_TOOL_CALLS=false
```

### Configuration File

The CLI automatically creates a configuration file at `~/.tantorinc/cli_sessions.json` to store:
- Session data
- Conversation history
- User preferences

## Examples

### API Testing Questions

```
👤 You: What's the best way to test a REST API?
🤖 For testing REST APIs, I recommend using tools like Postman, Insomnia, or automated testing frameworks...

👤 You: How do I handle authentication in API tests?
🤖 Authentication in API tests can be handled in several ways...
```

### Support Ticket Management

```
👤 You: I need to create a support ticket for login issues
🤖 I'll help you create a support ticket. Let me gather the details...

👤 You: What's the status of ticket ABC123?
🤖 Let me check the status of ticket ABC123 for you...
```

### Document Questions

```
👤 You: How do I set up the development environment?
🤖 Based on the documentation, here's how to set up your development environment...
```

### Document Upload Workflow

```bash
# 1. Upload your documents
python cli/upload.py --dir ./project_docs

# 2. Start chatting with the AI about your documents
python cli/main.py

# 3. Ask questions about your uploaded content
👤 You: What does the API documentation say about authentication?
🤖 Based on the uploaded API documentation, authentication is handled through...
```

## Architecture

The CLI is built with a modular architecture:

```
cli/
├── main.py              # Main chat application entry point
├── upload.py            # Document upload tool
├── chat_interface.py    # Backend communication and chat logic
├── session_manager.py   # Session management and persistence
├── config.py           # Configuration management
├── utils.py            # Utility functions and formatting
├── run.py              # Simple launcher script
├── run_upload.py       # Upload tool launcher
└── test_*.py           # Test scripts
```

### Key Components

- **CLIChat**: Main application orchestrator
- **DocumentUploader**: Handles document uploads and ingestion
- **ChatInterface**: Handles communication with the backend API
- **SessionManager**: Manages chat sessions and persistence
- **CLIConfig**: Configuration management with environment variable support

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure the backend server is running
   - Check API_HOST and API_PORT environment variables
   - Verify network connectivity

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Session Issues**
   - Check file permissions for `~/.tantorinc/` directory
   - Verify JSON file integrity

4. **Upload Issues**
   - Check file size (max 50MB)
   - Verify file format is supported
   - Ensure backend ingestion service is running

### Debug Mode

For debugging, you can set additional environment variables:

```bash
export CLI_DEBUG=true
export CLI_VERBOSE=true
```

## Development

### Adding New Commands

To add new CLI commands:

1. Add command logic to `ChatInterface.handle_command()`
2. Update help text in `ChatInterface.show_help()`
3. Add any necessary utility functions

### Extending Functionality

The CLI is designed to be easily extensible:

- **New Chat Features**: Extend `ChatInterface` class
- **Session Features**: Add methods to `SessionManager`
- **Upload Features**: Extend `DocumentUploader` class
- **UI Enhancements**: Modify utility functions in `utils.py`

### Testing

Test the CLI components:

```bash
# Test chat functionality
python cli/test_cli.py

# Test upload functionality
python cli/test_upload.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This CLI interface is part of the Tantor Inc AI Support Bot project and follows the same license terms.

## Support

For CLI-specific issues or questions:
- Check this README
- Review the code comments
- Open an issue in the project repository
