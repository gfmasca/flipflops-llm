"""
File-based implementation of the ConversationRepository.
"""
import os
import json
import time
import logging
from typing import List, Optional
from datetime import datetime

from src.entities.conversation import Conversation
from src.interfaces.repositories.conversation_repository import ConversationRepository


# Configure logger
logger = logging.getLogger(__name__)


class FileConversationRepository(ConversationRepository):
    """
    Implementation of the ConversationRepository interface that stores conversations in files.
    
    This repository saves conversations as JSON files and maintains a context file
    in Markdown format (FLIPFLOP.md) according to the MCP pattern.
    """
    
    def __init__(self, storage_dir: str, context_file_path: str):
        """
        Initialize the repository with the specified storage directory.
        
        Args:
            storage_dir: Directory where conversation files are stored
            context_file_path: Path to the FLIPFLOP.md context file
        """
        self.storage_dir = storage_dir
        self.context_file_path = context_file_path
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
            logger.info(f"Created conversation storage directory: {storage_dir}")
        
        # Initialize context file if it doesn't exist
        if not os.path.exists(context_file_path):
            self._initialize_context_file()
            logger.info(f"Initialized context file: {context_file_path}")
        
        logger.info(f"Initialized FileConversationRepository at {storage_dir}")
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """
        Save a conversation to the repository.
        
        Args:
            conversation: The conversation to save
            
        Returns:
            True if the conversation was saved successfully, False otherwise
        """
        try:
            # Prepare file path
            file_path = self._get_file_path(conversation.id)
            
            # Convert to dict for serialization
            data = conversation.to_dict()
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved conversation to {file_path}")
            
            # Update the context file
            self.update_context_file(conversation)
            
            return True
        except Exception as e:
            logger.exception(f"Error saving conversation: {e}")
            return False
    
    def get_conversation(self, id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            id: The conversation ID
            
        Returns:
            The conversation, or None if not found
        """
        try:
            file_path = self._get_file_path(id)
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.warning(f"Conversation file not found: {file_path}")
                return None
            
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Deserialize to Conversation object
            conversation = Conversation.from_dict(data)
            logger.info(f"Loaded conversation: {id}")
            
            return conversation
        except Exception as e:
            logger.exception(f"Error getting conversation: {e}")
            return None
    
    def update_conversation(self, conversation: Conversation) -> bool:
        """
        Update an existing conversation.
        
        Args:
            conversation: The conversation to update
            
        Returns:
            True if the conversation was updated successfully, False otherwise
        """
        return self.save_conversation(conversation)
    
    def list_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """
        List recent conversations, ordered by update time.
        
        Args:
            limit: Maximum number of conversations to return (default 10)
            
        Returns:
            List of conversations
        """
        try:
            # Get all JSON files in the storage directory
            files = [f for f in os.listdir(self.storage_dir) 
                   if f.endswith('.json') and os.path.isfile(os.path.join(self.storage_dir, f))]
            
            conversations = []
            
            # Load each file
            for file_name in files:
                try:
                    file_path = os.path.join(self.storage_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Deserialize to Conversation object
                    conversation = Conversation.from_dict(data)
                    conversations.append(conversation)
                except Exception as e:
                    logger.error(f"Error loading conversation from {file_name}: {e}")
            
            # Sort by updated_at (newest first)
            conversations.sort(key=lambda c: c.updated_at, reverse=True)
            
            # Limit the number of results
            if limit > 0:
                conversations = conversations[:limit]
            
            logger.info(f"Listed {len(conversations)} recent conversations")
            return conversations
        except Exception as e:
            logger.exception(f"Error listing conversations: {e}")
            return []
    
    def clear_conversations(self) -> bool:
        """
        Clear all conversations from the repository.
        
        Returns:
            True if the conversations were cleared successfully, False otherwise
        """
        try:
            # Get all JSON files in the storage directory
            files = [f for f in os.listdir(self.storage_dir) 
                   if f.endswith('.json') and os.path.isfile(os.path.join(self.storage_dir, f))]
            
            # Remove each file
            for file_name in files:
                file_path = os.path.join(self.storage_dir, file_name)
                os.remove(file_path)
            
            # Reset the context file
            self._initialize_context_file()
            
            logger.info(f"Cleared {len(files)} conversations")
            return True
        except Exception as e:
            logger.exception(f"Error clearing conversations: {e}")
            return False
    
    def update_context_file(self, conversation: Conversation) -> bool:
        """
        Update the context file with the current conversation state.
        
        Args:
            conversation: The conversation to update the context with
            
        Returns:
            True if the context file was updated successfully, False otherwise
        """
        try:
            # Generate the markdown content
            markdown_content = self._generate_context_markdown(conversation)
            
            # Save to file
            with open(self.context_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Updated context file: {self.context_file_path}")
            return True
        except Exception as e:
            logger.exception(f"Error updating context file: {e}")
            return False
    
    def _get_file_path(self, id: str) -> str:
        """
        Get the file path for a conversation.
        
        Args:
            id: The conversation ID
            
        Returns:
            The file path
        """
        return os.path.join(self.storage_dir, f"{id}.json")
    
    def _initialize_context_file(self) -> None:
        """Initialize the context file with default content."""
        markdown_content = """# FLIPFLOP.md Context File

## Metadata
- Created: {created}
- Last Updated: {updated}
- Session ID: {session_id}
- Version: 1.0

## User Profile
- Education Level: high_school
- Focus Areas: []
- Previous Topics: []

## Conversation History
No conversation history yet.

## Topics
No topics discussed yet.

## User Performance
No performance data yet.

## References
No references yet.
""".format(
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            session_id=f"session_{int(time.time())}"
        )
        
        # Save to file
        with open(self.context_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    def _generate_context_markdown(self, conversation: Conversation) -> str:
        """
        Generate markdown content for the context file.
        
        Args:
            conversation: The conversation to generate content for
            
        Returns:
            Markdown content as a string
        """
        # Extract messages for conversation history
        messages = conversation.get_messages()
        
        # Extract topics from messages
        topics = self._extract_topics_from_messages(messages)
        
        # Format messages for markdown
        message_history = ""
        for msg in messages[-10:]:  # Only include the last 10 messages
            role_icon = "👤" if msg.role == "user" else "🤖"
            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            message_history += f"### {role_icon} {timestamp}\n{msg.content}\n\n"
        
        if not message_history:
            message_history = "No conversation history yet.\n"
        
        # Format topics for markdown
        topics_section = ""
        if topics:
            for topic in topics:
                topics_section += f"- {topic}\n"
        else:
            topics_section = "No topics discussed yet.\n"
        
        # Build the markdown content
        markdown_content = f"""# FLIPFLOP.md Context File

## Metadata
- Created: {datetime.fromtimestamp(conversation.created_at).isoformat()}
- Last Updated: {datetime.fromtimestamp(conversation.updated_at).isoformat()}
- Session ID: {conversation.id}
- Version: 1.0

## User Profile
- Education Level: high_school
- Focus Areas: {', '.join(topics[:3]) if topics else 'Not determined yet'}
- Previous Topics: {', '.join(topics) if topics else 'None yet'}

## Conversation History
{message_history}

## Topics
{topics_section}

## User Performance
No performance data tracked yet.

## References
- FUVEST: https://www.fuvest.br/
- Vestibular: https://vestibular.brasilescola.uol.com.br/
"""
        
        return markdown_content
    
    def _extract_topics_from_messages(self, messages) -> List[str]:
        """
        Extract topics from messages.
        
        Args:
            messages: List of message objects
            
        Returns:
            List of topics
        """
        # Simple keyword extraction (this could be enhanced with NLP)
        keywords = [
            "matemática", "física", "química", "biologia", "história", "geografia",
            "literatura", "gramática", "redação", "inglês", "filosofia", "sociologia"
        ]
        
        topics = set()
        
        for msg in messages:
            if msg.role == "user":
                content = msg.content.lower()
                for keyword in keywords:
                    if keyword.lower() in content:
                        topics.add(keyword)
        
        return list(topics) 
