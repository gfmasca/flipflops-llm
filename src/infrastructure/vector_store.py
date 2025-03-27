"""
FAISS vector store implementation for document retrieval.
"""
from typing import List, Dict, Any
import os
import pickle

import faiss
import numpy as np


class FAISSVectorStore:
    """Vector store implementation using FAISS."""
    
    def __init__(self, dimension: int = 1536, index_path: str = None):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Embedding dimension
            index_path: Path to load existing index
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.documents = []
        self.doc_ids = []
        
        # Initialize or load existing index
        if index_path and os.path.exists(index_path):
            self._load_index()
        else:
            self._create_index()
    
    def _create_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.doc_ids = []
    
    def _load_index(self):
        """Load an existing FAISS index."""
        with open(self.index_path, 'rb') as f:
            saved_data = pickle.load(f)
            self.index = saved_data['index']
            self.documents = saved_data['documents']
            self.doc_ids = saved_data['doc_ids']
    
    def save(self, save_path: str = None):
        """
        Save the index to disk.
        
        Args:
            save_path: Path to save the index
        """
        path = save_path or self.index_path
        if not path:
            raise ValueError("No save path specified")
        
        with open(path, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'documents': self.documents,
                'doc_ids': self.doc_ids
            }, f)
    
    def add_documents(self, documents: List[Dict[str, Any]], vectors: List[List[float]]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries
            vectors: List of embedding vectors
        """
        if not documents or not vectors:
            return
        
        if len(documents) != len(vectors):
            raise ValueError("Document and vector counts must match")
        
        # Convert vectors to numpy array
        vectors_np = np.array(vectors).astype('float32')
        
        # Add to index
        self.index.add(vectors_np)
        
        # Store documents
        self.documents.extend(documents)
        self.doc_ids.extend([doc.get('id') for doc in documents])
    
    def similarity_search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of document dictionaries
        """
        if not self.index or self.index.ntotal == 0:
            return []
        
        # Convert query vector to numpy array
        query_vector_np = np.array([query_vector]).astype('float32')
        
        # Search index
        distances, indices = self.index.search(query_vector_np, k)
        
        # Retrieve documents
        results = []
        for i in indices[0]:
            if i < len(self.documents):
                results.append(self.documents[i])
        
        return results 
