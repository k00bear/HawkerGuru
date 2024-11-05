from pathlib import Path
import shutil
import logging
from datetime import datetime

def organize_and_verify_data():
    """Organize data folder and verify contents."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Define folder structure
    data_dir = Path("data")
    original_dir = data_dir / "original"
    current_dir = data_dir / "current"
    archive_dir = data_dir / "archive"
    
    # Create directories
    for directory in [original_dir, current_dir, archive_dir]:
        directory.mkdir(exist_ok=True)
    
    # Original file mappings
    original_files = {
        'faq': "FAQs on Electronic Tender (E-Tender)_20240326 (for cc) - with CC's internal comments (clean).docx",
        'tender_notice': "Aug 2024 Tender Notice_Text Only.docx",
        'terms_and_conditions': "Terms and Conditions of eTender (Aug 2024)_Text file.txt"
    }
    
    # Search for files in data directory and subdirectories
    print("\nSearching for original documents:")
    found_files = {}
    for doc_type, filename in original_files.items():
        # Search in multiple possible locations
        possible_locations = [
            data_dir / filename,
            original_dir / doc_type / filename,
            data_dir / "original" / filename,
        ]
        
        found_file = None
        for loc in possible_locations:
            if loc.exists():
                found_file = loc
                break
        
        if found_file:
            found_files[doc_type] = found_file
            print(f"✓ Found {doc_type} document at: {found_file}")
        else:
            print(f"✗ Cannot find {doc_type} document: {filename}")
    
    if not found_files:
        print("\nError: No original documents found!")
        print("Please ensure the following files are in the data directory:")
        for filename in original_files.values():
            print(f"- {filename}")
        return
    
    # Organize files
    print("\nOrganizing documents:")
    for doc_type, file_path in found_files.items():
        # Create type directory in original
        type_dir = original_dir / doc_type
        type_dir.mkdir(exist_ok=True)
        
        # Move to original folder if not already there
        dest_file = type_dir / file_path.name
        if not dest_file.exists():
            shutil.copy2(file_path, dest_file)
            print(f"✓ Copied {file_path.name} to original/{doc_type}/")
    
    # Process files to current format
    print("\nProcessing current versions:")
    from src.data_handlers.document_manager import DocumentManager
    
    try:
        doc_manager = DocumentManager(data_dir)
        
        for doc_type, file_path in found_files.items():
            source_file = original_dir / doc_type / file_path.name
            if source_file.exists():
                doc_manager.update_document(doc_type, source_file)
                print(f"✓ Processed {doc_type} document")
            else:
                print(f"✗ Cannot process {doc_type}: source file missing")
        
    except Exception as e:
        print(f"Error processing documents: {str(e)}")
    
    # Verify current files
    print("\nVerifying current files:")
    expected_current = {
        "faq_latest.txt": 20000,  # Expected minimum size in bytes
        "tender_notice_latest.txt": 10000,
        "terms_latest.txt": 15000
    }
    
    all_files_valid = True
    for filename, min_size in expected_current.items():
        current_file = current_dir / filename
        if current_file.exists():
            size = current_file.stat().st_size
            if size >= min_size:
                print(f"✓ {filename} exists and has valid size (size: {size:,} bytes)")
            else:
                print(f"✗ {filename} exists but may be incomplete (size: {size:,} bytes)")
                all_files_valid = False
        else:
            print(f"✗ Missing current file: {filename}")
            all_files_valid = False
    
    if all_files_valid:
        print("\nSuccess: All documents are organized and processed correctly!")
    else:
        print("\nWarning: Some files may be missing or incomplete. Please check the messages above.")

if __name__ == "__main__":
    organize_and_verify_data()