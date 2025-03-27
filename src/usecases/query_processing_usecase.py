"""
Implementation of query processing and retrieval service.
"""
import re
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.entities.embedding import Embedding
from src.entities.query import Query
from src.interfaces.services.query_service import QueryService
from src.interfaces.services.embedding_service import EmbeddingService
from src.interfaces.repositories.embedding_repository import EmbeddingRepository


# Configure logger
logger = logging.getLogger(__name__)


class QueryProcessingUseCase(QueryService):
    """Implementation of query processing and retrieval service."""

    # Portuguese stopwords
    PORTUGUESE_STOPWORDS = {
        "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até",
        "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois",
        "do", "dos", "e", "é", "ela", "elas", "ele", "eles", "em", "entre", "era",
        "eram", "essa", "essas", "esse", "esses", "esta", "estas", "este", "estes",
        "eu", "foi", "foram", "há", "isso", "isto", "já", "lhe", "lhes", "mais", "mas",
        "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "não", "nas",
        "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "numa",
        "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual",
        "quando", "que", "quem", "são", "se", "seja", "sem", "seu", "seus", "só",
        "sua", "suas", "também", "te", "tem", "tém", "tu", "tua", "tuas", "um", "uma", "você"
    }

    # Common question patterns in Portuguese
    QUESTION_PATTERNS = [
        r'^o que é', r'^o que são', r'^quem é', r'^quem são',
        r'^como', r'^quando', r'^onde', r'^por que', r'^qual', r'^quais',
        r'^explique', r'^defina', r'^descreva', r'^compare', r'^analise'
    ]

    def __init__(
        self, 
        embedding_service: EmbeddingService,
        embedding_repository: EmbeddingRepository,
        min_score_threshold: float = 0.6,
        max_context_length: int = 5000
    ):
        """
        Initialize the query processing use case.
        
        Args:
            embedding_service: Service for generating embeddings
            embedding_repository: Repository for storing and retrieving embeddings
            min_score_threshold: Minimum similarity score for relevant documents
            max_context_length: Maximum total length of context to include
        """
        self.embedding_service = embedding_service
        self.embedding_repository = embedding_repository
        self.min_score_threshold = min_score_threshold
        self.max_context_length = max_context_length
        
        logger.info("Initialized query processing service")

    def process_query(self, query_text: str) -> Query:
        """
        Process a raw query text and convert it to a structured Query object.
        
        Args:
            query_text: The raw query text from the user
            
        Returns:
            A structured Query object
            
        Raises:
            ValueError: If the query text is invalid or empty
        """
        # Validate input
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        # Trim whitespace
        query_text = query_text.strip()
        
        # Create unique ID for the query
        query_id = str(uuid.uuid4())
        
        # Extract metadata about the query
        metadata = self._extract_query_metadata(query_text)
        
        # Create and return the Query object
        query = Query(
            id=query_id,
            text=query_text,
            metadata=metadata
        )
        
        logger.info(f"Processed query: {query_text[:50]}{'...' if len(query_text) > 50 else ''}")
        return query

    def retrieve_relevant_documents(self, query: Query, top_k: int = 5) -> List[Embedding]:
        """
        Retrieve relevant document chunks for the given query.
        
        Args:
            query: The processed query
            top_k: Maximum number of results to retrieve
            
        Returns:
            List of relevant document embeddings
            
        Raises:
            ValueError: If the query is invalid
            RuntimeError: If retrieval fails
        """
        # Validate input
        if not query or not query.text:
            raise ValueError("Query cannot be empty")
        
        try:
            logger.info(f"Retrieving documents for query: {query.id}")
            
            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search for similar documents
            similar_embeddings = self.embedding_repository.search_similar(
                query_embedding=query_embedding,
                top_k=top_k * 2  # Retrieve more for filtering
            )
            
            # Rank and filter results
            ranked_results = self.rank_results(query, similar_embeddings)
            
            # Limit to requested number
            final_results = ranked_results[:top_k]
            
            logger.info(f"Retrieved {len(final_results)} relevant documents for query {query.id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents for query {query.id}: {str(e)}")
            raise RuntimeError(f"Failed to retrieve relevant documents: {str(e)}")

    def rank_results(self, query: Query, results: List[Embedding]) -> List[Embedding]:
        """
        Rank and filter results by relevance.
        
        Args:
            query: The processed query
            results: List of retrieved embeddings to rank
            
        Returns:
            Ranked list of embeddings
            
        Raises:
            ValueError: If the query or results are invalid
        """
        if not query:
            raise ValueError("Query cannot be None")
        if not results:
            return []
        
        logger.info(f"Ranking {len(results)} results for query {query.id}")
        
        # Calculate scores for each result
        scored_results = []
        for embedding in results:
            # Start with the semantic similarity score (assumed to be in metadata)
            score = embedding.metadata.get("score", 0.5)
            
            # Apply additional ranking factors
            final_score = self._calculate_final_score(query, embedding, score)
            
            # Add to scored results if above threshold
            if final_score >= self.min_score_threshold:
                # Add the score to metadata for future reference
                embedding.metadata["final_score"] = final_score
                scored_results.append((embedding, final_score))
        
        # Sort by final score (descending)
        sorted_results = [e for e, s in sorted(scored_results, key=lambda x: x[1], reverse=True)]
        
        logger.info(f"Ranked {len(sorted_results)} results above threshold for query {query.id}")
        return sorted_results

    def prepare_context(self, query: Query, results: List[Embedding]) -> List[str]:
        """
        Prepare context from retrieved results for LLM prompts.
        
        Args:
            query: The processed query
            results: Ranked list of relevant embeddings
            
        Returns:
            List of formatted context passages
        """
        if not results:
            return []
        
        logger.info(f"Preparing context from {len(results)} embeddings for query {query.id}")
        
        context_passages = []
        total_length = 0
        
        for embedding in results:
            # Format the passage with metadata
            source = embedding.metadata.get("source", "Unknown")
            
            # Create formatted passage
            passage = f"{embedding.text}\n\nFonte: {source}"
            
            # Check if adding this passage would exceed max context length
            if total_length + len(passage) > self.max_context_length:
                break
                
            context_passages.append(passage)
            total_length += len(passage)
        
        logger.info(f"Prepared {len(context_passages)} context passages")
        return context_passages

    def _extract_query_metadata(self, query_text: str) -> Dict[str, Any]:
        """
        Extract metadata from the query text.
        
        Args:
            query_text: The raw query text
            
        Returns:
            Dictionary of query metadata
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "length": len(query_text),
            "word_count": len(query_text.split()),
            "is_question": False
        }
        
        # Check if it's a question
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, query_text.lower()):
                metadata["is_question"] = True
                metadata["question_type"] = pattern.replace('^', '').replace('\\', '')
                break
        
        return metadata

    def _preprocess_query(self, query_text: str) -> str:
        """
        Preprocess query text for better retrieval.
        
        Args:
            query_text: The raw query text
            
        Returns:
            Preprocessed query text
        """
        # Lowercase
        text = query_text.lower()
        
        # Remove punctuation (except accented characters)
        text = re.sub(r'[^\w\sáàâãéèêíóôõúüçñ]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _calculate_final_score(self, query: Query, embedding: Embedding, base_score: float) -> float:
        """
        Calculate the final relevance score for an embedding.
        
        Args:
            query: The processed query
            embedding: The embedding to score
            base_score: The base semantic similarity score
            
        Returns:
            The final relevance score
        """
        # Start with the base score (semantic similarity)
        score = base_score
        
        # Adjust based on source type (if available)
        source_type = embedding.metadata.get("file_type", "")
        if source_type == "pdf":
            # Slight boost for PDF documents (often more authoritative)
            score *= 1.05
        
        # Consider document recency (if available)
        if "creation_date" in embedding.metadata:
            try:
                # Parse date and calculate recency factor
                creation_date = datetime.fromisoformat(embedding.metadata["creation_date"])
                now = datetime.now()
                days_old = (now - creation_date).days
                
                # Slight recency boost (max 10%)
                recency_factor = max(0.9, 1.0 - (days_old / 365))
                score *= recency_factor
            except (ValueError, TypeError):
                # If date parsing fails, ignore this factor
                pass
                
        # Consider text length (favor more substantial chunks slightly)
        text_length = len(embedding.text)
        if text_length > 500:
            score *= 1.05
        elif text_length < 100:
            score *= 0.95
            
        return score 
