import os
from pathlib import Path
import yaml
import shutil
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class DocumentManager:
    """Manages document versioning and mapping."""
    
    def __init__(self, data_dir: Path):
        """Initialize document manager.
        
        Args:
            data_dir: Path to the data directory
        """
        self.data_dir = Path(data_dir).resolve()  # Get absolute path
        self.config_file = Path("config") / "document_config.yaml"
        
        # Load config and set up paths
        self._ensure_config()
        
        # Set up directory paths directly under data_dir
        self.archive_dir = self.data_dir / "archive"
        self.current_dir = self.data_dir / "current"
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir = self.data_dir / "raw"
        
        # Create necessary directories
        for directory in [self.archive_dir, self.current_dir, self.processed_dir, self.raw_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensuring directory exists: {directory}")
    
    def _organize_existing_files(self) -> None:
        """Move existing files to their correct locations."""
        for doc_type, config in self.config.items():
            if doc_type == 'paths':
                continue
                
            # Check if file exists in data root
            current_file_name = config['current_file']
            old_path = self.data_dir / current_file_name
            new_path = self.current_dir / current_file_name
            
            if old_path.exists() and not new_path.exists():
                logger.info(f"Moving {current_file_name} to current directory")
                shutil.move(str(old_path), str(new_path))
            
            # Check archives
            old_archives = self.data_dir / 'archive'
            if old_archives.exists():
                pattern = config['archive_pattern'].split('%')[0]
                for file in old_archives.glob(f"{pattern}*.txt"):
                    new_archive_path = self.archive_dir / file.name
                    if not new_archive_path.exists():
                        logger.info(f"Moving {file.name} to archive directory")
                        shutil.move(str(file), str(new_archive_path))
    
    def _ensure_config(self) -> None:
        """Ensure configuration file exists and is valid."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config from {self.config_file}: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            'paths': {
                'archive': 'data/archive',
                'current': 'data/current',
                'processed': 'data/processed',
                'raw': 'data/raw'
            },
            'faq': {
                'current_file': 'faq_latest.txt',
                'archive_pattern': 'faq_%Y%m%d.txt',
                'preprocessor': 'FAQPreprocessor',
                'description': 'Frequently Asked Questions document'
            },
            'tender_notice': {
                'current_file': 'tender_notice_latest.txt',
                'archive_pattern': 'tender_notice_%Y%m%d.txt',
                'preprocessor': 'TenderNoticePreprocessor',
                'description': 'Current tender notice'
            },
            'terms_and_conditions': {
                'current_file': 'terms_latest.txt',
                'archive_pattern': 'terms_%Y%m%d.txt',
                'preprocessor': 'TenderTermsPreprocessor',
                'description': 'Terms and conditions document'
            }
        }
        
        # Ensure config directory exists
        Path("config").mkdir(exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        self.config = default_config
        logger.info("Created default configuration file")
    
    def update_document(self, doc_type: str, new_file_path: Path) -> None:
        """Update a document with a new version.
        
        Args:
            doc_type: Type of document (e.g., 'faq', 'tender_notice')
            new_file_path: Path to the new document file
        """
        if doc_type not in self.config:
            raise ValueError(f"Unknown document type: {doc_type}")
        
        try:
            # Archive current version if it exists
            current_file = self.current_dir / self.config[doc_type]['current_file']
            if current_file.exists():
                archive_name = datetime.now().strftime(
                    self.config[doc_type]['archive_pattern']
                )
                archive_path = self.archive_dir / archive_name
                shutil.copy2(current_file, archive_path)
                logger.info(f"Archived current version to {archive_path}")
            
            # Process and save new file
            from src.data_processing.processors.base_processor import DocumentProcessor
            processed_doc = DocumentProcessor.process_document(new_file_path)
            
            # Save processed content
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(processed_doc.content)
            
            logger.info(f"Updated {doc_type} with new content from {new_file_path}")
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise
    
    def get_current_file(self, doc_type: str) -> Optional[Path]:
        """Get path to current version of a document.
        
        Args:
            doc_type: Type of document to retrieve
            
        Returns:
            Path to current version if it exists, None otherwise
        """
        if doc_type not in self.config:
            return None
        
        current_file = self.current_dir / self.config[doc_type]['current_file']
        return current_file if current_file.exists() else None
    
    def list_documents(self) -> Dict[str, Dict[str, List[str]]]:
        """List all current and archived documents.
        
        Returns:
            Dictionary with document types as keys and lists of available versions
        """
        result = {}
        
        for doc_type in self.config:
            if doc_type == 'paths':  # Skip paths section
                continue
                
            result[doc_type] = {
                'current': None,
                'archived': []
            }
            
            # Check current version
            current_file = self.current_dir / self.config[doc_type]['current_file']
            if current_file.exists():
                result[doc_type]['current'] = str(current_file)
            
            # List archives
            try:
                # Get the base pattern
                base_pattern = self.config[doc_type]['archive_pattern'].split('%')[0]
                # List all files that start with the base pattern
                archives = [
                    p for p in self.archive_dir.glob(f"{base_pattern}*.txt")
                    if p.is_file()
                ]
                result[doc_type]['archived'] = sorted([str(p) for p in archives], reverse=True)
            except Exception as e:
                logger.error(f"Error listing archives for {doc_type}: {str(e)}")
                result[doc_type]['archived'] = []
        
        return result
    
    def get_document_info(self, doc_type: str) -> Dict:
        """Get information about a document type.
        
        Args:
            doc_type: Type of document to get info for
            
        Returns:
            Dictionary containing document configuration and status
        """
        if doc_type not in self.config or doc_type == 'paths':
            raise ValueError(f"Unknown document type: {doc_type}")
        
        info = self.config[doc_type].copy()
        current_file = self.current_dir / info['current_file']
        
        if current_file.exists():
            info['current_version_exists'] = True
            info['last_updated'] = datetime.fromtimestamp(
                current_file.stat().st_mtime
            ).strftime('%Y-%m-%d %H:%M:%S')
        else:
            info['current_version_exists'] = False
            info['last_updated'] = None
        
        return info