"""
Anthropic Claude API implementation of LLM service.
"""
from typing import Optional, List
import os

from anthropic import Anthropic

from src.entities.conversation import Conversation
from src.interfaces.llm import LLMService


class ClaudeLLMService(LLMService):
    """Implementation of LLM service using Anthropic Claude API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize the Claude LLM service.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
    
    def generate_answer(
        self, 
        query: str, 
        context: str, 
        conversation: Optional[Conversation] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate an answer using Claude API."""
        system_prompt = (
            "You are a helpful assistant for Brazilian high school students "
            "preparing for the FUVEST exam. Answer the student's question "
            "based on the provided context. If the answer cannot be "
            "determined from the context, say so."
        )
        
        messages = []
        
        # Add conversation history if available
        if conversation and conversation.messages:
            for msg in conversation.messages:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add current query with context
        prompt = f"Context:\n{context}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": prompt})
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.content[0].text
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Claude API.
        
        Note: As of now, Anthropic doesn't have a dedicated embeddings API.
        This should be replaced with a proper embeddings service (e.g., OpenAI).
        """
        # This is a placeholder. In a real implementation,
        # you would use a dedicated embeddings API
        raise NotImplementedError(
            "Claude doesn't provide an embeddings API. "
            "Please use a dedicated embeddings service."
        ) 
