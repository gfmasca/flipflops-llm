"""
FAISS Embedding Service implementation.

This module provides an implementation of the EmbeddingService interface
using FAISS for document embeddings.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Union

from sentence_transformers import SentenceTransformer

from src.interfaces.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class FAISSEmbeddingService(EmbeddingService):
    """
    Implementation of EmbeddingService using FAISS and SentenceTransformers.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/distiluse-base-multilingual-cased-v1"):
        """
        Initialize the FAISS embedding service.
        
        Args:
            model_name: Name of the sentence transformers model to use
        """
        logger.info(f"Initializing FAISS Embedding Service with model {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            logger.warning("Empty text list provided to get_embeddings")
            return np.array([])
        
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        return self.model.encode(texts, convert_to_numpy=True)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to generate embedding for
            
        Returns:
            Numpy array of the embedding
        """
        if not text:
            logger.warning("Empty text provided to get_embedding")
            return np.array([])
        
        logger.debug("Generating embedding for a single text")
        return self.model.encode(text, convert_to_numpy=True)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity value
        """
        # Normalize the embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            logger.warning("Zero norm encountered in similarity calculation")
            return 0.0
        
        # Calculate dot product of normalized vectors (cosine similarity)
        return np.dot(embedding1, embedding2) / (norm1 * norm2) 
