#!/usr/bin/env python3
"""
Tantor Inc AI Support Bot - CLI Interface

A command-line interface for interacting with the AI Support Bot.
Provides chat functionality, session management, and easy access to support features.
"""

import sys
import os
import signal
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import from the app package
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.config import cli_config
from cli.utils import (
    print_colored, print_header, print_success, print_error, print_warning, print_info,
    safe_input, Colors
)
from cli.session_manager import SessionManager
from cli.chat_interface import ChatInterface

class CLIChat:
    """Main CLI chat application"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.chat_interface = ChatInterface(self.session_manager)
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print_colored("\n\n🛑 Received interrupt signal, shutting down gracefully...", Colors.YELLOW)
        self.running = False
    
    def run(self):
        """Main application loop"""
        try:
            self._show_welcome()
            self._initialize_session()
            self._main_chat_loop()
        except KeyboardInterrupt:
            print_colored("\n\n👋 Goodbye!", Colors.GREEN)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            self._cleanup()
    
    def _show_welcome(self):
        """Display welcome message and application info"""
        print_header("🤖 Tantor Inc AI Support Bot - CLI")
        print_colored("Welcome to the AI Support Bot CLI!", Colors.GREEN, bold=True)
        print_colored("This interface provides access to:", Colors.WHITE)
        print_colored("• AI-powered support and assistance", Colors.WHITE)
        print_colored("• Document-based question answering", Colors.WHITE)
        print_colored("• Support ticket management", Colors.WHITE)
        print_colored("• Conversation history and session management", Colors.WHITE)
        print()
        
        # Show configuration info
        print_colored("🔧 Configuration:", Colors.CYAN)
        print_colored(f"  API URL: {cli_config.api_url}", Colors.GRAY)
        print_colored(f"  Colors: {'Enabled' if cli_config.enable_colors else 'Disabled'}", Colors.GRAY)
        print_colored(f"  Session File: {cli_config.get_session_file_path()}", Colors.GRAY)
        print()
    
    def _initialize_session(self):
        """Initialize the chat session and test connectivity"""
        print_colored("🔌 Testing connection to backend...", Colors.BLUE)
        
        if not self.chat_interface.test_connection():
            print_warning("⚠️  Backend connection failed. Some features may not work.")
            print_info("You can still use the CLI for demonstration purposes.")
            print_info("Start the backend server to enable full functionality.")
            print()
        else:
            print_success("✅ Backend connection successful!")
            print()
        
        # Create initial session if none exists
        if not self.session_manager.current_session_id:
            self.session_manager.create_session()
        
        # Show current session info
        current_session = self.session_manager.get_current_session()
        if current_session:
            print_colored(f"💬 Active Session: {current_session.session_id}", Colors.CYAN)
            print_colored(f"📝 Messages: {current_session.get_message_count()}", Colors.GRAY)
            print()
    
    def _main_chat_loop(self):
        """Main chat loop"""
        print_colored("💬 Chat started! Type your message or use /help for commands.", Colors.GREEN)
        print_colored("Type /quit to exit.", Colors.GRAY)
        print()
        
        while self.running:
            try:
                # Get user input
                user_input = safe_input(f"{cli_config.user_symbol} You: ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith('/'):
                    if not self.chat_interface.handle_command(user_input):
                        self.running = False
                    continue
                
                # Send message to backend
                response = self.chat_interface.send_message(user_input)
                
                # Display response
                self.chat_interface.display_response(response)
                
            except KeyboardInterrupt:
                print_colored("\n\n👋 Goodbye!", Colors.GREEN)
                break
            except Exception as e:
                print_error(f"Error in chat loop: {e}")
                print_info("Continuing...")
                continue
    
    def _cleanup(self):
        """Cleanup resources before exit"""
        try:
            # Save sessions
            if cli_config.auto_save_history:
                print_colored("💾 Saving session data...", Colors.BLUE)
                self.session_manager._save_sessions()
            
            # Clean up expired sessions
            self.session_manager.cleanup_expired_sessions()
            
            print_colored("✅ Cleanup completed", Colors.GREEN)
        except Exception as e:
            print_warning(f"⚠️  Cleanup warning: {e}")

def main():
    """Main entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print_error("Python 3.8 or higher is required")
            sys.exit(1)
        
        # Create and run CLI
        cli = CLIChat()
        cli.run()
        
    except ImportError as e:
        print_error(f"Import error: {e}")
        print_info("Make sure all dependencies are installed:")
        print_info("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
