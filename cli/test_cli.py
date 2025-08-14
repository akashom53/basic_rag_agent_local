#!/usr/bin/env python3
"""
Simple test script for CLI components
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all CLI modules can be imported"""
    try:
        from cli.config import cli_config
        print("✅ Config module imported successfully")
        
        from cli.utils import Colors, print_colored
        print("✅ Utils module imported successfully")
        
        from cli.session_manager import SessionManager, ChatSession
        print("✅ Session manager imported successfully")
        
        from cli.chat_interface import ChatInterface
        print("✅ Chat interface imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration functionality"""
    try:
        from cli.config import cli_config
        
        print(f"✅ API URL: {cli_config.api_url}")
        print(f"✅ Colors enabled: {cli_config.enable_colors}")
        print(f"✅ Session file: {cli_config.get_session_file_path()}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_session_manager():
    """Test session manager functionality"""
    try:
        from cli.session_manager import SessionManager
        
        # Create session manager
        sm = SessionManager()
        print("✅ Session manager created")
        
        # Create a session
        session_id = sm.create_session("test_session")
        print(f"✅ Test session created: {session_id}")
        
        # Add messages
        sm.add_message('user', 'Hello, world!', session_id)
        sm.add_message('assistant', 'Hi there!', session_id)
        print("✅ Messages added to session")
        
        # Get session
        session = sm.get_session(session_id)
        if session:
            print(f"✅ Session retrieved with {session.get_message_count()} messages")
        
        # Cleanup
        sm.delete_session(session_id)
        print("✅ Test session cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Session manager error: {e}")
        return False

def test_utils():
    """Test utility functions"""
    try:
        from cli.utils import print_colored, Colors, truncate_text, format_timestamp
        
        # Test colored output
        print_colored("✅ Colored output test", Colors.GREEN)
        print_colored("✅ Bold colored output", Colors.BLUE, bold=True)
        
        # Test text utilities
        long_text = "This is a very long text that should be truncated"
        truncated = truncate_text(long_text, 20)
        print(f"✅ Text truncation: '{truncated}'")
        
        timestamp = format_timestamp()
        print(f"✅ Timestamp formatting: {timestamp}")
        
        return True
    except Exception as e:
        print(f"❌ Utils error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CLI Components")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Session Manager Test", test_session_manager),
        ("Utils Test", test_utils),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! CLI is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
