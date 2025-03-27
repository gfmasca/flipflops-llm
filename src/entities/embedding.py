"""
Entity representing a vector embedding of text.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Embedding:
    """Represents a vector embedding of text content."""
    
    id: str
    vector: List[float]
    text: str
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def dimension(self) -> int:
        """Get the dimension of the embedding vector."""
        return len(self.vector)
    
    @property
    def has_metadata(self) -> bool:
        """Check if the embedding has any metadata."""
        return bool(self.metadata)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the embedding."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the embedding."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def cosine_similarity(self, other_vector: List[float]) -> float:
        """
        Calculate cosine similarity with another vector.
        
        Note: This is a simple implementation and not optimized for performance.
        """
        if len(other_vector) != self.dimension:
            raise ValueError("Vectors must have the same dimension")
            
        dot_product = sum(a * b for a, b in zip(self.vector, other_vector))
        norm1 = sum(a * a for a in self.vector) ** 0.5
        norm2 = sum(b * b for b in other_vector) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return dot_product / (norm1 * norm2) 
