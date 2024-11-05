# src/data_processing/processors/tender_notice_processor.py

from .base_processor import BasePreprocessor
import re
from typing import Dict, List

class TenderNoticePreprocessor(BasePreprocessor):
    """Preprocesses Tender Notice document."""
    
    def __init__(self, input_text: str):
        super().__init__(input_text)
        self.special_notes = {}
    
    def process(self) -> str:
        """Process Tender Notice document."""
        text = self.raw_text
        
        # Basic cleanup
        text = self._basic_cleanup(text)
        
        # Format main header and dates
        text = self._format_header_section(text)
        
        # Process special notes and markers
        text = self._process_special_notes(text)
        
        # Format main sections
        text = self._format_main_sections(text)
        
        # Format rental sections
        text = self._format_rental_sections(text)
        
        # Process location-specific rules
        text = self._format_location_rules(text)
        
        # Format tender details
        text = self._format_tender_details(text)
        
        self.processed_text = text
        return text
    
    def _format_header_section(self, text: str) -> str:
        """Format the main header and tender dates section."""
        dates_pattern = r"\[Opening on .*?\] *\n *\[Closing on .*?\]"
        
        def format_dates(match):
            dates_text = match.group(0)
            return """
## Tender Dates
### Opening
{opening_date}
### Closing
{closing_date}
""".format(
                opening_date=re.search(r"\[Opening on (.*?)\]", dates_text).group(1),
                closing_date=re.search(r"\[Closing on (.*?)\]", dates_text).group(1)
            )
        
        text = re.sub(dates_pattern, format_dates, text)
        text = re.sub(r"TENDER NOTICE", "# TENDER NOTICE\n## August 2024", text)
        return text
    
    def _process_special_notes(self, text: str) -> str:
        """Process and format special notes and markers."""
        text = re.sub(r"\[Important Notes\]:\s*", "\n## Important Notes\n", text)
        
        markers = {
            r"\*\*\*\*": "SPECIAL_NOTE_4",
            r"\*\*\*": "SPECIAL_NOTE_3",
            r"\*\*": "SPECIAL_NOTE_2",
            r"\*": "SPECIAL_NOTE_1",
            r"\+": "HALAL_NOTE",
            r"\^": "INDIAN_CUISINE_NOTE"
        }
        
        for marker, replacement in markers.items():
            notes = re.findall(f"{marker}\\s*(.*?)\\s*(?={marker}|$)", text, re.DOTALL)
            if notes:
                self.special_notes[replacement] = notes
            
            text = re.sub(
                f"{marker}\\s*(.*?)\\s*(?={marker}|$)",
                f"\n> Note ({replacement}): \\1\n",
                text
            )
        
        return text
    
    def _format_main_sections(self, text: str) -> str:
        """Format main document sections."""
        section_patterns = {
            r"Tenders for Rental of \[Cooked Food\] Stalls":
                "\n## Cooked Food Stall Rentals\n",
            r"Tenders for Rental of \[Market\] Stalls":
                "\n## Market Stall Rentals\n",
            r"\[Details of Tender\]":
                "\n## Tender Details\n",
            r"\[Important Notes for All Tenderers\]":
                "\n## General Important Notes\n"
        }
        
        for pattern, replacement in section_patterns.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _format_rental_sections(self, text: str) -> str:
        """Format rental-specific sections."""
        text = re.sub(
            r"(\n\* Please choose only \[ONE\] type of trade of sale.*?)\n",
            "\n### Trade Type Selection Requirements\\1\n",
            text
        )
        
        text = re.sub(
            r"(\n\* Not for sale of.*?at \[.*?\].*?)\n",
            "\n### Location-Specific Restrictions\\1\n",
            text
        )
        
        return text
    
    def _format_location_rules(self, text: str) -> str:
        """Format location-specific rules."""
        location_pattern = r"\[([^\]]+)\](?=.*?(?:not allowed|not permitted|restricted))"
        
        def format_location(match):
            location = match.group(1)
            return f"\n#### Restrictions for {location}\n"
        
        text = re.sub(location_pattern, format_location, text)
        return text
    
    def _format_tender_details(self, text: str) -> str:
        """Format tender details section."""
        text = re.sub(
            r"Eligibility Criteria:(.*?)(?=-|$)",
            "### Eligibility Requirements\\1",
            text,
            flags=re.DOTALL
        )
        
        text = re.sub(
            r"Tender bids shall be submitted.*?(?=-|$)",
            "### Submission Requirements\\0",
            text,
            flags=re.DOTALL
        )
        
        return text
    
    def get_special_notes(self) -> Dict[str, List[str]]:
        """Return processed special notes."""
        return self.special_notes