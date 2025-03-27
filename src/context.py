"""
Context management for the Model-Context-Protocol pattern.
"""
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Context:
    """Context manager for the MCP pattern."""
    
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        """
        Initialize context with optional initial data.
        
        Args:
            initial_data: Initial context data
        """
        self.context_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.data = initial_data or {}
        self.data['context_id'] = self.context_id
        self.data['created_at'] = self.created_at
        self.data['history'] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Value from context or default
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context.
        
        Args:
            key: Context key
            value: Value to set
        """
        self.data[key] = value
    
    def add_to_history(self, entry: Dict[str, Any]) -> None:
        """
        Add an entry to the context history.
        
        Args:
            entry: History entry to add
        """
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now()
        
        self.data['history'].append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return self.data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """
        Create context from dictionary.
        
        Args:
            data: Dictionary to create context from
            
        Returns:
            New Context instance
        """
        context = cls()
        context.data = data
        if 'context_id' in data:
            context.context_id = data['context_id']
        if 'created_at' in data:
            context.created_at = data['created_at']
        
        return context 
