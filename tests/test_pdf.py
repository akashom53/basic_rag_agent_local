import pypdf
import sys

def test_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            
            print(f"✅ PDF is readable!")
            print(f"Pages: {len(reader.pages)}")
            
            # Test first page text extraction
            if reader.pages:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                print(f"First page text length: {len(text)} characters")
                print(f"First 200 chars: {text[:200]}...")
                
                if len(text.strip()) > 50:  # Reasonable amount of text
                    print("✅ Text extraction working well")
                else:
                    print("⚠️  Low text content - might be image-based PDF")
                    
    except Exception as e:
        print(f"❌ PDF error: {e}")

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "samples/sample_doc.pdf"
    test_pdf(pdf_path)