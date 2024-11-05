# src/data_processing/processors/faq_processor.py

from .base_processor import BasePreprocessor
import re

class FAQPreprocessor(BasePreprocessor):
    """Preprocesses FAQ document."""
    
    def process(self) -> str:
        """Process FAQ document."""
        text = self.raw_text
        
        # Basic cleanup first
        text = self._basic_cleanup(text)
        
        # Remove internal notes
        text = self._remove_internal_notes(text)
        
        # Remove revision history
        text = self._remove_revision_history(text)
        
        # Format main sections
        text = self._format_sections(text)
        
        # Format individual FAQs
        text = self._format_questions(text)
        
        # Add metadata
        text = self._add_metadata(text)
        
        self.processed_text = text
        return text
    
    def _remove_internal_notes(self, text: str) -> str:
        """Remove internal CC notes."""
        # Remove anything between [[ and ]]
        text = re.sub(r'\[\[.*?\]\].*?\+=+\+', '', text, flags=re.DOTALL)
        return text
    
    def _remove_revision_history(self, text: str) -> str:
        """Remove revision history section."""
        # Remove the revision history section and everything after it
        text = re.sub(r'REVISION HISTORY.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()
    
    def _format_sections(self, text: str) -> str:
        """Format main FAQ sections."""
        # Start with the title
        result = "# Frequently Asked Questions (FAQs) on Electronic Tender (e-Tender)\n\n"
        
        # Define section patterns with more flexible matching
        sections = {
            r'Eligibility\s*(?:\n|$)': "Eligibility",
            r'About\s+e-?Tender\s*(?:\n|$)': "About e-Tender",
            r'Preparations?\s+Before\s+Tendering': "Preparations Before Tendering",
            r'Considerations?\s+to\s+Tender': "Considerations for Tendering",
            r'Submitting\s+a\s+Tender\s+Bid': "Submitting a Tender Bid",
            r'Amend\s+Particulars': "Amending Tender Details",
            r'Withdrawal\s+of\s+Tender': "Withdrawal of Tender",
            r'Tender\s+Results': "Tender Results",
            r'Successful\s+Tender': "Successful Tender",
            r'Protection\s+Against\s+Scams': "Protection Against Scams",
            r'Security\s+and\s+Data\s+Protection': "Security and Data Protection",
            r'Contact\s+Information': "Contact Information"
        }
        
        current_text = text
        for pattern, section_name in sections.items():
            # Look for the section pattern
            matches = re.split(f'({pattern})', current_text, flags=re.IGNORECASE)
            if len(matches) > 1:
                # Add any text before the section
                if matches[0].strip():
                    result += matches[0].strip() + "\n\n"
                # Add the section header
                result += f"## {section_name}\n\n"
                # Continue with remaining text
                current_text = ''.join(matches[2:])
        
        # Add any remaining text
        if current_text.strip():
            result += current_text.strip() + "\n"
        
        return result
    
    def _format_questions(self, text: str) -> str:
        """Format individual FAQ entries."""
        # Pattern to match numbered questions, handling various formats
        patterns = [
            # Standard numbered questions
            (r'(\d+)[\.|\)]\s*(?:\*\*)?(.*?)(?:\*\*)?\s*(?=\n|$)', r'\n### Q\1: \2\n'),
            # Questions ending with question mark
            (r'^([^#\n].*?\?)\s*$', r'\n### \1\n'),
            # Cleanup excessive newlines
            (r'\n{3,}', '\n\n'),
            # Format bullet points
            (r'(?m)^[•●]\s+', '- '),
            # Remove any remaining asterisks
            (r'\*\*', '')
        ]
        
        # Apply all patterns
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        
        return text
    
    def _add_metadata(self, text: str) -> str:
        """Add metadata for better retrieval."""
        metadata = """<!-- Document Metadata
Type: FAQ
Purpose: Quick reference guide for e-tender process
Target Users: New hawker stall tenderers
Last Updated: March 2024
Topics: eligibility, e-tender process, payments, security, data protection
-->\n\n"""
        return metadata + text