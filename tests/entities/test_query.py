"""
Unit tests for the Query entity.
"""
import pytest
from datetime import datetime
from src.entities.query import Query


@pytest.fixture
def sample_query():
    """Fixture providing a sample query entity."""
    return Query(
        id="1234",
        text="What is the capital of Brazil?",
        topic="Geography"
    )


class TestQuery:
    """Tests for the Query entity."""
    
    def test_query_creation(self, sample_query):
        """Test creating a query entity."""
        assert sample_query.id == "1234"
        assert sample_query.text == "What is the capital of Brazil?"
        assert sample_query.topic == "Geography"
        assert isinstance(sample_query.timestamp, datetime)
        assert isinstance(sample_query.metadata, dict)
    
    def test_word_count_property(self, sample_query):
        """Test the word_count property."""
        assert sample_query.word_count == 6
        
        # Test with empty text
        sample_query.text = ""
        assert sample_query.word_count == 0
    
    def test_is_about_topic_property(self):
        """Test the is_about_topic property."""
        # With topic
        query_with_topic = Query(
            id="1234",
            text="What is the capital of Brazil?",
            topic="Geography"
        )
        assert query_with_topic.is_about_topic is True
        
        # Without topic
        query_without_topic = Query(
            id="1234",
            text="What is the capital of Brazil?",
            topic=None
        )
        assert query_without_topic.is_about_topic is False
    
    def test_metadata_operations(self, sample_query):
        """Test adding and retrieving metadata."""
        # Add metadata
        sample_query.add_metadata("difficulty", "easy")
        assert sample_query.metadata["difficulty"] == "easy"
        
        # Get metadata with existing key
        assert sample_query.get_metadata("difficulty") == "easy"
        
        # Get metadata with non-existing key and default value
        assert sample_query.get_metadata("user_id", "anonymous") == "anonymous"
    
    def test_update_text(self, sample_query):
        """Test updating query text."""
        new_text = "What is the largest city in Brazil?"
        sample_query.update_text(new_text)
        assert sample_query.text == new_text 
