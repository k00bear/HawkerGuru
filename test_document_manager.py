# To test: Move .py into project root folder before running in command prompt "python test_document_manager.py"

from pathlib import Path
from src.data_handlers.document_manager import DocumentManager
import logging

logging.basicConfig(level=logging.INFO)

def test_document_manager():
    """Test the document manager functionality."""
    # Initialize document manager
    data_dir = Path("data")
    doc_manager = DocumentManager(data_dir)
    
    print("\nTesting Document Manager:")
    print("="*80)
    
    # Document mapping
    documents = {
        'faq': "FAQs on Electronic Tender (E-Tender)_20240326 (for cc) - with CC's internal comments (clean).docx",
        'tender_notice': "Aug 2024 Tender Notice_Text Only.docx",
        'terms_and_conditions': "Terms and Conditions of eTender (Aug 2024)_Text file.txt"
    }
    
    # Process each document
    for doc_type, filename in documents.items():
        file_path = Path("data") / filename
        print(f"\nProcessing {doc_type.upper()}:")
        print(f"File: {filename}")
        
        if file_path.exists():
            try:
                doc_manager.update_document(doc_type, file_path)
                print(f"✓ Successfully updated {doc_type}")
            except Exception as e:
                print(f"✗ Error updating {doc_type}: {str(e)}")
        else:
            print(f"✗ File not found: {file_path}")
    
    # List all documents
    print("\nCurrent document status:")
    print("-" * 40)
    documents = doc_manager.list_documents()
    for doc_type, versions in documents.items():
        print(f"\n{doc_type.upper()}:")
        current = versions.get('current')
        if current:
            print(f"  Current: {Path(current).name}")
        else:
            print("  Current: Not available")
        
        archives = versions.get('archived', [])
        if archives:
            print("  Archived versions:")
            for archive in archives[:3]:  # Show only last 3 archives
                print(f"    - {Path(archive).name}")
            if len(archives) > 3:
                print(f"    ... and {len(archives)-3} more")
        else:
            print("  No archived versions")
    
    # Get document info
    print("\nDocument configurations:")
    print("-" * 40)
    for doc_type in ['faq', 'tender_notice', 'terms_and_conditions']:
        try:
            info = doc_manager.get_document_info(doc_type)
            print(f"\n{doc_type.upper()}:")
            print(f"  Preprocessor: {info['preprocessor']}")
            print(f"  Description: {info['description']}")
            print(f"  Current version exists: {info['current_version_exists']}")
            if info.get('last_updated'):
                print(f"  Last updated: {info['last_updated']}")
        except Exception as e:
            print(f"Error getting info for {doc_type}: {str(e)}")

    # Verify content
    print("\nVerifying document content:")
    print("-" * 40)
    for doc_type in ['faq', 'tender_notice', 'terms_and_conditions']:
        current_file = doc_manager.get_current_file(doc_type)
        if current_file and current_file.exists():
            content = current_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            print(f"\n{doc_type.upper()} content preview (first 5 lines):")
            for line in lines[:5]:
                print(f"  {line[:100]}")
            print(f"  ... ({len(lines)} lines total)")
        else:
            print(f"\n{doc_type.upper()}: No content available")

if __name__ == "__main__":
    test_document_manager()