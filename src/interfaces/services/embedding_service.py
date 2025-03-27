"""
Abstract interface for embedding services.
"""
from abc import ABC, abstractmethod
from typing import List

from src.entities.embedding import Embedding
from src.entities.file import File
from src.entities.query import Query


class EmbeddingService(ABC):
    """Interface for embedding services."""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
            
        Raises:
            ValueError: If the text cannot be embedded
        """
        pass

    @abstractmethod
    def embed_document(self, file: File) -> List[Embedding]:
        """
        Generate embeddings for a document.
        
        Args:
            file: The document to embed
            
        Returns:
            List of embeddings for the document chunks
            
        Raises:
            ValueError: If the document cannot be embedded
        """
        pass

    @abstractmethod
    def embed_query(self, query: Query) -> List[float]:
        """
        Generate an embedding for a search query.
        
        Args:
            query: The query to embed
            
        Returns:
            The embedding vector for the query
            
        Raises:
            ValueError: If the query cannot be embedded
        """
        pass 
