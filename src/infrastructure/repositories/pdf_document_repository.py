"""
Repository implementation for PDF documents.
"""
import os
import shutil
from datetime import datetime
from typing import Dict, Any

import PyPDF2

from src.entities.file import File
from src.infrastructure.repositories.base_document_repository import BaseDocumentRepository


class PDFDocumentRepository(BaseDocumentRepository):
    """Repository for handling PDF documents."""

    def load_document(self, path: str) -> File:
        """
        Load a PDF document from the given path and create a File entity.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            File entity with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        mime_type = self._get_mime_type(path)
        if not mime_type.startswith('application/pdf'):
            raise ValueError(f"Not a PDF file: {path} (MIME type: {mime_type})")
        
        try:
            content = self._extract_text_from_pdf(path)
            metadata = self._extract_metadata_from_pdf(path)
            
            file_id = self._generate_id()
            filename = os.path.basename(path)
            
            file = File(
                id=file_id,
                name=filename,
                path=path,
                content=content,
                file_type="pdf",
                uploaded_at=datetime.now(),
                metadata=metadata
            )
            
            self.documents[file_id] = file
            return file
            
        except Exception as e:
            raise IOError(f"Error reading PDF file: {str(e)}")

    def save_document(self, file: File) -> bool:
        """
        Save a PDF document to storage.
        
        Args:
            file: File entity to save
            
        Returns:
            True if the document was saved successfully, False otherwise
            
        Raises:
            IOError: If there's an error writing the file
            ValueError: If the file is not a PDF
        """
        if file.file_type != "pdf":
            raise ValueError(f"Not a PDF file: {file.name}")
        
        try:
            # Create a copy of the original file if it exists
            if file.id not in self.documents and os.path.exists(file.path):
                storage_path = self._get_storage_path(file.name, "pdf")
                shutil.copy2(file.path, storage_path)
                file.path = storage_path
            
            # If content has been modified, we need to create a new PDF
            # This would require more complex PDF creation logic
            # For simplicity, we're just updating the document in memory
            
            self.documents[file.id] = file
            return True
            
        except Exception as e:
            raise IOError(f"Error saving PDF file: {str(e)}")

    def _extract_text_from_pdf(self, path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        return text

    def _extract_metadata_from_pdf(self, path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            info = reader.metadata
            
            if info:
                if info.title:
                    metadata['title'] = info.title
                if info.author:
                    metadata['author'] = info.author
                if info.subject:
                    metadata['subject'] = info.subject
                if info.creator:
                    metadata['creator'] = info.creator
                if info.producer:
                    metadata['producer'] = info.producer
                
                # Handle dates carefully to avoid format issues
                try:
                    if hasattr(info, 'creation_date') and info.creation_date:
                        if isinstance(info.creation_date, datetime):
                            metadata['creation_date'] = info.creation_date.isoformat()
                        else:
                            metadata['creation_date'] = str(info.creation_date)
                except Exception:
                    # Skip date if format is incompatible
                    pass
                
                try:
                    if hasattr(info, 'modification_date') and info.modification_date:
                        if isinstance(info.modification_date, datetime):
                            metadata['modification_date'] = info.modification_date.isoformat()
                        else:
                            metadata['modification_date'] = str(info.modification_date)
                except Exception:
                    # Skip date if format is incompatible
                    pass
            
            metadata['page_count'] = len(reader.pages)
            
        return metadata 
