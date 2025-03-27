"""
Entity representing a chunk of text from a document.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class TextChunk:
    """Represents a chunk of text extracted from a document."""
    
    id: str
    text: str
    document_id: str
    chunk_index: int
    metadata: Dict[str, Any] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {} 
