"""
Base implementation for document repositories with common functionality.
"""
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import magic

from src.entities.file import File
from src.interfaces.repositories.document_repository import DocumentRepository


class BaseDocumentRepository(DocumentRepository):
    """Base class for document repositories."""

    def __init__(self, storage_dir: str = "./storage/documents"):
        """
        Initialize the repository.
        
        Args:
            storage_dir: Directory to store documents
        """
        self.storage_dir = storage_dir
        self.documents: Dict[str, File] = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

    def get_document(self, id: str) -> Optional[File]:
        """
        Retrieve a document by its ID.
        
        Args:
            id: Document identifier
            
        Returns:
            File entity if found, None otherwise
        """
        return self.documents.get(id)

    def list_documents(self) -> List[File]:
        """
        List all available documents.
        
        Returns:
            List of File entities
        """
        return list(self.documents.values())

    def delete_document(self, id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            id: Document identifier
            
        Returns:
            True if the document was deleted successfully, False otherwise
        """
        if id not in self.documents:
            return False
            
        file = self.documents[id]
        try:
            if os.path.exists(file.path):
                os.remove(file.path)
            del self.documents[id]
            return True
        except Exception as e:
            print(f"Error deleting document {id}: {str(e)}")
            return False

    def _get_mime_type(self, file_path: str) -> str:
        """
        Get the MIME type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type of the file
        """
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)

    def _generate_id(self) -> str:
        """
        Generate a unique ID for a document.
        
        Returns:
            Unique ID
        """
        return str(uuid.uuid4())

    def _get_storage_path(self, filename: str, extension: str) -> str:
        """
        Get the storage path for a document.
        
        Args:
            filename: Original filename
            extension: File extension
            
        Returns:
            Storage path
        """
        safe_filename = os.path.basename(filename)
        return os.path.join(self.storage_dir, f"{safe_filename}.{extension}") 
