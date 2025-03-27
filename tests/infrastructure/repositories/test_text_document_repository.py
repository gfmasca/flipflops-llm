"""
Unit tests for the TextDocumentRepository.
"""
import os
import tempfile
import unittest
from datetime import datetime

import pytest

from src.entities.file import File
from src.infrastructure.repositories.text_document_repository import TextDocumentRepository


class TestTextDocumentRepository(unittest.TestCase):
    """Tests for the TextDocumentRepository class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize repository with the temporary directory
        self.repository = TextDocumentRepository(self.temp_dir)
        
        # Paths to sample files
        test_files_dir = os.path.join(os.path.dirname(__file__), "test_files")
        self.sample_txt_path = os.path.join(test_files_dir, "sample.txt")
        self.sample_md_path = os.path.join(test_files_dir, "sample.md")
        
        # Ensure the sample files exist
        if not os.path.exists(self.sample_txt_path):
            pytest.skip("Sample TXT file not found")
        if not os.path.exists(self.sample_md_path):
            pytest.skip("Sample MD file not found")

    def tearDown(self):
        """Clean up after each test."""
        # Clean up created files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
            
        # Remove the temporary directory
        os.rmdir(self.temp_dir)

    def test_load_txt_document(self):
        """Test loading a TXT document."""
        # Load the sample TXT
        file = self.repository.load_document(self.sample_txt_path)
        
        # Validate the file entity
        self.assertIsInstance(file, File)
        self.assertEqual(file.name, os.path.basename(self.sample_txt_path))
        self.assertEqual(file.path, self.sample_txt_path)
        self.assertEqual(file.file_type, "text")
        self.assertIsInstance(file.uploaded_at, datetime)
        self.assertIsNotNone(file.content)
        
        # Check that metadata was extracted
        self.assertIn("line_count", file.metadata)
        self.assertIn("word_count", file.metadata)
        self.assertIn("char_count", file.metadata)

    def test_load_md_document(self):
        """Test loading a Markdown document."""
        # Load the sample Markdown
        file = self.repository.load_document(self.sample_md_path)
        
        # Validate the file entity
        self.assertIsInstance(file, File)
        self.assertEqual(file.name, os.path.basename(self.sample_md_path))
        self.assertEqual(file.path, self.sample_md_path)
        self.assertEqual(file.file_type, "markdown")
        self.assertIsInstance(file.uploaded_at, datetime)
        self.assertIsNotNone(file.content)
        
        # Check that metadata was extracted
        self.assertIn("line_count", file.metadata)
        self.assertIn("word_count", file.metadata)
        self.assertIn("char_count", file.metadata)
        self.assertIn("title", file.metadata)
        self.assertEqual(file.metadata["title"], "Sample Markdown Document")

    def test_save_document(self):
        """Test saving a text document."""
        # First load the document
        file = self.repository.load_document(self.sample_txt_path)
        
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
        file = self.repository.load_document(self.sample_txt_path)
        
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
        txt_file = self.repository.load_document(self.sample_txt_path)
        md_file = self.repository.load_document(self.sample_md_path)
        
        # Check that both documents are in the list
        documents = self.repository.list_documents()
        self.assertEqual(len(documents), 2)
        document_ids = [doc.id for doc in documents]
        self.assertIn(txt_file.id, document_ids)
        self.assertIn(md_file.id, document_ids)

    def test_delete_document(self):
        """Test deleting a document."""
        # First load a document
        file = self.repository.load_document(self.sample_txt_path)
        
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
        # Create a temporary PDF file (simulated)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(b"%PDF-1.4\nThis is a fake PDF file")
            temp_path = temp.name
        
        # Attempt to load the PDF file as a text document
        with self.assertRaises(ValueError):
            self.repository.load_document(temp_path)
        
        # Clean up
        os.unlink(temp_path) 
