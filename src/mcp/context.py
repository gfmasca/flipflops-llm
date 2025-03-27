"""
Context component for the MCP pattern.

The Context manages application state and conversation history,
providing a centralized state management solution.
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.entities.conversation import Conversation, Message
from src.interfaces.repositories.conversation_repository import ConversationRepository

# Configure logger
logger = logging.getLogger(__name__)


class FlipflopsContext:
    """
    Context component that manages application state.
    
    Responsibilities:
    - Maintain conversation state between interactions
    - Track user performance and preferences
    - Read/write state to persistent storage (FLIPFLOP.md)
    - Provide context to enhance model responses
    """
    
    def __init__(self, conversation_repository: ConversationRepository):
        """
        Initialize the context with required repositories.
        
        Args:
            conversation_repository: Repository for persisting conversations
        """
        self._conversation_repository = conversation_repository
        self._current_conversation = None
        self._state = {
            "user_level": "high_school",
            "user_performance": {},
            "related_topics": [],
            "previous_topics": [],
            "available_topics": [],
            "session_start": datetime.now().isoformat(),
        }
        
        # Initialize by loading the current conversation
        self._load_conversation()
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current application state.
        
        Returns:
            The current state dictionary
        """
        # Update timestamp
        self._state["last_updated"] = datetime.now().isoformat()
        return self._state
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update the application state.
        
        Args:
            updates: Dictionary of state updates to apply
        """
        self._state.update(updates)
        logger.debug(f"Updated context state with: {list(updates.keys())}")
    
    def add_user_message(self, message: str) -> None:
        """
        Add a user message to the current conversation.
        
        Args:
            message: The message content
        """
        if not self._current_conversation:
            self._create_new_conversation()
        
        self._current_conversation.add_message(
            Message(content=message, role="user", timestamp=time.time())
        )
        self._save_conversation()
        
        # Extract and track topics from user messages
        self._extract_topics_from_message(message)
    
    def add_system_message(self, message: str) -> None:
        """
        Add a system message to the current conversation.
        
        Args:
            message: The message content
        """
        if not self._current_conversation:
            self._create_new_conversation()
        
        self._current_conversation.add_message(
            Message(content=message, role="assistant", timestamp=time.time())
        )
        self._save_conversation()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        if not self._current_conversation:
            return []
        
        messages = self._current_conversation.get_messages()
        if limit and limit > 0:
            messages = messages[-limit:]
        
        return [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in messages
        ]
    
    def clear_conversation(self) -> bool:
        """
        Clear the current conversation.
        
        Returns:
            True if successful, False otherwise
        """
        self._current_conversation = None
        success = self._conversation_repository.clear_conversations()
        
        if success:
            self._create_new_conversation()
            logger.info("Cleared conversation history")
        
        return success
    
    def update_flipflop_file(self) -> bool:
        """
        Update the FLIPFLOP.md context file with the current state.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._current_conversation:
            self._create_new_conversation()
        
        return self._conversation_repository.update_context_file(self._current_conversation)
    
    def add_related_topic(self, topic: str) -> None:
        """
        Add a related topic to the context.
        
        Args:
            topic: The topic to add
        """
        related_topics = self._state.get("related_topics", [])
        if topic not in related_topics:
            related_topics.append(topic)
            self._state["related_topics"] = related_topics
            logger.debug(f"Added related topic: {topic}")
    
    def add_previous_topic(self, topic: str) -> None:
        """
        Add a topic to the list of previously discussed topics.
        
        Args:
            topic: The topic to add
        """
        previous_topics = self._state.get("previous_topics", [])
        if topic not in previous_topics:
            previous_topics.append(topic)
            self._state["previous_topics"] = previous_topics
            logger.debug(f"Added previous topic: {topic}")
    
    def update_user_performance(self, topic: str, score: float) -> None:
        """
        Update the user's performance on a topic.
        
        Args:
            topic: The topic
            score: The score (0.0 to 1.0)
        """
        user_performance = self._state.get("user_performance", {})
        if topic not in user_performance:
            user_performance[topic] = []
        user_performance[topic].append(score)
        self._state["user_performance"] = user_performance
        logger.debug(f"Updated user performance for topic: {topic}")
    
    def set_user_level(self, level: str) -> None:
        """
        Set the user's education level.
        
        Args:
            level: The education level (e.g., "high_school", "university")
        """
        self._state["user_level"] = level
        logger.debug(f"Set user level to: {level}")
    
    def _load_conversation(self) -> None:
        """Load the current conversation from the repository."""
        try:
            conversation = self._conversation_repository.get_conversation("current")
            if conversation:
                self._current_conversation = conversation
                logger.info("Loaded existing conversation")
            else:
                self._create_new_conversation()
                logger.info("No existing conversation found, created new one")
        except Exception as e:
            logger.exception(f"Error loading conversation: {e}")
            self._create_new_conversation()
    
    def _create_new_conversation(self) -> None:
        """Create a new conversation."""
        self._current_conversation = Conversation(
            id="current",
            messages=[],
            created_at=time.time(),
            updated_at=time.time(),
        )
        self._save_conversation()
        logger.info("Created new conversation")
    
    def _save_conversation(self) -> None:
        """Save the current conversation to the repository."""
        if self._current_conversation:
            self._current_conversation.updated_at = time.time()
            success = self._conversation_repository.save_conversation(self._current_conversation)
            
            if success:
                # Update the context file
                self._conversation_repository.update_context_file(self._current_conversation)
            else:
                logger.warning("Failed to save conversation")
    
    def _extract_topics_from_message(self, message: str) -> None:
        """
        Extract potential topics from a user message.
        
        Args:
            message: The user message
        """
        # Simple keyword extraction for now
        # In a full implementation, this would use NLP techniques
        keywords = [
            "matemática", "física", "química", "biologia", "história", "geografia",
            "literatura", "gramática", "redação", "inglês", "filosofia", "sociologia",
            "algebra", "geometria", "trigonometria", "estatística", "probabilidade",
            "cálculo", "mecânica", "eletromagnetismo", "termodinâmica", "ótica",
            "organic", "inorganic", "bioquímica", "zoologia", "botânica", "ecologia",
            "genética", "idade média", "renascimento", "iluminismo", "revolução",
            "brasil colonial", "brasil império", "brasil república", "cartografia",
            "clima", "geopolítica", "romantismo", "realismo", "modernismo",
            "poesia", "conto", "romance", "sintaxe", "morfologia", "semântica"
        ]
        
        lowercase_message = message.lower()
        for keyword in keywords:
            if keyword.lower() in lowercase_message:
                self.add_related_topic(keyword)
                self.add_previous_topic(keyword) 
