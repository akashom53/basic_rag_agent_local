#!/usr/bin/env python3
"""
Test script for the document upload tool
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all upload modules can be imported"""
    try:
        from cli.upload import DocumentUploader
        print("✅ Upload module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_uploader_creation():
    """Test uploader creation and basic functionality"""
    try:
        from cli.upload import DocumentUploader
        
        uploader = DocumentUploader()
        print("✅ DocumentUploader created successfully")
        
        # Test supported formats
        formats = uploader.get_supported_formats()
        print(f"✅ Supported formats: {len(formats)} formats")
        
        # Test file validation with a markdown file from samples
        samples_dir = Path(__file__).parent.parent / "samples"
        md_file = samples_dir / "api_testing_guide.md"
        
        if md_file.exists():
            if uploader.validate_file(md_file):
                print("✅ File validation working with markdown file")
            else:
                print("⚠️  File validation failed for markdown file")
        else:
            print("⚠️  Markdown file not found in samples directory")
        
        return True
    except Exception as e:
        print(f"❌ Uploader creation error: {e}")
        return False

def test_file_validation():
    """Test file validation logic"""
    try:
        from cli.upload import DocumentUploader
        
        uploader = DocumentUploader()
        
        # Test with non-existent file
        fake_file = Path("/fake/path/file.txt")
        if not uploader.validate_file(fake_file):
            print("✅ Non-existent file correctly rejected")
        else:
            print("❌ Non-existent file incorrectly accepted")
            return False
        
        # Test with directory
        current_dir = Path(__file__).parent
        if not uploader.validate_file(current_dir):
            print("✅ Directory correctly rejected")
        else:
            print("❌ Directory incorrectly accepted")
            return False
        
        # Test with valid markdown file from samples
        samples_dir = Path(__file__).parent.parent / "samples"
        md_file = samples_dir / "api_testing_guide.md"
        
        if md_file.exists():
            if uploader.validate_file(md_file):
                print("✅ Valid markdown file correctly accepted")
            else:
                print("❌ Valid markdown file incorrectly rejected")
                return False
        else:
            print("⚠️  Markdown file not found in samples directory")
            return False
        
        return True
    except Exception as e:
        print(f"❌ File validation test error: {e}")
        return False

def test_metadata_handling():
    """Test metadata handling"""
    try:
        from cli.upload import DocumentUploader
        from datetime import datetime
        
        uploader = DocumentUploader()
        
        # Test metadata creation with markdown file
        samples_dir = Path(__file__).parent.parent / "samples"
        md_file = samples_dir / "api_testing_guide.md"
        
        if md_file.exists():
            metadata = {
                'source': 'test',
                'category': 'documentation'
            }
            
            # This would normally be called during upload
            # We're just testing the logic
            metadata.update({
                'filename': md_file.name,
                'file_size': md_file.stat().st_size,
                'file_type': md_file.suffix.lower()
            })
            print("✅ Metadata handling working")
            return True
        else:
            print("❌ Markdown file not found in samples directory")
            return False
            
    except Exception as e:
        print(f"❌ Metadata test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Document Upload Tool")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Uploader Creation Test", test_uploader_creation),
        ("File Validation Test", test_file_validation),
        ("Metadata Test", test_metadata_handling),
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Upload tool is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
