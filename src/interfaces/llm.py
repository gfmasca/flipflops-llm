"""
LLM service interface for generating responses.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from src.entities.conversation import Conversation


class LLMService(ABC):
    """Interface for LLM service implementations."""
    
    @abstractmethod
    def generate_answer(
        self, 
        query: str, 
        context: str, 
        conversation: Optional[Conversation] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate an answer to a query using an LLM.
        
        Args:
            query: The query text
            context: The context for the query
            conversation: Optional conversation history
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            The generated answer
        """
        pass
    
    @abstractmethod
    def generate_embeddings(self, text: str) -> list:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            The generated embedding vector
        """
        pass 
