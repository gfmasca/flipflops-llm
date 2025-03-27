"""
Implementation of document processing service.
"""
import os
import re
import uuid
import logging
from typing import Dict, List, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.entities.file import File
from src.entities.text_chunk import TextChunk
from src.entities.topic import Topic
from src.interfaces.repositories.document_repository import DocumentRepository
from src.interfaces.services.document_processing_service import DocumentProcessingService


# Configure logger
logger = logging.getLogger(__name__)


class DocumentProcessingUseCase(DocumentProcessingService):
    """Implementation of document processing service."""

    def __init__(self, document_repository: DocumentRepository):
        """
        Initialize the document processing use case.
        
        Args:
            document_repository: Repository for document storage and retrieval
        """
        self.document_repository = document_repository
        
        # Default configuration for chunking
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        # Simple topic categories
        self.topics = {
            "business": Topic(
                id="business",
                name="Business",
                description="Business, finance, and economics content",
                keywords=["company", "market", "finance", "business", "economic"]
            ),
            "technology": Topic(
                id="technology",
                name="Technology",
                description="Technology, computing, and IT content",
                keywords=["software", "computer", "technology", "data", "digital"]
            ),
            "science": Topic(
                id="science",
                name="Science",
                description="Scientific research and discoveries",
                keywords=["science", "research", "study", "analysis", "experiment"]
            ),
            "legal": Topic(
                id="legal",
                name="Legal",
                description="Legal documents and regulations",
                keywords=["legal", "law", "regulation", "compliance", "contract"]
            ),
            "general": Topic(
                id="general",
                name="General",
                description="General content that doesn't fit other categories",
                keywords=[]
            )
        }

    def process_document(self, file_path: str) -> File:
        """
        Process a document from the given path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Processed File entity
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file format is not supported
        """
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load document using repository
            file = self.document_repository.load_document(file_path)
            
            # Extract additional metadata
            additional_metadata = self.extract_metadata(file)
            
            # Merge additional metadata with existing metadata
            for key, value in additional_metadata.items():
                if key not in file.metadata:
                    file.metadata[key] = value
            
            # Categorize the document
            topic = self.categorize_document(file)
            file.metadata["topic"] = topic.name
            file.metadata["topic_id"] = topic.id
            
            logger.info(f"Document processed successfully: {file.id}")
            return file
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except ValueError as e:
            logger.error(f"Invalid document format: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Error reading document: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing document: {str(e)}")
            raise ValueError(f"Failed to process document: {str(e)}")

    def chunk_document(self, file: File) -> List[TextChunk]:
        """
        Split a document into chunks for further processing.
        
        Args:
            file: File entity to chunk
            
        Returns:
            List of TextChunk entities
            
        Raises:
            ValueError: If chunking fails or the document type is not supported
        """
        logger.info(f"Chunking document: {file.id}")
        
        try:
            # Use LangChain's RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                is_separator_regex=False
            )
            
            # Split the document content
            texts = text_splitter.split_text(file.content)
            
            # Create TextChunk entities
            chunks = []
            for i, text in enumerate(texts):
                chunk_id = str(uuid.uuid4())
                chunk = TextChunk(
                    id=chunk_id,
                    text=text,
                    document_id=file.id,
                    chunk_index=i,
                    metadata={
                        "source": file.path,
                        "file_type": file.file_type
                    }
                )
                chunks.append(chunk)
            
            logger.info(f"Document {file.id} split into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking document {file.id}: {str(e)}")
            raise ValueError(f"Failed to chunk document: {str(e)}")

    def extract_metadata(self, file: File) -> Dict[str, Any]:
        """
        Extract enhanced metadata from a document.
        
        Args:
            file: File entity to extract metadata from
            
        Returns:
            Dictionary of extracted metadata
            
        Raises:
            ValueError: If metadata extraction fails
        """
        logger.info(f"Extracting metadata from document: {file.id}")
        
        try:
            metadata = {}
            
            # Add basic metadata
            metadata["word_count"] = len(file.content.split())
            metadata["char_count"] = len(file.content)
            
            # Extract title if not already available
            if "title" not in file.metadata:
                title = self._extract_title(file)
                if title:
                    metadata["title"] = title
            
            # Extract dates if not already available
            if "creation_date" not in file.metadata:
                date = self._extract_date(file)
                if date:
                    metadata["extracted_date"] = date
                    
            # Extract author if not already available
            if "author" not in file.metadata:
                author = self._extract_author(file)
                if author:
                    metadata["author"] = author
            
            logger.info(f"Metadata extracted successfully from document {file.id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from document {file.id}: {str(e)}")
            # Return empty metadata rather than raising an exception
            return {}

    def categorize_document(self, file: File) -> Topic:
        """
        Categorize a document based on its content.
        
        Args:
            file: File entity to categorize
            
        Returns:
            Topic classification for the document
            
        Raises:
            ValueError: If categorization fails
        """
        logger.info(f"Categorizing document: {file.id}")
        
        try:
            # Simple keyword-based categorization
            content = file.content.lower()
            
            # Count keyword occurrences for each topic
            topic_scores = {}
            for topic_id, topic in self.topics.items():
                if topic_id == "general":
                    continue  # Skip the general category for now
                    
                score = 0
                for keyword in topic.keywords:
                    score += content.count(keyword.lower())
                
                topic_scores[topic_id] = score
            
            # Find the topic with the highest score
            if topic_scores:
                max_score = max(topic_scores.values())
                
                # If we have a meaningful score, return that topic
                if max_score > 0:
                    best_topic_id = max(topic_scores, key=topic_scores.get)
                    selected_topic = self.topics[best_topic_id]
                    selected_topic.confidence = max_score / sum(1 for _ in file.content.split())
                    return selected_topic
            
            # Default to general category if no clear match
            general_topic = self.topics["general"]
            general_topic.confidence = 1.0
            return general_topic
            
        except Exception as e:
            logger.error(f"Error categorizing document {file.id}: {str(e)}")
            # Return general category rather than raising an exception
            general_topic = self.topics["general"]
            general_topic.confidence = 0.0
            return general_topic

    def _extract_title(self, file: File) -> Optional[str]:
        """
        Extract a title from document content.
        
        Args:
            file: File entity
            
        Returns:
            Extracted title or None if not found
        """
        # Check if PDF has title in metadata
        if file.file_type == "pdf" and "title" in file.metadata:
            return file.metadata["title"]
        
        # For markdown, look for first heading
        if file.file_type == "markdown":
            lines = file.content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    return line.replace('# ', '').strip()
        
        # For text files, use the first non-empty line
        if file.file_type in ["text", "csv"]:
            lines = file.content.split('\n')
            for line in lines:
                if line.strip():
                    # Limit title length
                    title = line.strip()
                    return title[:100] + ('...' if len(title) > 100 else '')
        
        # Fallback to filename
        return os.path.splitext(file.name)[0]

    def _extract_date(self, file: File) -> Optional[str]:
        """
        Extract a date from document content or metadata.
        
        Args:
            file: File entity
            
        Returns:
            Extracted date or None if not found
        """
        # Check metadata first
        for key in ["creation_date", "modification_date", "date"]:
            if key in file.metadata:
                return str(file.metadata[key])
        
        # Look for date patterns in content (simple regex)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}\.\d{2}\.\d{4}'  # DD.MM.YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, file.content)
            if match:
                return match.group(0)
        
        return None

    def _extract_author(self, file: File) -> Optional[str]:
        """
        Extract author information from document.
        
        Args:
            file: File entity
            
        Returns:
            Extracted author or None if not found
        """
        # Check metadata first
        if "author" in file.metadata:
            return file.metadata["author"]
        
        # Look for common author patterns
        author_patterns = [
            r'author[s]?[\s:]+([^\n,]+)',
            r'by[\s:]+([^\n,]+)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, file.content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None 
