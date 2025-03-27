"""
Unit tests for the Topic entity.
"""
import pytest
from src.entities.topic import Topic


class TestTopic:
    """Tests for the Topic entity."""
    
    def test_topic_creation(self):
        """Test creating a topic entity."""
        topic = Topic(
            id="1234",
            name="Mechanics",
            description="Study of motion and forces",
            related_terms=["force", "acceleration"]
        )
        
        assert topic.id == "1234"
        assert topic.name == "Mechanics"
        assert topic.description == "Study of motion and forces"
        assert topic.related_terms == ["force", "acceleration"]
        assert isinstance(topic.metadata, dict)
    
    def test_topic_with_defaults(self):
        """Test creating a topic with default values."""
        topic = Topic(id="1234", name="Mechanics")
        
        assert topic.id == "1234"
        assert topic.name == "Mechanics"
        assert topic.description == ""
        assert topic.related_terms == []
        assert isinstance(topic.metadata, dict)
    
    def test_has_description_property(self):
        """Test the has_description property."""
        # With description
        topic = Topic(
            id="1234",
            name="Mechanics",
            description="Study of motion and forces"
        )
        assert topic.has_description is True
        
        # Without description (empty string)
        topic.description = ""
        assert topic.has_description is False
    
    def test_term_count_property(self):
        """Test the term_count property."""
        topic = Topic(
            id="1234",
            name="Mechanics",
            related_terms=["force", "acceleration", "velocity"]
        )
        
        assert topic.term_count == 3
        
        # With no terms
        topic.related_terms = []
        assert topic.term_count == 0
    
    def test_add_related_term(self):
        """Test adding related terms."""
        topic = Topic(id="1234", name="Mechanics")
        
        # Add new term
        topic.add_related_term("force")
        assert "force" in topic.related_terms
        assert len(topic.related_terms) == 1
        
        # Add duplicate term (should not be added)
        topic.add_related_term("force")
        assert len(topic.related_terms) == 1
        
        # Add another term
        topic.add_related_term("velocity")
        assert "velocity" in topic.related_terms
        assert len(topic.related_terms) == 2
    
    def test_remove_related_term(self):
        """Test removing related terms."""
        topic = Topic(
            id="1234",
            name="Mechanics",
            related_terms=["force", "acceleration", "velocity"]
        )
        
        # Remove existing term
        result = topic.remove_related_term("force")
        assert result is True
        assert "force" not in topic.related_terms
        assert len(topic.related_terms) == 2
        
        # Remove non-existing term
        result = topic.remove_related_term("energy")
        assert result is False
        assert len(topic.related_terms) == 2
    
    def test_update_description(self):
        """Test updating description."""
        topic = Topic(id="1234", name="Mechanics")
        
        new_description = "Branch of physics dealing with motion and forces"
        topic.update_description(new_description)
        assert topic.description == new_description
    
    def test_metadata_operations(self):
        """Test adding and retrieving metadata."""
        topic = Topic(id="1234", name="Mechanics")
        
        # Add metadata
        topic.add_metadata("level", "advanced")
        assert topic.metadata["level"] == "advanced"
        
        # Get metadata with existing key
        assert topic.get_metadata("level") == "advanced"
        
        # Get metadata with non-existing key and default value
        assert topic.get_metadata("semester", 1) == 1 
