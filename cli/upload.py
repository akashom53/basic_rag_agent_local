#!/usr/bin/env python3
"""
Document Upload Script for Tantor Inc AI Support Bot

This script allows users to upload documents to the backend for ingestion
into the RAG (Retrieval-Augmented Generation) system.
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime

# Add the parent directory to the path so we can import from the app package
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.config import cli_config
from cli.utils import (
    print_header, print_success, print_error, print_warning, print_info,
    print_colored, Colors, safe_input, confirm_action
)

class DocumentUploader:
    """Handles document uploads to the backend"""
    
    def __init__(self):
        self.client = httpx.Client(timeout=60.0)
        self.api_base_url = cli_config.api_url.replace('/api/v1', '')
        self.upload_endpoint = f"{self.api_base_url}/api/v1/ingest/file"
        self.status_endpoint = f"{self.api_base_url}/api/v1/ingest/status"
        
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_connection(self) -> bool:
        """Test connection to the backend"""
        try:
            response = self.client.get(f"{self.api_base_url}/health")
            if response.status_code == 200:
                print_success("✅ Backend connection successful")
                return True
            else:
                print_warning(f"⚠️  Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"❌ Cannot connect to backend: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return [
            # Document formats
            '.pdf', '.txt', '.md', '.docx', '.doc', 
            '.html', '.htm', '.json', '.xml', '.csv',
            # Code and development files
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift',
            '.kt', '.scala', '.r', '.m', '.pl', '.sh', '.bat',
            # Configuration files
            '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            # Markup and documentation
            '.rst', '.tex', '.adoc', '.wiki', '.org',
            # Data files
            '.tsv', '.xlsx', '.xls', '.ods', '.parquet', '.avro'
        ]
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate if a file can be uploaded"""
        if not file_path.exists():
            print_error(f"❌ File does not exist: {file_path}")
            return False
        
        if not file_path.is_file():
            print_error(f"❌ Path is not a file: {file_path}")
            return False
        
        # Check file size (limit to 50MB)
        file_size = file_path.stat().st_size
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            print_error(f"❌ File too large: {file_size / (1024*1024):.1f}MB (max: 50MB)")
            return False
        
        # Check file extension
        supported_formats = self.get_supported_formats()
        if file_path.suffix.lower() not in supported_formats:
            print_error(f"❌ Unsupported file format: {file_path.suffix}")
            print_info(f"Supported formats: {', '.join(supported_formats)}")
            return False
        
        return True
    
    def upload_file(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Upload a single file to the backend"""
        try:
            print_colored(f"📤 Uploading {file_path.name}...", Colors.BLUE)
            
            # Prepare files for upload
            files = {
                'file': (file_path.name, open(file_path, 'rb'), 'application/octet-stream')
            }
            
            # Prepare form data (backend expects chunk_size and chunk_overlap)
            data = {
                'chunk_size': '1000',  # Default chunk size
                'chunk_overlap': '200'  # Default chunk overlap
            }
            
            # Upload file
            response = self.client.post(
                self.upload_endpoint,
                files=files,
                data=data,
                timeout=120.0  # Longer timeout for large files
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"✅ {file_path.name} uploaded successfully")
                print_colored(f"📊 Chunks created: {result.get('chunks_created', 'N/A')}", Colors.CYAN)
                print_colored(f"⏱️  Processing time: {result.get('processing_time', 'N/A')}s", Colors.CYAN)
                return result
            else:
                error_msg = f"Upload failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                
                print_error(f"❌ {error_msg}")
                return None
                
        except Exception as e:
            print_error(f"❌ Error uploading {file_path.name}: {e}")
            return None
    
    def upload_directory(self, dir_path: Path, recursive: bool = False) -> Dict[str, Any]:
        """Upload all supported files in a directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            print_error(f"❌ Directory does not exist: {dir_path}")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        print_colored(f"📁 Scanning directory: {dir_path}", Colors.BLUE)
        
        # Find all files
        if recursive:
            files = list(dir_path.rglob('*'))
        else:
            files = list(dir_path.glob('*'))
        
        # Filter for supported files
        supported_formats = self.get_supported_formats()
        uploadable_files = [
            f for f in files 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        if not uploadable_files:
            print_warning(f"⚠️  No supported files found in {dir_path}")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        print_info(f"Found {len(uploadable_files)} files to upload")
        
        # Confirm upload
        if not confirm_action(f"Upload {len(uploadable_files)} files?"):
            print_info("Upload cancelled")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        # Upload files
        success_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(uploadable_files, 1):
            print_colored(f"\n[{i}/{len(uploadable_files)}] Processing: {file_path.name}", Colors.CYAN)
            
            if self.validate_file(file_path):
                result = self.upload_file(file_path)
                if result:
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
            
            # Progress indicator
            progress = (i / len(uploadable_files)) * 100
            print_colored(f"Progress: {progress:.1f}%", Colors.GRAY)
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(uploadable_files)
        }
    
    def check_upload_status(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of an upload"""
        try:
            response = self.client.get(self.status_endpoint)
            if response.status_code == 200:
                return response.json()
            else:
                print_warning(f"Could not check status: {response.status_code}")
                return None
        except Exception as e:
            print_warning(f"Error checking status: {e}")
            return None
    
    def show_upload_help(self):
        """Display upload help information"""
        help_text = """
📤 Document Upload Help

This tool allows you to upload documents to the AI Support Bot for ingestion.

Supported Formats:
  • Documents: PDF (.pdf), Text (.txt), Markdown (.md), Word (.docx, .doc)
  • Web: HTML (.html, .htm), JSON (.json), XML (.xml)
  • Data: CSV (.csv), TSV (.tsv), Excel (.xlsx, .xls), Parquet (.parquet)
  • Code: Python (.py), JavaScript (.js), Java (.java), C/C++ (.c, .cpp, .h)
  • Config: YAML (.yaml, .yml), TOML (.toml), INI (.ini, .cfg)
  • Documentation: RST (.rst), LaTeX (.tex), AsciiDoc (.adoc)

File Requirements:
  • Maximum size: 50MB per file
  • Files must be readable text or parseable documents
  • Binary files are not supported

Usage Examples:
  • Upload single file: python upload.py document.pdf
  • Upload directory: python upload.py --dir /path/to/documents
  • Recursive upload: python upload.py --dir /path/to/documents --recursive
  • Check status: python upload.py --status <upload_id>

After upload, documents will be processed and made available for AI queries.
        """
        print_colored(help_text, Colors.CYAN)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload documents to Tantor Inc AI Support Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload.py document.pdf
  python upload.py --dir ./documents
  python upload.py --dir ./documents --recursive
  python upload.py --status abc123
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='File or directory path to upload'
    )
    
    parser.add_argument(
        '--dir', '--directory',
        dest='directory',
        help='Upload all supported files from directory'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively scan directories (with --dir)'
    )
    
    parser.add_argument(
        '--status',
        help='Check status of upload by ID'
    )
    
    # Note: --help is automatically provided by argparse
    
    args = parser.parse_args()
    
    # Show help if requested (argparse handles --help automatically)
    # We can still show our custom help for interactive mode
    
    # Initialize uploader
    uploader = DocumentUploader()
    
    # Test connection
    if not uploader.test_connection():
        print_warning("⚠️  Backend connection failed. Uploads may not work.")
        if not confirm_action("Continue anyway?"):
            return
    
    # Handle different upload modes
    if args.status:
        # Check upload status
        print_colored(f"🔍 Checking upload status: {args.status}", Colors.BLUE)
        status = uploader.check_upload_status(args.status)
        if status:
            print_colored("📊 Upload Status:", Colors.MAGENTA, bold=True)
            print(json.dumps(status, indent=2, default=str))
        return
    
    if args.directory:
        # Upload directory
        dir_path = Path(args.directory)
        print_header("📁 Directory Upload")
        result = uploader.upload_directory(dir_path, recursive=args.recursive)
        
        # Show results
        print_colored("\n📊 Upload Results:", Colors.MAGENTA, bold=True)
        print_colored(f"✅ Successful: {result['success']}", Colors.GREEN)
        print_colored(f"❌ Failed: {result['failed']}", Colors.RED)
        print_colored(f"📁 Total: {result['total']}", Colors.CYAN)
        
    elif args.path:
        # Upload single file
        file_path = Path(args.path)
        print_header("📄 File Upload")
        
        if uploader.validate_file(file_path):
            result = uploader.upload_file(file_path)
            if result:
                print_colored("\n📊 Upload Result:", Colors.MAGENTA, bold=True)
                print(json.dumps(result, indent=2, default=str))
        else:
            print_error("❌ File validation failed")
            sys.exit(1)
            
    else:
        # Interactive mode
        print_header("📤 Document Upload")
        print_colored("Welcome to the Document Upload Tool!", Colors.GREEN, bold=True)
        print()
        
        while True:
            print_colored("Choose an option:", Colors.CYAN)
            print_colored("1. Upload single file", Colors.WHITE)
            print_colored("2. Upload directory", Colors.WHITE)
            print_colored("3. Check upload status", Colors.WHITE)
            print_colored("4. Show help", Colors.WHITE)
            print_colored("5. Exit", Colors.WHITE)
            print()
            
            choice = safe_input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                file_path = safe_input("Enter file path: ").strip()
                if file_path:
                    file_path = Path(file_path)
                    if uploader.validate_file(file_path):
                        uploader.upload_file(file_path)
                    else:
                        print_error("❌ File validation failed")
                print()
                
            elif choice == '2':
                dir_path = safe_input("Enter directory path: ").strip()
                if dir_path:
                    dir_path = Path(dir_path)
                    recursive = safe_input("Recursive scan? (y/N): ").strip().lower() == 'y'
                    result = uploader.upload_directory(dir_path, recursive=recursive)
                    
                    print_colored("\n📊 Upload Results:", Colors.MAGENTA, bold=True)
                    print_colored(f"✅ Successful: {result['success']}", Colors.GREEN)
                    print_colored(f"❌ Failed: {result['failed']}", Colors.RED)
                    print_colored(f"📁 Total: {result['total']}", Colors.CYAN)
                print()
                
            elif choice == '3':
                upload_id = safe_input("Enter upload ID: ").strip()
                if upload_id:
                    status = uploader.check_upload_status(upload_id)
                    if status:
                        print_colored("📊 Upload Status:", Colors.MAGENTA, bold=True)
                        print(json.dumps(status, indent=2, default=str))
                    else:
                        print_warning("⚠️  Could not retrieve status")
                print()
                
            elif choice == '4':
                uploader.show_upload_help()
                print()
                
            elif choice == '5':
                print_colored("👋 Goodbye!", Colors.GREEN)
                break
                
            else:
                print_warning("⚠️  Invalid choice. Please enter 1-5.")
                print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Upload cancelled", Colors.YELLOW)
    except Exception as e:
        print_error(f"❌ Unexpected error: {e}")
        sys.exit(1)
