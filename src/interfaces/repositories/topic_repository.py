"""
Interface for repositories that manage topics.
"""
import abc
from typing import List


class TopicRepository(abc.ABC):
    """
    Interface for repositories that store and retrieve topics.
    
    This interface defines methods for saving, deleting, and listing topics.
    """
    
    @abc.abstractmethod
    def save_topic(self, topic: str) -> bool:
        """
        Save a topic to the repository.
        
        Args:
            topic: The topic to save
            
        Returns:
            True if the topic was saved successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def delete_topic(self, topic: str) -> bool:
        """
        Delete a topic from the repository.
        
        Args:
            topic: The topic to delete
            
        Returns:
            True if the topic was deleted successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def list_topics(self) -> List[str]:
        """
        List all topics in the repository.
        
        Returns:
            A list of topics
        """
        pass
    
    @abc.abstractmethod
    def clear_topics(self) -> bool:
        """
        Clear all topics from the repository.
        
        Returns:
            True if the topics were cleared successfully, False otherwise
        """
        pass 
