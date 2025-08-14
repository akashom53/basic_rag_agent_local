import sys
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

def colorize(text: str, color: str, bold: bool = False) -> str:
    """Apply color and formatting to text"""
    if not cli_config.enable_colors:
        return text
    
    result = ""
    if bold:
        result += Colors.BOLD
    result += color + text + Colors.RESET
    return result

def print_colored(text: str, color: str = Colors.WHITE, bold: bool = False, end: str = "\n"):
    """Print colored text to terminal"""
    colored_text = colorize(text, color, bold)
    print(colored_text, end=end)

def print_header(text: str):
    """Print a formatted header"""
    print_colored("=" * 60, Colors.CYAN, bold=True)
    print_colored(f" {text} ", Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN, bold=True)

def print_success(text: str):
    """Print success message"""
    print_colored(f"✅ {text}", Colors.GREEN)

def print_error(text: str):
    """Print error message"""
    print_colored(f"❌ {text}", Colors.RED)

def print_warning(text: str):
    """Print warning message"""
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_info(text: str):
    """Print info message"""
    print_colored(f"ℹ️  {text}", Colors.BLUE)

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """Format timestamp for display"""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_sources(sources: List[Dict[str, Any]]) -> str:
    """Format source information for display"""
    if not sources:
        return ""
    
    formatted = []
    for i, source in enumerate(sources, 1):
        content = source.get('content', '')
        score = source.get('score', 0)
        metadata = source.get('metadata', {})
        
        source_text = f"Source {i}:"
        if score:
            source_text += f" (Score: {score:.3f})"
        if metadata.get('filename'):
            source_text += f" - {metadata['filename']}"
        
        formatted.append(source_text)
        formatted.append(f"  {truncate_text(content, 80)}")
    
    return "\n".join(formatted)

def format_tool_calls(tool_calls: List[Dict[str, Any]]) -> str:
    """Format tool call information for display"""
    if not tool_calls:
        return ""
    
    formatted = []
    for i, tool_call in enumerate(tool_calls, 1):
        name = tool_call.get('name', 'Unknown')
        args = tool_call.get('args', {})
        result = tool_call.get('result', '')
        
        formatted.append(f"Tool {i}: {name}")
        if args:
            formatted.append(f"  Args: {json.dumps(args, indent=2)}")
        if result:
            formatted.append(f"  Result: {truncate_text(str(result), 80)}")
    
    return "\n".join(formatted)

def safe_input(prompt: str = "") -> str:
    """Safe input function with error handling"""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print_colored("\nGoodbye! 👋", Colors.GREEN)
        sys.exit(0)
    except Exception as e:
        print_error(f"Input error: {e}")
        return ""

def confirm_action(prompt: str = "Continue? (y/N): ") -> bool:
    """Ask for user confirmation"""
    response = safe_input(prompt).strip().lower()
    return response in ['y', 'yes']

def create_directory_if_not_exists(path: Path):
    """Create directory if it doesn't exist"""
    path.mkdir(parents=True, exist_ok=True)

def load_json_file(file_path: Path, default: Any = None) -> Any:
    """Load JSON file with error handling"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print_warning(f"Could not load {file_path}: {e}")
    
    return default

def save_json_file(file_path: Path, data: Any):
    """Save data to JSON file with error handling"""
    try:
        create_directory_if_not_exists(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        print_error(f"Could not save to {file_path}: {e}")
        return False

# Import cli_config after defining the functions
from .config import cli_config
