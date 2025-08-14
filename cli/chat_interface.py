import json
import time
from typing import Dict, List, Optional, Any
import httpx
from .config import cli_config
from .utils import (
    print_colored, print_error, print_warning, print_info, print_success,
    format_sources, format_tool_calls, safe_input, Colors
)
from .session_manager import SessionManager

class ChatInterface:
    """Handles chat communication with the backend API"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.client = httpx.Client(timeout=30.0)
        self.api_base_url = cli_config.api_url
        
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_connection(self) -> bool:
        """Test connection to the backend API"""
        try:
            response = self.client.get(f"{self.api_base_url.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                print_success("✅ Backend API is accessible")
                return True
            else:
                print_warning(f"⚠️  Backend API returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"❌ Cannot connect to backend API: {e}")
            print_info("Make sure the backend server is running")
            return False
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Send a message to the backend and get response"""
        target_session_id = session_id or self.session_manager.current_session_id
        
        # Add user message to session
        self.session_manager.add_message('user', message, target_session_id)
        
        # Prepare request payload
        payload = {
            "message": message,
            "session_id": target_session_id
        }
        
        try:
            print_colored("🤔 Thinking...", Colors.YELLOW, end="")
            
            # Send request to backend
            response = self.client.post(
                f"{self.api_base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add assistant response to session
                self.session_manager.add_message('assistant', result['reply'], target_session_id)
                
                # Update session ID if provided
                if result.get('session_id') and not target_session_id:
                    self.session_manager.current_session_id = result['session_id']
                
                return result
            else:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                
                print_error(f"\n❌ {error_msg}")
                return None
                
        except httpx.TimeoutException:
            print_error("\n❌ Request timed out")
            return None
        except httpx.ConnectError:
            print_error("\n❌ Cannot connect to backend")
            return None
        except Exception as e:
            print_error(f"\n❌ Error sending message: {e}")
            return None
        finally:
            print()  # Clear the "Thinking..." message
    
    def display_response(self, response: Dict[str, Any]):
        """Display the response in a formatted way"""
        if not response:
            return
        
        # Display main reply
        reply = response.get('reply', 'No response received')
        print_colored(f"\n{cli_config.prompt_symbol} ", Colors.CYAN, end="")
        print_colored(reply, Colors.WHITE)
        
        # Display sources if available and enabled
        sources = response.get('sources', [])
        if sources and cli_config.show_sources:
            print_colored("\n📚 Sources:", Colors.MAGENTA)
            formatted_sources = format_sources(sources)
            print_colored(formatted_sources, Colors.GRAY)
        
        # Display tool calls if available and enabled
        tool_calls = response.get('tool_calls', [])
        if tool_calls and cli_config.show_tool_calls:
            print_colored("\n🔧 Tools Used:", Colors.MAGENTA)
            formatted_tools = format_tool_calls(tool_calls)
            print_colored(formatted_tools, Colors.GRAY)
        
        # Display session info
        session_id = response.get('session_id')
        if session_id:
            print_colored(f"\n💬 Session: {session_id}", Colors.GRAY)
        
        print()  # Add spacing
    
    def get_conversation_history(self, session_id: Optional[str] = None, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history from the backend"""
        target_session_id = session_id or self.session_manager.current_session_id
        if not target_session_id:
            return []
        
        try:
            response = self.client.get(f"{self.api_base_url}/chat/session/{target_session_id}/history")
            if response.status_code == 200:
                data = response.json()
                return data.get('history', [])
            else:
                print_warning(f"Could not fetch history: {response.status_code}")
                return []
        except Exception as e:
            print_warning(f"Error fetching history: {e}")
            return []
    
    def clear_conversation_history(self, session_id: Optional[str] = None) -> bool:
        """Clear conversation history from the backend"""
        target_session_id = session_id or self.session_manager.current_session_id
        if not target_session_id:
            return False
        
        try:
            response = self.client.delete(f"{self.api_base_url}/chat/session/{target_session_id}")
            if response.status_code == 200:
                print_success(f"Cleared conversation history for session {target_session_id}")
                return True
            else:
                print_warning(f"Could not clear history: {response.status_code}")
                return False
        except Exception as e:
            print_warning(f"Error clearing history: {e}")
            return False
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List active sessions from the backend"""
        try:
            response = self.client.get(f"{self.api_base_url}/chat/sessions")
            if response.status_code == 200:
                data = response.json()
                # For now, return local sessions since backend endpoint is not fully implemented
                return self.session_manager.list_sessions()
            else:
                print_warning(f"Could not fetch sessions: {response.status_code}")
                return self.session_manager.list_sessions()
        except Exception as e:
            print_warning(f"Error fetching sessions: {e}")
            return self.session_manager.list_sessions()
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands"""
        command = command.strip().lower()
        
        if command in ['/help', '/h', 'help']:
            self.show_help()
            return True
        elif command in ['/clear', '/c', 'clear']:
            self.clear_current_session()
            return True
        elif command in ['/history', '/hist', 'history']:
            self.show_history()
            return True
        elif command in ['/sessions', '/s', 'sessions']:
            self.show_sessions()
            return True
        elif command in ['/quit', '/q', 'quit', 'exit']:
            print_colored("👋 Goodbye!", Colors.GREEN)
            return False
        elif command.startswith('/switch '):
            session_id = command.split(' ', 1)[1].strip()
            self.switch_session(session_id)
            return True
        elif command.startswith('/delete '):
            session_id = command.split(' ', 1)[1].strip()
            self.delete_session(session_id)
            return True
        elif command.startswith('/stats '):
            session_id = command.split(' ', 1)[1].strip()
            self.show_session_stats(session_id)
            return True
        
        return False
    
    def show_help(self):
        """Display help information"""
        help_text = """
🤖 Tantor Inc AI Support Bot - CLI Commands

📝 Chat Commands:
  Just type your message to chat with the AI

🔧 Special Commands:
  /help, /h          - Show this help message
  /clear, /c         - Clear current session history
  /history, /hist    - Show conversation history
  /sessions, /s      - List all sessions
  /switch <id>       - Switch to a different session
  /delete <id>       - Delete a session
  /stats <id>        - Show session statistics
  /quit, /q          - Exit the CLI

💡 Tips:
  - The AI can help with API testing, software development, and support tickets
  - Use natural language to ask questions
  - Sessions are automatically saved and restored
  - Use /sessions to see all your conversations
        """
        print_colored(help_text, Colors.CYAN)
    
    def clear_current_session(self):
        """Clear the current session"""
        if self.session_manager.current_session_id:
            # Clear from backend
            self.clear_conversation_history()
            # Clear from local session manager
            self.session_manager.clear_session()
            print_success("Current session cleared")
        else:
            print_warning("No active session to clear")
    
    def show_history(self):
        """Show conversation history"""
        session = self.session_manager.get_current_session()
        if not session:
            print_warning("No active session")
            return
        
        history = session.get_recent_messages(cli_config.max_history_display)
        if not history:
            print_info("No conversation history")
            return
        
        print_colored(f"\n📜 Conversation History (Session: {session.session_id})", Colors.MAGENTA, bold=True)
        print_colored("-" * 60, Colors.GRAY)
        
        for i, message in enumerate(history, 1):
            role = message['role']
            content = message['content']
            timestamp = message.get('timestamp', 'Unknown')
            
            if role == 'user':
                print_colored(f"{i}. {cli_config.user_symbol} You:", Colors.BLUE, bold=True)
            else:
                print_colored(f"{i}. {cli_config.prompt_symbol} AI:", Colors.CYAN, bold=True)
            
            # Truncate long messages
            if len(content) > 100:
                content = content[:100] + "..."
            
            print_colored(f"   {content}", Colors.WHITE)
            print_colored(f"   {timestamp}", Colors.GRAY)
            print()
    
    def show_sessions(self):
        """Show all available sessions"""
        sessions = self.session_manager.list_sessions()
        if not sessions:
            print_info("No sessions found")
            return
        
        print_colored("\n📋 Available Sessions", Colors.MAGENTA, bold=True)
        print_colored("-" * 80, Colors.GRAY)
        
        for session in sessions:
            session_id = session['session_id']
            created = session['created_at'].strftime("%Y-%m-%d %H:%M")
            last_activity = session['last_activity'].strftime("%Y-%m-%d %H:%M")
            message_count = session['message_count']
            is_current = "⭐" if session['is_current'] else "  "
            
            print_colored(f"{is_current} {session_id}", Colors.CYAN, bold=session['is_current'])
            print_colored(f"    Created: {created} | Messages: {message_count} | Last: {last_activity}", Colors.GRAY)
            print()
    
    def switch_session(self, session_id: str):
        """Switch to a different session"""
        if self.session_manager.switch_session(session_id):
            # Load history from backend
            history = self.get_conversation_history(session_id)
            if history:
                print_info(f"Loaded {len(history)} messages from session {session_id}")
        else:
            print_warning(f"Could not switch to session {session_id}")
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if self.session_manager.delete_session(session_id):
            # Also try to clear from backend
            self.clear_conversation_history(session_id)
    
    def show_session_stats(self, session_id: str):
        """Show statistics for a session"""
        stats = self.session_manager.get_session_stats(session_id)
        if not stats:
            print_warning(f"Session {session_id} not found")
            return
        
        print_colored(f"\n📊 Session Statistics: {session_id}", Colors.MAGENTA, bold=True)
        print_colored("-" * 50, Colors.GRAY)
        print_colored(f"Created: {stats['created_at']}", Colors.WHITE)
        print_colored(f"Last Activity: {stats['last_activity']}", Colors.WHITE)
        print_colored(f"Total Messages: {stats['total_messages']}", Colors.WHITE)
        print_colored(f"User Messages: {stats['user_messages']}", Colors.WHITE)
        print_colored(f"AI Messages: {stats['assistant_messages']}", Colors.WHITE)
        print_colored(f"Active: {'Yes' if stats['is_active'] else 'No'}", Colors.WHITE)
