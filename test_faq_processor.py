# To test: Move .py into project root folder before running in command prompt "python test_faq_processor.py"

from pathlib import Path
from src.data_handlers.processor import FAQPreprocessor, DocumentProcessor

def test_faq_preprocessing():
    """Test FAQ document preprocessing."""
    faq_path = Path("data/FAQs on Electronic Tender (E-Tender)_20240326 (for cc) - with CC's internal comments (clean).docx")
    
    if not faq_path.exists():
        print(f"Error: FAQ document not found at {faq_path}")
        return
    
    print(f"\nProcessing file: {faq_path.name}")
    
    # Process the document
    processed_doc = DocumentProcessor.process_document(faq_path)
    
    # Print first few sections to verify formatting
    print("\nProcessed FAQ Document Preview:")
    print("="*80)
    
    # Print first part with line numbers
    print("\nFirst 30 lines:")
    lines = processed_doc.content.split('\n')
    for i, line in enumerate(lines[:30]):
        print(f"{i+1:2d}| {line}")
    
    # Find and print all section headers
    print("\nDetected section headers:")
    sections = [line for line in lines if line.startswith('## ')]
    for section in sections:
        print(f"  {section}")
    
    # Find and print first few questions
    print("\nFirst 5 detected questions:")
    questions = [line for line in lines if line.startswith('### ')]
    for q in questions[:5]:
        print(f"  {q}")
    print(f"  ... and {len(questions)-5 if len(questions) > 5 else 0} more questions")
    
    # Print statistics
    print("\nDocument Statistics:")
    print(f"Total lines: {len(lines)}")
    print(f"Number of sections: {len(sections)}")
    print(f"Number of questions: {len(questions)}")
    
    # Check document integrity
    print("\nContent checks:")
    revision_history = "REVISION HISTORY" in processed_doc.content
    print(f"- Revision history removed: {'No (WARNING!)' if revision_history else 'Yes (Good)'}")
    
    internal_notes = "[[INTERNAL NOTES FOR CC:]]" in processed_doc.content
    print(f"- Internal notes removed: {'No (WARNING!)' if internal_notes else 'Yes (Good)'}")
    
    if len(sections) == 0 or len(questions) == 0:
        print("\nWARNING: Document structure may not be correct!")
        print("Please check the patterns in the preprocessor.")

if __name__ == "__main__":
    test_faq_preprocessing()