"""
Abstract interface for conversation repositories.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.entities.conversation import Conversation


class ConversationRepository(ABC):
    """Interface for conversation repositories."""

    @abstractmethod
    def save_conversation(self, conversation: Conversation) -> bool:
        """
        Save a conversation to the repository.
        
        Args:
            conversation: The conversation to save
            
        Returns:
            True if the conversation was saved successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_conversation(self, id: str) -> Optional[Conversation]:
        """
        Get a conversation by its ID.
        
        Args:
            id: The ID of the conversation to retrieve
            
        Returns:
            The retrieved conversation or None if not found
        """
        pass

    @abstractmethod
    def update_conversation(self, conversation: Conversation) -> bool:
        """
        Update an existing conversation.
        
        Args:
            conversation: The conversation to update
            
        Returns:
            True if the conversation was updated successfully, False otherwise
        """
        pass

    @abstractmethod
    def list_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """
        List recent conversations, ordered by update time (newest first).
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        pass

    @abstractmethod
    def clear_conversations(self) -> bool:
        """
        Clear all conversations from the repository.
        
        Returns:
            True if the conversations were cleared successfully, False otherwise
        """
        pass
        
    @abstractmethod
    def update_context_file(self, conversation: Conversation) -> bool:
        """
        Update the context file with the current conversation state.
        
        Args:
            conversation: The current conversation
            
        Returns:
            True if the context file was updated successfully, False otherwise
        """
        pass 
