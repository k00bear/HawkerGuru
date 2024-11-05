# To test: Move .py into project root folder before running in command prompt "python test_qa_chain.py"

import warnings
from pathlib import Path
from src.data_handlers.qa_chain import setup_hawker_guru
import logging

# Filter warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def verify_documents():
    """Verify required documents exist."""
    current_dir = Path("data/current")
    required_files = [
        "faq_latest.txt",
        "tender_notice_latest.txt",
        "terms_latest.txt"
    ]
    
    missing_files = []
    for filename in required_files:
        file_path = current_dir / filename
        if not file_path.exists():
            missing_files.append(filename)
    
    return missing_files

def test_qa_chain():
    """Test the enhanced QA chain with various types of questions."""
    print("\nTesting Enhanced QA Chain:")
    print("="*80)
    
    # Verify documents first
    missing_files = verify_documents()
    if missing_files:
        print("\nError: Missing required files:")
        for file in missing_files:
            print(f"- {file}")
        print("\nPlease run organize_and_verify.py first to set up the required files.")
        return
    
    # Initialize QA chain
    try:
        qa_chain = setup_hawker_guru()
    except Exception as e:
        logger.error(f"Failed to initialize QA chain: {str(e)}")
        return
    
    # Test questions
    test_questions = [
        # FAQ-type questions
        "How do I submit my tender bid?",
        "What documents do I need to prepare?",
        
        # T&C-focused questions
        "What are the eligibility requirements for bidding?",
        "Can I operate multiple stalls?",
        
        # Current tender questions
        "When is the next tender deadline?",
        "What stalls are available now?",
        
        # Complex questions
        "I'm new to hawker business. What should I consider before bidding?",
        "How do I calculate a sustainable bid amount?"
    ]
    
    chat_history = []
    
    print("\nTesting different types of questions:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'-'*80}")
        print(f"Q{i}: {question}")
        
        try:
            response = qa_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            
            print("\nAnswer:", response['answer'].strip())
            
            # Update chat history
            chat_history.append((question, response['answer']))
            
            # Print source documents used
            print("\nSources used:")
            for doc in response['source_documents'][:2]:
                print(f"- {doc.metadata.get('source', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error processing question {i}: {str(e)}")

if __name__ == "__main__":
    test_qa_chain()