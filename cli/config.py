import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

class CLIConfig(BaseModel):
    """CLI-specific configuration"""
    # API Configuration
    api_host: str = "localhost"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000/api/v1"
    
    # CLI Behavior
    max_history_display: int = 10
    enable_colors: bool = True
    show_sources: bool = True
    show_tool_calls: bool = False
    
    # Session Management
    session_file: str = "cli_sessions.json"
    auto_save_history: bool = True
    
    # Display Settings
    prompt_symbol: str = ">"
    user_symbol: str = "👤"
    system_symbol: str = "⚙️"
    
    @classmethod
    def from_env(cls) -> "CLIConfig":
        """Create config from environment variables"""
        return cls(
            api_host=os.getenv("API_HOST", "localhost"),
            api_port=int(os.getenv("API_PORT", "8000")),
            enable_colors=os.getenv("CLI_COLORS", "true").lower() == "true",
            show_sources=os.getenv("CLI_SHOW_SOURCES", "true").lower() == "true",
            show_tool_calls=os.getenv("CLI_SHOW_TOOL_CALLS", "false").lower() == "true",
        )
    
    @property
    def api_url(self) -> str:
        """Get full API URL"""
        return f"http://{self.api_host}:{self.api_port}/api/v1"
    
    def get_session_file_path(self) -> Path:
        """Get full path to session file"""
        return Path.home() / ".tantorinc" / self.session_file

# Global CLI config instance
cli_config = CLIConfig.from_env()
