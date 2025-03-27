"""
Abstract interface for query processing and retrieval services.
"""
from abc import ABC, abstractmethod
from typing import List

from src.entities.embedding import Embedding
from src.entities.query import Query


class QueryService(ABC):
    """Interface for query processing and retrieval services."""

    @abstractmethod
    def process_query(self, query_text: str) -> Query:
        """
        Process a raw query text and convert it to a structured Query object.
        
        Args:
            query_text: The raw query text from the user
            
        Returns:
            A structured Query object
            
        Raises:
            ValueError: If the query text is invalid or empty
        """
        pass

    @abstractmethod
    def retrieve_relevant_documents(self, query: Query, top_k: int = 5) -> List[Embedding]:
        """
        Retrieve relevant document chunks for the given query.
        
        Args:
            query: The processed query
            top_k: Maximum number of results to retrieve
            
        Returns:
            List of relevant document embeddings
            
        Raises:
            ValueError: If the query is invalid
            RuntimeError: If retrieval fails
        """
        pass

    @abstractmethod
    def rank_results(self, query: Query, results: List[Embedding]) -> List[Embedding]:
        """
        Rank and filter results by relevance.
        
        Args:
            query: The processed query
            results: List of retrieved embeddings to rank
            
        Returns:
            Ranked list of embeddings
            
        Raises:
            ValueError: If the query or results are invalid
        """
        pass 
