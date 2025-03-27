"""
Repository implementation for text documents (TXT, MD).
"""
import os
import shutil
from datetime import datetime
from typing import Dict, Any

from src.entities.file import File
from src.infrastructure.repositories.base_document_repository import BaseDocumentRepository


class TextDocumentRepository(BaseDocumentRepository):
    """Repository for handling text documents (TXT, MD)."""

    def __init__(self, storage_dir: str = "./storage/documents"):
        """
        Initialize the repository.
        
        Args:
            storage_dir: Directory to store documents
        """
        super().__init__(storage_dir)
        self.supported_extensions = ["txt", "md", "markdown"]
        self.supported_mime_types = [
            "text/plain", 
            "text/markdown",
            "text/x-markdown"
        ]

    def load_document(self, path: str) -> File:
        """
        Load a text document from the given path and create a File entity.
        
        Args:
            path: Path to the text file
            
        Returns:
            File entity with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file is not a supported text format
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        # Check file extension
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext not in self.supported_extensions:
            mime_type = self._get_mime_type(path)
            if not any(mime_type.startswith(m) for m in self.supported_mime_types):
                raise ValueError(
                    f"Unsupported text format: {path} "
                    f"(ext: {ext}, MIME: {mime_type})"
                )
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            file_id = self._generate_id()
            filename = os.path.basename(path)
            
            # Determine file type from extension
            if ext == "md" or ext == "markdown":
                file_type = "markdown"
            else:
                file_type = "text"
            
            metadata = self._extract_metadata_from_text(content, file_type)
            
            file = File(
                id=file_id,
                name=filename,
                path=path,
                content=content,
                file_type=file_type,
                uploaded_at=datetime.now(),
                metadata=metadata
            )
            
            self.documents[file_id] = file
            return file
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Not a valid text file: {str(e)}")
        except Exception as e:
            raise IOError(f"Error reading text file: {str(e)}")

    def save_document(self, file: File) -> bool:
        """
        Save a text document to storage.
        
        Args:
            file: File entity to save
            
        Returns:
            True if the document was saved successfully, False otherwise
            
        Raises:
            IOError: If there's an error writing the file
            ValueError: If the file type is not supported
        """
        if file.file_type not in ["text", "markdown"]:
            raise ValueError(f"Unsupported file type: {file.file_type}")
        
        try:
            # Determine extension based on file type
            ext = "md" if file.file_type == "markdown" else "txt"
            
            # Create the storage path
            storage_path = self._get_storage_path(file.name, ext)
            
            # Write the content to the file
            with open(storage_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
            
            # Update the file path
            file.path = storage_path
            
            # Store the document in memory
            self.documents[file.id] = file
            
            return True
            
        except Exception as e:
            raise IOError(f"Error saving text file: {str(e)}")

    def _extract_metadata_from_text(self, content: str, file_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a text file.
        
        Args:
            content: Content of the text file
            file_type: Type of the text file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "line_count": content.count('\n') + 1,
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        # Extract title from markdown files (first # heading)
        if file_type == "markdown":
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    metadata['title'] = line.lstrip('# ').strip()
                    break
        
        return metadata 
