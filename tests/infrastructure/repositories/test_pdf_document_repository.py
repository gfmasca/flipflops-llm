"""
Unit tests for the PDFDocumentRepository.
"""
import os
import tempfile
import unittest
from datetime import datetime

import pytest

from src.entities.file import File
from src.infrastructure.repositories.pdf_document_repository import PDFDocumentRepository


class TestPDFDocumentRepository(unittest.TestCase):
    """Tests for the PDFDocumentRepository class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize repository with the temporary directory
        self.repository = PDFDocumentRepository(self.temp_dir)
        
        # Path to sample PDF file
        self.sample_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            "test_files", 
            "sample.pdf"
        )
        
        # Ensure the sample file exists
        if not os.path.exists(self.sample_pdf_path):
            pytest.skip("Sample PDF file not found")

    def tearDown(self):
        """Clean up after each test."""
        # Clean up created files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
            
        # Remove the temporary directory
        os.rmdir(self.temp_dir)

    def test_load_document(self):
        """Test loading a PDF document."""
        # Load the sample PDF
        file = self.repository.load_document(self.sample_pdf_path)
        
        # Validate the file entity
        self.assertIsInstance(file, File)
        self.assertEqual(file.name, os.path.basename(self.sample_pdf_path))
        self.assertEqual(file.path, self.sample_pdf_path)
        self.assertEqual(file.file_type, "pdf")
        self.assertIsInstance(file.uploaded_at, datetime)
        self.assertIsNotNone(file.content)
        
        # Check that metadata was extracted
        self.assertIn("page_count", file.metadata)

    def test_save_document(self):
        """Test saving a PDF document."""
        # First load the document
        file = self.repository.load_document(self.sample_pdf_path)
        
        # Make some changes to the content
        original_content = file.content
        file.update_content(file.content + " -- Modified content")
        
        # Save the document
        result = self.repository.save_document(file)
        
        # Validate the result
        self.assertTrue(result)
        
        # Validate that the file is in the repository
        saved_file = self.repository.get_document(file.id)
        self.assertEqual(saved_file.content, file.content)
        
        # Restore original content for other tests
        file.update_content(original_content)

    def test_get_document(self):
        """Test retrieving a document by ID."""
        # First load a document
        file = self.repository.load_document(self.sample_pdf_path)
        
        # Get the document by ID
        retrieved_file = self.repository.get_document(file.id)
        
        # Validate the retrieved file
        self.assertEqual(retrieved_file.id, file.id)
        self.assertEqual(retrieved_file.content, file.content)
        
        # Test retrieving non-existent document
        self.assertIsNone(self.repository.get_document("non-existent-id"))

    def test_list_documents(self):
        """Test listing all documents."""
        # Initially, the repository should be empty
        self.assertEqual(len(self.repository.list_documents()), 0)
        
        # Load a document
        file = self.repository.load_document(self.sample_pdf_path)
        
        # Check that the document is in the list
        documents = self.repository.list_documents()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].id, file.id)

    def test_delete_document(self):
        """Test deleting a document."""
        # First load a document
        file = self.repository.load_document(self.sample_pdf_path)
        
        # Delete the document
        result = self.repository.delete_document(file.id)
        
        # Validate the result
        self.assertTrue(result)
        
        # Check that the document is no longer in the repository
        self.assertIsNone(self.repository.get_document(file.id))
        
        # Verify that attempting to delete a non-existent document returns False
        self.assertFalse(self.repository.delete_document("non-existent-id"))

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
            temp.write(b"This is not a PDF file")
            temp_path = temp.name
        
        # Attempt to load the text file as a PDF
        with self.assertRaises(ValueError):
            self.repository.load_document(temp_path)
        
        # Clean up
        os.unlink(temp_path) 
