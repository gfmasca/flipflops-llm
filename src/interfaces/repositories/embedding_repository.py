"""
Abstract interface for embedding repositories.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.entities.embedding import Embedding


class EmbeddingRepository(ABC):
    """Interface for embedding repositories."""

    @abstractmethod
    def save_embedding(self, embedding: Embedding) -> bool:
        """
        Save an embedding to the repository.
        
        Args:
            embedding: The embedding to save
            
        Returns:
            True if the embedding was saved successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_embedding(self, id: str) -> Optional[Embedding]:
        """
        Get an embedding by its ID.
        
        Args:
            id: The ID of the embedding to retrieve
            
        Returns:
            The retrieved embedding or None if not found
        """
        pass

    @abstractmethod
    def search_similar(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Embedding]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of similar embeddings to return
            
        Returns:
            List of similar embeddings, ordered by similarity (most similar first)
        """
        pass

    @abstractmethod
    def list_embeddings(self) -> List[Embedding]:
        """
        List all embeddings in the repository.
        
        Returns:
            List of all embeddings
        """
        pass 
