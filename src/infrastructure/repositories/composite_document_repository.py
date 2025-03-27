"""
Composite document repository that delegates to appropriate implementations.
"""
import os
from typing import Dict, List, Optional, Type

from src.entities.file import File
from src.interfaces.repositories.document_repository import DocumentRepository
from src.infrastructure.repositories.pdf_document_repository import PDFDocumentRepository
from src.infrastructure.repositories.text_document_repository import TextDocumentRepository
from src.infrastructure.repositories.csv_document_repository import CSVDocumentRepository


class CompositeDocumentRepository(DocumentRepository):
    """
    Composite repository that delegates to specific repositories
    based on file type/extension.
    """

    def __init__(self, storage_dir: str = "./storage/documents"):
        """
        Initialize the composite repository.
        
        Args:
            storage_dir: Directory to store documents
        """
        self.storage_dir = storage_dir
        self.repositories: Dict[str, DocumentRepository] = {}
        self.documents: Dict[str, File] = {}
        
        # Initialize repositories for different file types
        self._init_repositories()
        
    def _init_repositories(self) -> None:
        """Initialize specific repositories for each file type."""
        pdf_repo = PDFDocumentRepository(self.storage_dir)
        text_repo = TextDocumentRepository(self.storage_dir)
        csv_repo = CSVDocumentRepository(self.storage_dir)
        
        # Map file extensions to repositories
        self.repositories = {
            # PDF
            "pdf": pdf_repo,
            
            # Text formats
            "txt": text_repo,
            "md": text_repo,
            "markdown": text_repo,
            
            # CSV format
            "csv": csv_repo
        }

    def load_document(self, path: str) -> File:
        """
        Load a document from the given path and create a File entity.
        
        Args:
            path: Path to the document file
            
        Returns:
            File entity with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file format is not supported
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        # Get file extension
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        
        # Get appropriate repository
        repo = self._get_repository_for_extension(ext)
        if not repo:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Load document using the appropriate repository
        file = repo.load_document(path)
        
        # Store document in the composite repository
        self.documents[file.id] = file
        
        return file

    def save_document(self, file: File) -> bool:
        """
        Save a document to storage.
        
        Args:
            file: File entity to save
            
        Returns:
            True if the document was saved successfully, False otherwise
            
        Raises:
            IOError: If there's an error writing the file
            ValueError: If the file format is not supported
        """
        # Get file extension
        ext = os.path.splitext(file.path)[1].lower().lstrip('.')
        if not ext:
            ext = file.file_type
        
        # Get appropriate repository
        repo = self._get_repository_for_extension(ext)
        if not repo:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Save document using the appropriate repository
        result = repo.save_document(file)
        
        # Store document in the composite repository if save was successful
        if result:
            self.documents[file.id] = file
        
        return result

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
        ext = os.path.splitext(file.path)[1].lower().lstrip('.')
        
        # Get appropriate repository
        repo = self._get_repository_for_extension(ext)
        if not repo:
            return False
        
        # Delete document using the appropriate repository
        result = repo.delete_document(id)
        
        # Remove document from the composite repository if delete was successful
        if result:
            del self.documents[id]
        
        return result

    def _get_repository_for_extension(self, extension: str) -> Optional[DocumentRepository]:
        """
        Get the appropriate repository for the given file extension.
        
        Args:
            extension: File extension
            
        Returns:
            DocumentRepository implementation for the extension,
            or None if not supported
        """
        return self.repositories.get(extension.lower()) 
