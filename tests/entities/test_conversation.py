"""
Unit tests for the Conversation entity.
"""
import pytest
from datetime import datetime, timedelta
from src.entities.conversation import Conversation, Message


class TestConversation:
    """Tests for the Conversation entity."""
    
    def test_conversation_creation(self):
        """Test creating a conversation entity."""
        conversation = Conversation(
            id="1234",
            topic="Physics"
        )
        
        assert conversation.id == "1234"
        assert conversation.topic == "Physics"
        assert isinstance(conversation.start_time, datetime)
        assert conversation.messages == []
        assert isinstance(conversation.metadata, dict)
    
    def test_add_message(self):
        """Test adding messages to the conversation."""
        conversation = Conversation(id="1234")
        
        # Add user message
        conversation.add_message("user", "Hello")
        assert len(conversation.messages) == 1
        assert conversation.messages[0].role == "user"
        assert conversation.messages[0].content == "Hello"
        
        # Add assistant message
        conversation.add_message("assistant", "How can I help you?")
        assert len(conversation.messages) == 2
        assert conversation.messages[1].role == "assistant"
        assert conversation.messages[1].content == "How can I help you?"
    
    def test_get_recent_messages(self):
        """Test getting recent messages."""
        conversation = Conversation(id="1234")
        
        # Add 10 messages
        for i in range(10):
            conversation.add_message("user", f"Message {i}")
        
        # Get default number of recent messages (5)
        recent = conversation.get_recent_messages()
        assert len(recent) == 5
        assert recent[0].content == "Message 5"
        assert recent[4].content == "Message 9"
        
        # Get specific number of recent messages
        recent = conversation.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[0].content == "Message 7"
        assert recent[2].content == "Message 9"
        
        # Get more messages than exist
        recent = conversation.get_recent_messages(20)
        assert len(recent) == 10
    
    def test_clear(self):
        """Test clearing all messages."""
        conversation = Conversation(id="1234")
        
        # Add messages
        conversation.add_message("user", "Hello")
        conversation.add_message("assistant", "Hi")
        assert len(conversation.messages) == 2
        
        # Clear messages
        conversation.clear()
        assert len(conversation.messages) == 0
    
    def test_message_count_property(self):
        """Test the message_count property."""
        conversation = Conversation(id="1234")
        assert conversation.message_count == 0
        
        conversation.add_message("user", "Hello")
        assert conversation.message_count == 1
        
        conversation.add_message("assistant", "Hi")
        assert conversation.message_count == 2
    
    def test_duration_property(self):
        """Test the duration property."""
        conversation = Conversation(id="1234")
        
        # No messages
        assert conversation.duration == 0.0
        
        # Set a known start time for testing
        conversation.start_time = datetime.now()
        
        # Add message with mocked timestamp
        msg = Message(
            role="user",
            content="Hello",
            timestamp=conversation.start_time + timedelta(minutes=5)
        )
        conversation.messages.append(msg)
        
        assert conversation.duration == 300.0  # 5 minutes = 300 seconds
    
    def test_metadata_operations(self):
        """Test adding and retrieving metadata."""
        conversation = Conversation(id="1234")
        
        # Add metadata
        conversation.add_metadata("user_id", "user123")
        assert conversation.metadata["user_id"] == "user123"
        
        # Get metadata with existing key
        assert conversation.get_metadata("user_id") == "user123"
        
        # Get metadata with non-existing key and default value
        assert conversation.get_metadata("language", "en") == "en" 
