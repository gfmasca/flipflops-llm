"""
Document management use cases for handling study materials.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from src.entities.file import File
from src.entities.topic import Topic


class DocumentManager:
    """Handles operations related to document management."""
    
    def __init__(self, file_repository, embedding_service):
        self.file_repository = file_repository
        self.embedding_service = embedding_service
    
    def upload_document(self, name: str, content: str, file_type: str, topics: Optional[List[str]] = None) -> File:
        """Upload a new document to the system."""
        file_id = str(uuid.uuid4())
        file = File(
            id=file_id,
            name=name,
            content=content,
            file_type=file_type,
            uploaded_at=datetime.now(),
            topics=topics or []
        )
        
        # Save the file
        self.file_repository.save(file)
        
        # Generate embeddings asynchronously
        self.embedding_service.schedule_embedding(file)
        
        return file
    
    def get_document(self, file_id: str) -> Optional[File]:
        """Retrieve a document by its ID."""
        return self.file_repository.get_by_id(file_id)
    
    def list_documents(self, topic: Optional[str] = None) -> List[File]:
        """List all documents, optionally filtered by topic."""
        if topic:
            return self.file_repository.get_by_topic(topic)
        return self.file_repository.get_all()
    
    def delete_document(self, file_id: str) -> bool:
        """Delete a document from the system."""
        file = self.file_repository.get_by_id(file_id)
        if not file:
            return False
        
        # Delete the file
        self.file_repository.delete(file_id)
        
        # Delete associated embeddings
        if file.embedding_id:
            self.embedding_service.delete_embedding(file.embedding_id)
        
        return True 
