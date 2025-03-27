"""
Entity representing a conversation with history and context.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Message:
    """A message within a conversation."""
    id: str
    content: str
    role: str  # 'user', 'assistant', or 'system'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Represents a conversation with history and context."""
    
    id: str
    title: Optional[str] = None
    topic: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """
        Add a message to the conversation.
        
        Args:
            message: The message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages(self, limit: Optional[int] = None, role: Optional[str] = None) -> List[Message]:
        """
        Get messages from the conversation, optionally filtered.
        
        Args:
            limit: Maximum number of messages to return (newest first)
            role: Filter by message role if provided
            
        Returns:
            List of messages
        """
        filtered = self.messages
        
        # Filter by role if specified
        if role:
            filtered = [m for m in filtered if m.role == role]
            
        # Sort by timestamp (newest first)
        sorted_messages = sorted(filtered, key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit and limit > 0:
            return sorted_messages[:limit]
            
        return sorted_messages
    
    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.messages = []
        self.updated_at = datetime.now()
    
    def is_stale(self, retention_minutes: int = 10) -> bool:
        """
        Check if the conversation is stale based on retention policy.
        
        Args:
            retention_minutes: Retention period in minutes
            
        Returns:
            True if the conversation is older than the retention period
        """
        if not self.messages:
            return True
            
        # Find the most recent message timestamp
        now = datetime.now()
        latest_message = max(self.messages, key=lambda m: m.timestamp)
        
        # Check if the latest message is older than the retention period
        delta = now - latest_message.timestamp
        return delta.total_seconds() > (retention_minutes * 60)
    
    def to_context_format(self) -> str:
        """
        Convert conversation to a format suitable for context.
        
        Returns:
            Formatted string representation of the conversation
        """
        lines = []
        
        if self.title:
            lines.append(f"# {self.title}")
            lines.append("")
            
        for msg in sorted(self.messages, key=lambda m: m.timestamp):
            # Format timestamp
            time_str = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # Format based on role
            if msg.role == "user":
                lines.append(f"**User** ({time_str}):")
                lines.append(f"```")
                lines.append(msg.content)
                lines.append(f"```")
            elif msg.role == "assistant":
                lines.append(f"**Assistant** ({time_str}):")
                lines.append(f"```")
                lines.append(msg.content)
                lines.append(f"```")
            elif msg.role == "system":
                lines.append(f"**System Note** ({time_str}):")
                lines.append(f"_{msg.content}_")
            
            lines.append("")
            
        return "\n".join(lines)
        
    @staticmethod
    def from_context_file(context_str: str, conversation_id: str) -> 'Conversation':
        """
        Create a Conversation object from a context file string.
        
        Args:
            context_str: String content of the context file
            conversation_id: ID to assign to the conversation
            
        Returns:
            Conversation object
        """
        # Implementation will depend on the format of FLIPFLOP.md
        # This is a basic implementation that will need to be refined
        
        conversation = Conversation(id=conversation_id)
        
        # Find title if present
        lines = context_str.split("\n")
        if lines and lines[0].startswith("# "):
            conversation.title = lines[0][2:].strip()
            
        # Parse messages
        # This is a simplified parser and would need to be improved for production
        user_content = []
        assistant_content = []
        system_content = []
        current_section = None
        current_content = []
        
        # TODO: Implement more robust parsing
        
        return conversation 
