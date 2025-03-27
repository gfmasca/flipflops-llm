"""
Abstract interface for document repositories.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.entities.file import File


class DocumentRepository(ABC):
    """Interface for managing document files."""

    @abstractmethod
    def load_document(self, path: str) -> File:
        """
        Load a document from the given path and create a File entity.
        
        Args:
            path: Path to the document file
            
        Returns:
            File entity with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file format is not supported
        """
        pass

    @abstractmethod
    def save_document(self, file: File) -> bool:
        """
        Save a document to storage.
        
        Args:
            file: File entity to save
            
        Returns:
            True if the document was saved successfully, False otherwise
            
        Raises:
            IOError: If there's an error writing the file
            ValueError: If the file format is not supported
        """
        pass

    @abstractmethod
    def get_document(self, id: str) -> Optional[File]:
        """
        Retrieve a document by its ID.
        
        Args:
            id: Document identifier
            
        Returns:
            File entity if found, None otherwise
        """
        pass

    @abstractmethod
    def list_documents(self) -> List[File]:
        """
        List all available documents.
        
        Returns:
            List of File entities
        """
        pass

    @abstractmethod
    def delete_document(self, id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            id: Document identifier
            
        Returns:
            True if the document was deleted successfully, False otherwise
        """
        pass 
