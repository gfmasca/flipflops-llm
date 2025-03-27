"""
File-based implementation of the TopicRepository.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional

from src.interfaces.repositories.topic_repository import TopicRepository


# Configure logger
logger = logging.getLogger(__name__)


class FileTopicRepository(TopicRepository):
    """
    Implementation of the TopicRepository interface that stores topics in JSON files.
    """
    
    def __init__(self, storage_dir: str):
        """
        Initialize the file topic repository.
        
        Args:
            storage_dir: The directory to store topic files in
        """
        self.storage_dir = storage_dir
        self.topics_file = os.path.join(storage_dir, "topics.json")
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
            logger.info(f"Created topics storage directory: {storage_dir}")
        
        # Create empty topics file if it doesn't exist
        if not os.path.exists(self.topics_file):
            self._save_topics([])
            logger.info(f"Created empty topics file: {self.topics_file}")
        
        logger.info(f"Initialized FileTopicRepository at {storage_dir}")
    
    def save_topic(self, topic: str) -> bool:
        """
        Save a topic to the repository.
        
        Args:
            topic: The topic to save
            
        Returns:
            True if the topic was saved successfully, False otherwise
        """
        try:
            # Get existing topics
            topics = self.list_topics()
            
            # Add topic if it doesn't exist
            if topic not in topics:
                topics.append(topic)
                self._save_topics(topics)
                logger.info(f"Saved topic: {topic}")
            
            return True
        except Exception as e:
            logger.exception(f"Error saving topic: {e}")
            return False
    
    def delete_topic(self, topic: str) -> bool:
        """
        Delete a topic from the repository.
        
        Args:
            topic: The topic to delete
            
        Returns:
            True if the topic was deleted successfully, False otherwise
        """
        try:
            # Get existing topics
            topics = self.list_topics()
            
            # Remove topic if it exists
            if topic in topics:
                topics.remove(topic)
                self._save_topics(topics)
                logger.info(f"Deleted topic: {topic}")
            
            return True
        except Exception as e:
            logger.exception(f"Error deleting topic: {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """
        List all topics in the repository.
        
        Returns:
            A list of topics
        """
        try:
            # Load topics from file
            if not os.path.exists(self.topics_file):
                return []
            
            with open(self.topics_file, "r", encoding="utf-8") as f:
                topics = json.load(f)
            
            logger.debug(f"Loaded {len(topics)} topics")
            return topics
        except Exception as e:
            logger.exception(f"Error listing topics: {e}")
            return []
    
    def clear_topics(self) -> bool:
        """
        Clear all topics from the repository.
        
        Returns:
            True if the topics were cleared successfully, False otherwise
        """
        try:
            self._save_topics([])
            logger.info("Cleared all topics")
            return True
        except Exception as e:
            logger.exception(f"Error clearing topics: {e}")
            return False
    
    def _save_topics(self, topics: List[str]) -> None:
        """
        Save topics to file.
        
        Args:
            topics: The list of topics to save
        """
        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2) 
