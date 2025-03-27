"""
Abstract interface for LLM services.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.entities.topic import Topic


class LLMService(ABC):
    """Interface for LLM services."""

    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        context: List[str] = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate a response from the LLM using the provided prompt and context.
        
        Args:
            prompt: The main prompt to send to the LLM
            context: List of context passages to include
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            The generated response text
            
        Raises:
            ValueError: If the prompt is invalid
            RuntimeError: If the LLM API call fails
        """
        pass

    @abstractmethod
    def generate_question(
        self, 
        topic: Topic, 
        difficulty: str,
        additional_context: List[str] = None
    ) -> str:
        """
        Generate an educational question about the given topic.
        
        Args:
            topic: The topic to generate a question about
            difficulty: The difficulty level (e.g., "easy", "medium", "hard")
            additional_context: Additional context to include
            
        Returns:
            The generated question
            
        Raises:
            ValueError: If the topic or difficulty is invalid
            RuntimeError: If the LLM API call fails
        """
        pass

    @abstractmethod
    def explain_concept(
        self, 
        concept: str, 
        context: List[str] = None,
        detail_level: str = "medium"
    ) -> str:
        """
        Generate an explanation of a concept.
        
        Args:
            concept: The concept to explain
            context: List of context passages to include
            detail_level: Level of detail for the explanation 
                         (e.g., "brief", "medium", "detailed")
            
        Returns:
            The generated explanation
            
        Raises:
            ValueError: If the concept is invalid
            RuntimeError: If the LLM API call fails
        """
        pass 
