"""
Implementation of embedding generation service.
"""
import uuid
import logging
from typing import List, Optional

from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings

from src.entities.embedding import Embedding
from src.entities.file import File
from src.entities.query import Query
from src.entities.text_chunk import TextChunk
from src.interfaces.services.embedding_service import EmbeddingService
from src.interfaces.services.document_processing_service import DocumentProcessingService
from src.interfaces.repositories.embedding_repository import EmbeddingRepository


# Configure logger
logger = logging.getLogger(__name__)


class EmbeddingGenerationUseCase(EmbeddingService):
    """Implementation of embedding generation service."""

    def __init__(
        self,
        embedding_repository: EmbeddingRepository,
        document_processor: Optional[DocumentProcessingService] = None,
        model_name: str = "text-embedding-ada-002",
        use_openai: bool = True,
    ):
        """
        Initialize the embedding generation use case.
        
        Args:
            embedding_repository: Repository for storing and retrieving embeddings
            document_processor: Service for processing and chunking documents
            model_name: Name of the embedding model to use
            use_openai: Whether to use OpenAI or HuggingFace for embeddings
        """
        self.embedding_repository = embedding_repository
        self.document_processor = document_processor
        self.model_name = model_name
        self.use_openai = use_openai
        
        # Initialize embedding model
        self._initialize_embedding_model()

    def _initialize_embedding_model(self) -> None:
        """Initialize the embedding model."""
        try:
            if self.use_openai:
                logger.info(f"Initializing OpenAI embedding model: {self.model_name}")
                self.model = OpenAIEmbeddings(model=self.model_name)
            else:
                logger.info(f"Initializing HuggingFace embedding model: {self.model_name}")
                self.model = HuggingFaceEmbeddings(model_name=self.model_name)
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise ValueError(f"Failed to initialize embedding model: {str(e)}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
            
        Raises:
            ValueError: If the text cannot be embedded
        """
        try:
            # Ensure text is not empty
            if not text or not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
            
            # Generate embedding using the model
            embedding = self.model.embed_query(text)
            
            logger.info(f"Generated embedding for text ({len(embedding)} dimensions)")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise ValueError(f"Failed to generate embedding: {str(e)}")

    def embed_document(self, file: File) -> List[Embedding]:
        """
        Generate embeddings for a document.
        
        Args:
            file: The document to embed
            
        Returns:
            List of embeddings for the document chunks
            
        Raises:
            ValueError: If the document cannot be embedded
        """
        try:
            logger.info(f"Embedding document: {file.id}")
            
            # Get chunks using document processor if available
            chunks = []
            if self.document_processor:
                chunks = self.document_processor.chunk_document(file)
            else:
                # Use basic chunking if no document processor is available
                chunk_id = str(uuid.uuid4())
                chunks = [
                    TextChunk(
                        id=chunk_id,
                        text=file.content,
                        document_id=file.id,
                        chunk_index=0,
                        metadata={"source": file.path}
                    )
                ]
            
            # Generate embeddings for each chunk
            embeddings = []
            for chunk in chunks:
                # Generate embedding
                vector = self.generate_embedding(chunk.text)
                
                # Create embedding entity
                embedding_id = str(uuid.uuid4())
                embedding = Embedding(
                    id=embedding_id,
                    vector=vector,
                    text=chunk.text,
                    document_id=file.id,
                    chunk_id=chunk.id,
                    metadata={
                        "source": file.path,
                        "file_type": file.file_type,
                        "chunk_index": chunk.chunk_index
                    }
                )
                
                # Save to repository
                if self.embedding_repository.save_embedding(embedding):
                    embeddings.append(embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings for document {file.id}")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding document {file.id}: {str(e)}")
            raise ValueError(f"Failed to embed document: {str(e)}")

    def embed_query(self, query: Query) -> List[float]:
        """
        Generate an embedding for a search query.
        
        Args:
            query: The query to embed
            
        Returns:
            The embedding vector for the query
            
        Raises:
            ValueError: If the query cannot be embedded
        """
        try:
            logger.info(f"Embedding query: {query.id}")
            
            # Generate embedding for the query text
            vector = self.generate_embedding(query.text)
            
            # Optionally save query embedding to repository
            embedding_id = str(uuid.uuid4())
            embedding = Embedding(
                id=embedding_id,
                vector=vector,
                text=query.text,
                metadata={"query_id": query.id}
            )
            
            # Save to repository (but don't raise error if this fails)
            try:
                self.embedding_repository.save_embedding(embedding)
            except Exception as e:
                logger.warning(f"Failed to save query embedding: {str(e)}")
            
            logger.info(f"Generated embedding for query {query.id}")
            return vector
        except Exception as e:
            logger.error(f"Error embedding query {query.id}: {str(e)}")
            raise ValueError(f"Failed to embed query: {str(e)}") 
