"""
Unit tests for the Embedding entity.
"""
import pytest
import math
from src.entities.embedding import Embedding


@pytest.fixture
def sample_embedding():
    """Fixture providing a sample embedding entity."""
    return Embedding(
        id="1234",
        vector=[0.1, 0.2, 0.3, 0.4],
        source_id="doc_1",
        chunk_text="This is a text chunk"
    )


@pytest.fixture
def unit_vector_embedding():
    """Fixture providing an embedding with a unit vector."""
    return Embedding(
        id="5678",
        vector=[1.0, 0.0, 0.0],
        source_id="doc_2",
        chunk_text="Unit vector embedding"
    )


class TestEmbedding:
    """Tests for the Embedding entity."""
    
    def test_embedding_creation(self, sample_embedding):
        """Test creating an embedding entity."""
        assert sample_embedding.id == "1234"
        assert sample_embedding.vector == [0.1, 0.2, 0.3, 0.4]
        assert sample_embedding.source_id == "doc_1"
        assert sample_embedding.chunk_text == "This is a text chunk"
        assert isinstance(sample_embedding.chunk_metadata, dict)
    
    def test_dimension_property(self, sample_embedding):
        """Test the dimension property."""
        assert sample_embedding.dimension == 4
        
        # Test with empty vector
        sample_embedding.vector = []
        assert sample_embedding.dimension == 0
    
    def test_has_metadata_property(self, sample_embedding):
        """Test the has_metadata property."""
        # Empty metadata
        assert sample_embedding.has_metadata is False
        
        # Add metadata
        sample_embedding.add_metadata("position", 1)
        assert sample_embedding.has_metadata is True
    
    def test_metadata_operations(self, sample_embedding):
        """Test adding and retrieving metadata."""
        # Add metadata
        sample_embedding.add_metadata("position", 1)
        assert sample_embedding.chunk_metadata["position"] == 1
        
        # Get metadata with existing key
        assert sample_embedding.get_metadata("position") == 1
        
        # Get metadata with non-existing key and default value
        assert sample_embedding.get_metadata("page", 0) == 0
    
    def test_cosine_similarity(self, unit_vector_embedding):
        """Test cosine similarity computation."""
        # Same vector
        similarity = unit_vector_embedding.cosine_similarity([1.0, 0.0, 0.0])
        assert similarity == pytest.approx(1.0)
        
        # Orthogonal vector
        similarity = unit_vector_embedding.cosine_similarity([0.0, 1.0, 0.0])
        assert similarity == pytest.approx(0.0)
        
        # 45-degree angle (cos(45°) = 1/√2 ≈ 0.7071)
        similarity = unit_vector_embedding.cosine_similarity([1.0, 1.0, 0.0])
        angle_cos = 1/math.sqrt(2)
        assert similarity == pytest.approx(angle_cos)
        
        # Zero vector
        similarity = unit_vector_embedding.cosine_similarity([0.0, 0.0, 0.0])
        assert similarity == 0.0
        
        # Test with different dimensions
        with pytest.raises(ValueError):
            unit_vector_embedding.cosine_similarity([1.0, 0.0]) 
