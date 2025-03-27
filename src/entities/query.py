"""
Entity representing a search query.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Query:
    """Represents a search query."""
    
    id: str
    text: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def word_count(self) -> int:
        """Get the number of words in the query."""
        return len(self.text.split())
    
    @property
    def is_about_topic(self) -> bool:
        """Check if the query is associated with a topic."""
        return self.topic is not None
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the query."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the query."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def update_text(self, text: str) -> None:
        """Update the query text."""
        self.text = text
