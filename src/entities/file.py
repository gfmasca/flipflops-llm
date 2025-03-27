"""
File entity representing a study document.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime


@dataclass
class File:
    """A study document uploaded by the user."""
    id: str
    name: str
    path: str
    content: str
    file_type: str
    uploaded_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def size(self) -> int:
        """Get the size of the file content in bytes."""
        return len(self.content.encode('utf-8'))
    
    @property
    def extension(self) -> str:
        """Get the file extension."""
        return self.path.split('.')[-1] if '.' in self.path else ""
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the file."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the file."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def update_content(self, content: str) -> None:
        """Update the file content."""
        self.content = content
