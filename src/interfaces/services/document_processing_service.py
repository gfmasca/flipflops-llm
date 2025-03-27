"""
Abstract interface for document processing services.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from src.entities.file import File
from src.entities.text_chunk import TextChunk
from src.entities.topic import Topic


class DocumentProcessingService(ABC):
    """Interface for document processing services."""

    @abstractmethod
    def process_document(self, file_path: str) -> File:
        """
        Process a document from the given path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Processed File entity
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file format is not supported
        """
        pass

    @abstractmethod
    def chunk_document(self, file: File) -> List[TextChunk]:
        """
        Split a document into chunks for further processing.
        
        Args:
            file: File entity to chunk
            
        Returns:
            List of TextChunk entities
            
        Raises:
            ValueError: If chunking fails or the document type is not supported
        """
        pass

    @abstractmethod
    def extract_metadata(self, file: File) -> Dict[str, Any]:
        """
        Extract enhanced metadata from a document.
        
        Args:
            file: File entity to extract metadata from
            
        Returns:
            Dictionary of extracted metadata
            
        Raises:
            ValueError: If metadata extraction fails
        """
        pass

    @abstractmethod
    def categorize_document(self, file: File) -> Topic:
        """
        Categorize a document based on its content.
        
        Args:
            file: File entity to categorize
            
        Returns:
            Topic classification for the document
            
        Raises:
            ValueError: If categorization fails
        """
        pass 
