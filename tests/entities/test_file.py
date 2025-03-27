"""
Unit tests for the File entity.
"""
import pytest
from datetime import datetime
from src.entities.file import File


@pytest.fixture
def sample_file():
    """Fixture providing a sample file entity."""
    return File(
        id="1234",
        name="test.pdf",
        path="/path/to/test.pdf",
        content="This is a test document",
        file_type="pdf"
    )


class TestFile:
    """Tests for the File entity."""
    
    def test_file_creation(self, sample_file):
        """Test creating a file entity."""
        assert sample_file.id == "1234"
        assert sample_file.name == "test.pdf"
        assert sample_file.path == "/path/to/test.pdf"
        assert sample_file.content == "This is a test document"
        assert sample_file.file_type == "pdf"
        assert isinstance(sample_file.uploaded_at, datetime)
        assert isinstance(sample_file.metadata, dict)
    
    def test_size_property(self, sample_file):
        """Test the size property."""
        # Size should be the length of the content in bytes
        assert sample_file.size == len("This is a test document".encode('utf-8'))
    
    def test_extension_property(self, sample_file):
        """Test the extension property."""
        assert sample_file.extension == "pdf"
        
        # Test with no extension
        sample_file.path = "/path/to/test"
        assert sample_file.extension == ""
    
    def test_metadata_operations(self, sample_file):
        """Test adding and retrieving metadata."""
        # Add metadata
        sample_file.add_metadata("page_count", 10)
        assert sample_file.metadata["page_count"] == 10
        
        # Get metadata with existing key
        assert sample_file.get_metadata("page_count") == 10
        
        # Get metadata with non-existing key and default value
        assert sample_file.get_metadata("author", "Unknown") == "Unknown"
    
    def test_update_content(self, sample_file):
        """Test updating content."""
        new_content = "This content has been updated"
        sample_file.update_content(new_content)
        assert sample_file.content == new_content 
