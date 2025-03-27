"""
Topic entity representing a study subject for the FUVEST exam.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Topic:
    """A study subject for the FUVEST exam."""
    id: str
    name: str
    parent_id: Optional[str] = None
    subtopics: List[str] = field(default_factory=list)  # IDs of child topics
    file_ids: List[str] = field(default_factory=list)  # Associated file IDs 
    description: str = ""
    related_terms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_description(self) -> bool:
        """Check if the topic has a description."""
        return bool(self.description)
    
    @property
    def term_count(self) -> int:
        """Get the number of related terms."""
        return len(self.related_terms)
    
    def add_related_term(self, term: str) -> None:
        """Add a related term to the topic."""
        if term not in self.related_terms:
            self.related_terms.append(term)
    
    def remove_related_term(self, term: str) -> bool:
        """
        Remove a related term from the topic.
        
        Returns:
            bool: True if the term was removed, False if it wasn't found.
        """
        if term in self.related_terms:
            self.related_terms.remove(term)
            return True
        return False
    
    def update_description(self, description: str) -> None:
        """Update the topic description."""
        self.description = description
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the topic."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the topic."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
