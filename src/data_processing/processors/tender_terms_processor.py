# src/data_processing/processors/tender_terms_processor.py

from .base_processor import BasePreprocessor
import re

class TenderTermsPreprocessor(BasePreprocessor):
    """Preprocesses Terms and Conditions document."""
    
    def process(self) -> str:
        """Process Terms and Conditions document."""
        text = self.raw_text
        
        # Basic cleanup
        text = self._basic_cleanup(text)
        
        # Add consistent title formatting
        text = self._format_main_title(text)
        
        # Standardize section headers
        text = self._format_section_headers(text)
        
        # Format clause numbers and subsections
        text = self._format_clauses(text)
        
        # Add section metadata
        text = self._add_section_metadata(text)
        
        self.processed_text = text
        return text
    
    def _format_main_title(self, text: str) -> str:
        """Format the main title section."""
        title_pattern = r"TERMS AND CONDITIONS OF TENDER\s*\nVer \d+: [A-Za-z]+ \d{4}"
        replacement = """
# TERMS AND CONDITIONS OF TENDER
## Version Information
{submatch}

## Document Overview
This document outlines the terms and conditions for hawker stall tenders.
"""
        return re.sub(title_pattern, lambda m: replacement.format(submatch=m.group(0)), text)
    
    def _format_section_headers(self, text: str) -> str:
        """Format all major section headers."""
        section_headers = {
            "Eligibility": 2,
            "Tendering": 2,
            "Market Stall": 2,
            "Cooked Food Stall": 2,
            "Successful Tenderer": 2,
            "Anti-Collusion": 2,
            "Reporting of Anti-competitive Conduct": 3,
            "Warranty": 3,
            "Disclosure of Prior Anti-competitive Conduct": 3
        }
        
        for header, level in section_headers.items():
            pattern = f"({header}\\s*\n)"
            hashes = "#" * level
            text = re.sub(pattern, f"\n{hashes} {header}\n\n", text)
        
        return text
    
    def _format_clauses(self, text: str) -> str:
        """Format clause numbers and subsections."""
        text = re.sub(r"^(\d+)\.\s+", r"\n### Clause \1\n", text, flags=re.MULTILINE)
        text = re.sub(r"^(\d+\.\d+)\s+", r"#### \1\n", text, flags=re.MULTILINE)
        text = re.sub(r"^(\d+\.\d+\.\d+)\s+", r"##### \1\n", text, flags=re.MULTILINE)
        return text
    
    def _add_section_metadata(self, text: str) -> str:
        """Add metadata tags for better context retrieval."""
        sections = {
            "Eligibility": "Clauses 2-6: Requirements for tender submission",
            "Tendering": "Clauses 7-17: Process and rules for submitting tenders",
            "Market Stall": "Clause 18: Specific rules for market stalls",
            "Cooked Food Stall": "Clauses 19-23: Specific rules for cooked food stalls",
            "Successful Tenderer": "Clauses 24-40: Obligations and requirements for successful tenderers",
            "Anti-Collusion": "Clause 41: Rules preventing anti-competitive behavior"
        }
        
        for section, description in sections.items():
            pattern = f"(## {section})"
            metadata = f"""
<!-- Section Metadata
Type: Terms and Conditions
Section: {section}
Description: {description}
-->

"""
            text = re.sub(pattern, f"{metadata}\\1", text)
        
        return text