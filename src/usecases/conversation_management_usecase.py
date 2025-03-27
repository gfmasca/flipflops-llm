"""
Implementation of conversation management service.
"""
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.entities.conversation import Conversation, Message
from src.interfaces.repositories.conversation_repository import (
    ConversationRepository
)


# Configure logger
logger = logging.getLogger(__name__)


class ConversationManagementUseCase:
    """
    Implementation of conversation management service.
    
    This class handles the lifecycle of conversations, including:
    - Creating new conversations
    - Adding messages to conversations
    - Retrieving conversation history
    - Maintaining context with the specified retention policy
    - Updating the context file for MCP pattern integration
    """

    def __init__(
        self, 
        repository: ConversationRepository,
        retention_minutes: int = 10
    ):
        """
        Initialize the conversation management use case.
        
        Args:
            repository: Repository for storing and retrieving conversations
            retention_minutes: Conversation retention period in minutes
        """
        self.repository = repository
        self.retention_minutes = retention_minutes
        self.current_conversation: Optional[Conversation] = None
        
        msg = f"Initialized conversation management with {retention_minutes}"
        logger.info(f"{msg} minute retention")

    def start_new_conversation(self, title: Optional[str] = None) -> Conversation:
        """
        Start a new conversation.
        
        Args:
            title: Optional title for the conversation
            
        Returns:
            The new conversation
        """
        # Generate a unique ID for the conversation
        conversation_id = str(uuid.uuid4())
        
        # Create the conversation
        self.current_conversation = Conversation(
            id=conversation_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save the conversation
        self.repository.save_conversation(self.current_conversation)
        
        logger.info(f"Started new conversation: {conversation_id}")
        return self.current_conversation

    def add_user_message(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add a user message to the current conversation.
        
        Args:
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            The created message
        """
        return self._add_message("user", content, metadata)

    def add_assistant_message(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add an assistant message to the current conversation.
        
        Args:
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            The created message
        """
        return self._add_message("assistant", content, metadata)

    def add_system_message(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add a system message to the current conversation.
        
        Args:
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            The created message
        """
        return self._add_message("system", content, metadata)

    def _add_message(
        self, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add a message to the current conversation.
        
        Args:
            role: Message role ("user", "assistant", or "system")
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            The created message
        """
        # Start a new conversation if there isn't one or if the current one is stale
        stale_check = (
            self.current_conversation is None or 
            self.current_conversation.is_stale(self.retention_minutes)
        )
        if stale_check:
            self.start_new_conversation()
        
        # Create the message
        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Add the message to the conversation
        self.current_conversation.add_message(message)
        
        # Update the conversation in the repository
        self.repository.update_conversation(self.current_conversation)
        
        # Update the context file
        self.repository.update_context_file(self.current_conversation)
        
        logger.info(
            f"Added {role} message to conversation "
            f"{self.current_conversation.id}"
        )
        return message

    def get_current_conversation(self) -> Optional[Conversation]:
        """
        Get the current conversation.
        
        Returns:
            The current conversation or None if no conversation is active
        """
        # Check if the current conversation is stale
        if (self.current_conversation is not None and 
                self.current_conversation.is_stale(self.retention_minutes)):
            logger.info(
                f"Current conversation {self.current_conversation.id} "
                f"is stale"
            )
            self.current_conversation = None
            
        return self.current_conversation

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by its ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            The retrieved conversation or None if not found
        """
        return self.repository.get_conversation(conversation_id)

    def list_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """
        List recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        return self.repository.list_recent_conversations(limit)

    def clear_conversation_history(self) -> bool:
        """
        Clear all conversation history.
        
        Returns:
            True if the history was cleared successfully, False otherwise
        """
        # Reset current conversation
        self.current_conversation = None
        
        # Clear conversations from repository
        return self.repository.clear_conversations()

    def update_conversation_context(self) -> bool:
        """
        Update the context file with the current conversation.
        
        Returns:
            True if the context file was updated successfully, False otherwise
        """
        if self.current_conversation is None:
            logger.warning("No active conversation to update context with")
            return False
            
        return self.repository.update_context_file(self.current_conversation)

    def get_conversation_messages(
        self, 
        limit: Optional[int] = None, 
        role: Optional[str] = None
    ) -> List[Message]:
        """
        Get messages from the current conversation.
        
        Args:
            limit: Maximum number of messages to return
            role: Filter by message role if provided
            
        Returns:
            List of messages
        """
        if self.current_conversation is None:
            return []
            
        return self.current_conversation.get_messages(limit, role) 
