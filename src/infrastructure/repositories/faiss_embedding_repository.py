"""
FAISS-based implementation of the embedding repository.
"""
import os
import pickle
import logging
from typing import List, Dict, Any, Optional

import numpy as np
import faiss

from src.entities.embedding import Embedding
from src.interfaces.repositories.embedding_repository import EmbeddingRepository


# Configure logger
logger = logging.getLogger(__name__)


class FAISSEmbeddingRepository(EmbeddingRepository):
    """FAISS-based implementation of the embedding repository."""
    
    def __init__(self, index_path: str = None, dimension: int = 1536):
        """
        Initialize the FAISS embedding repository.
        
        Args:
            index_path: Path to load/save the FAISS index
            dimension: Dimension of the embedding vectors
        """
        self.index_path = index_path
        self.dimension = dimension
        self.embeddings: Dict[str, Embedding] = {}
        self.index = None
        
        # Initialize FAISS index
        self._initialize_index()
        
        # Load existing index if provided
        if index_path and os.path.exists(index_path):
            self.load_index()
    
    def _initialize_index(self) -> None:
        """Initialize the FAISS index."""
        try:
            # Create a flat L2 index (exact search)
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"FAISS index initialized with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {str(e)}")
            raise ValueError(f"Failed to initialize FAISS index: {str(e)}")
    
    def save_embedding(self, embedding: Embedding) -> bool:
        """
        Save an embedding to the repository.
        
        Args:
            embedding: The embedding to save
            
        Returns:
            True if the embedding was saved successfully, False otherwise
        """
        try:
            # Convert the embedding vector to numpy array
            vector = np.array([embedding.vector], dtype=np.float32)
            
            # Add to FAISS index
            self.index.add(vector)
            
            # Store the embedding object
            self.embeddings[embedding.id] = embedding
            
            # Save the index if path is provided
            if self.index_path:
                self.save_index()
            
            logger.info(f"Embedding {embedding.id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving embedding {embedding.id}: {str(e)}")
            return False
    
    def get_embedding(self, id: str) -> Optional[Embedding]:
        """
        Get an embedding by its ID.
        
        Args:
            id: The ID of the embedding to retrieve
            
        Returns:
            The retrieved embedding or None if not found
        """
        return self.embeddings.get(id)
    
    def search_similar(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Embedding]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of similar embeddings to return
            
        Returns:
            List of similar embeddings, ordered by similarity (most similar first)
        """
        try:
            # Ensure we don't request more items than we have
            actual_top_k = min(top_k, len(self.embeddings))
            
            if actual_top_k == 0:
                logger.warning("No embeddings to search in")
                return []
            
            # Convert query to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search in the index
            distances, indices = self.index.search(query_vector, actual_top_k)
            
            # Map indices to embeddings
            results = []
            embedding_ids = list(self.embeddings.keys())
            
            for idx in indices[0]:
                if 0 <= idx < len(embedding_ids):
                    embedding_id = embedding_ids[idx]
                    results.append(self.embeddings[embedding_id])
            
            logger.info(f"Found {len(results)} similar embeddings")
            return results
        except Exception as e:
            logger.error(f"Error searching similar embeddings: {str(e)}")
            return []
    
    def list_embeddings(self) -> List[Embedding]:
        """
        List all embeddings in the repository.
        
        Returns:
            List of all embeddings
        """
        return list(self.embeddings.values())
    
    def save_index(self) -> bool:
        """
        Save the FAISS index and embeddings to disk.
        
        Returns:
            True if successfully saved, False otherwise
        """
        if not self.index_path:
            logger.warning("No index path provided, cannot save index")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save the FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Save the embeddings dictionary
            with open(f"{self.index_path}.pkl", "wb") as f:
                pickle.dump(self.embeddings, f)
            
            logger.info(f"FAISS index saved to {self.index_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            return False
    
    def load_index(self) -> bool:
        """
        Load the FAISS index and embeddings from disk.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        if not self.index_path:
            logger.warning("No index path provided, cannot load index")
            return False
        
        try:
            # Check if files exist
            faiss_path = f"{self.index_path}.faiss"
            pkl_path = f"{self.index_path}.pkl"
            
            if not os.path.exists(faiss_path) or not os.path.exists(pkl_path):
                logger.warning("Index files not found, creating new index")
                return False
            
            # Load the FAISS index
            self.index = faiss.read_index(faiss_path)
            
            # Load the embeddings dictionary
            with open(pkl_path, "rb") as f:
                self.embeddings = pickle.load(f)
            
            logger.info(f"FAISS index loaded from {self.index_path}")
            logger.info(f"Loaded {len(self.embeddings)} embeddings")
            return True
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            self._initialize_index()  # Reinitialize index on failure
            return False 
