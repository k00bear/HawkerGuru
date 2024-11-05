"""
cleanup_project.py - Script to remove old directories and check for needed import updates
"""

import os
from pathlib import Path
import shutil
import re
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectCleaner:
    """Handles cleanup of old project structure and identifies needed import updates."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
        # Directories to remove
        self.cleanup_dirs = [
            'src/data_handlers',
        ]
        
        # Old import patterns to look for
        self.old_import_patterns = [
            r'from src\.data_handlers\.',
            r'from data_handlers\.',
            r'import data_handlers\.',
            r'from \.data_handlers\.'
        ]
        
        # Import path mappings (old -> new)
        self.import_mappings = {
            'data_handlers.excel_to_json': 'src.data_processing.converters.excel_converter',
            'data_handlers.geojson_to_excel': 'src.data_processing.converters.geojson_converter',
            'data_handlers.processor': 'src.data_processing.processors.base_processor',
            'data_handlers.document_manager': 'src.data_processing.managers.document_manager',
            'data_handlers.merge_hawker_data': 'src.data_processing.managers.data_merger',
            'data_handlers.data_models': 'src.models.data_models',
            'data_handlers.qa_chain': 'src.qa.qa_chain'
        }
    
    def remove_old_directories(self) -> None:
        """Remove old directories that are no longer needed."""
        for dir_path in self.cleanup_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                try:
                    shutil.rmtree(full_path)
                    logger.info(f"Removed directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {dir_path}: {str(e)}")
    
    def find_files_needing_updates(self) -> Dict[str, List[str]]:
        """Find all Python files that need import updates."""
        files_to_update = {}
        
        # Files to check
        check_paths = [
            self.project_root / 'HawkerGuru.py',
            self.project_root / 'pages',
            self.project_root / 'tests',
        ]
        
        for path in check_paths:
            if path.is_file() and path.suffix == '.py':
                self._check_file(path, files_to_update)
            elif path.is_dir():
                for py_file in path.rglob('*.py'):
                    self._check_file(py_file, files_to_update)
        
        return files_to_update
    
    def _check_file(self, file_path: Path, files_to_update: Dict[str, List[str]]) -> None:
        """Check a single file for old import patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            old_imports = []
            for pattern in self.old_import_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    old_imports.extend(matches)
            
            if old_imports:
                files_to_update[str(file_path)] = old_imports
                logger.info(f"Found old imports in: {file_path}")
                for imp in old_imports:
                    logger.info(f"  - {imp}")
        
        except Exception as e:
            logger.error(f"Error checking {file_path}: {str(e)}")
    
    def suggest_import_updates(self, files_to_update: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
        """Generate suggested import updates for each file."""
        suggestions = {}
        
        for file_path, old_imports in files_to_update.items():
            suggestions[file_path] = {}
            for old_import in old_imports:
                for old_path, new_path in self.import_mappings.items():
                    if old_path in old_import:
                        old_line = old_import
                        new_line = old_import.replace(old_path, new_path)
                        suggestions[file_path][old_line] = new_line
        
        return suggestions

def main():
    """Run cleanup and import checks."""
    cleaner = ProjectCleaner()
    
    # Step 1: Remove old directories
    print("\n=== Removing Old Directories ===")
    cleaner.remove_old_directories()
    
    # Step 2: Find files needing updates
    print("\n=== Checking for Files Needing Import Updates ===")
    files_to_update = cleaner.find_files_needing_updates()
    
    # Step 3: Generate and display suggestions
    if files_to_update:
        print("\n=== Import Update Suggestions ===")
        suggestions = cleaner.suggest_import_updates(files_to_update)
        
        for file_path, updates in suggestions.items():
            print(f"\nFile: {file_path}")
            print("Suggested updates:")
            for old, new in updates.items():
                print(f"  Replace: {old}")
                print(f"  With:    {new}")
                print()
        
        print("\nNEXT STEPS:")
        print("1. Update the imports in each file listed above")
        print("2. Run the verify_imports.py script again")
        print("3. Test your application to ensure everything works")
    else:
        print("\n✅ No files found needing import updates!")
        print("\nNEXT STEPS:")
        print("1. Test your application to ensure everything works")

if __name__ == "__main__":
    main()