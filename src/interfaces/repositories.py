"""
Repository interfaces for data persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class Repository(Generic[T], ABC):
    """Base repository interface."""
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity."""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get an entity by its ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by its ID."""
        pass


class FileRepository(Repository):
    """Repository interface for File entities."""
    
    @abstractmethod
    def get_by_topic(self, topic: str) -> List[T]:
        """Get files by topic."""
        pass


class EmbeddingRepository(Repository):
    """Repository interface for Embedding entities."""
    
    @abstractmethod
    def get_by_source_id(self, source_id: str) -> Optional[T]:
        """Get an embedding by its source ID."""
        pass


class ConversationRepository(Repository):
    """Repository interface for Conversation entities."""
    
    @abstractmethod
    def get_recent(self, limit: int = 10) -> List[T]:
        """Get recent conversations."""
        pass


class TopicRepository(Repository):
    """Repository interface for Topic entities."""
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[T]:
        """Get a topic by its name."""
        pass
    
    @abstractmethod
    def get_subtopics(self, topic_id: str) -> List[T]:
        """Get subtopics of a topic."""
        pass 
