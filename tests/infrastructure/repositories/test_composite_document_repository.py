"""
Unit tests for the CompositeDocumentRepository.
"""
import os
import tempfile
import unittest
from datetime import datetime

import pytest

from src.entities.file import File
from src.infrastructure.repositories.composite_document_repository import (
    CompositeDocumentRepository
)


class TestCompositeDocumentRepository(unittest.TestCase):
    """Tests for the CompositeDocumentRepository class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize repository with the temporary directory
        self.repository = CompositeDocumentRepository(self.temp_dir)
        
        # Paths to sample files - corrected path
        test_files_dir = os.path.join("tests", "infrastructure", "repositories", "test_files")
        self.sample_txt_path = os.path.join(test_files_dir, "sample.txt")
        self.sample_md_path = os.path.join(test_files_dir, "sample.md")
        self.sample_csv_path = os.path.join(test_files_dir, "sample.csv")
        self.sample_pdf_path = os.path.join(test_files_dir, "sample.pdf")
        
        # Print file paths for debugging
        print(f"TXT file: {self.sample_txt_path}, exists: {os.path.exists(self.sample_txt_path)}")
        print(f"MD file: {self.sample_md_path}, exists: {os.path.exists(self.sample_md_path)}")
        print(f"CSV file: {self.sample_csv_path}, exists: {os.path.exists(self.sample_csv_path)}")
        print(f"PDF file: {self.sample_pdf_path}, exists: {os.path.exists(self.sample_pdf_path)}")
        
        # Ensure the sample files exist
        missing_files = []
        if not os.path.exists(self.sample_txt_path):
            missing_files.append("sample.txt")
        if not os.path.exists(self.sample_md_path):
            missing_files.append("sample.md")
        if not os.path.exists(self.sample_csv_path):
            missing_files.append("sample.csv")
        if not os.path.exists(self.sample_pdf_path):
            missing_files.append("sample.pdf")
            
        if missing_files:
            print(f"DEBUG: Skipping test due to missing files: {', '.join(missing_files)}")
            pytest.skip(f"Sample files not found: {', '.join(missing_files)}")

    def tearDown(self):
        """Clean up after each test."""
        # Clean up created files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
            
        # Remove the temporary directory
        os.rmdir(self.temp_dir)

    def test_load_pdf_document(self):
        """Test loading a PDF document."""
        file = self.repository.load_document(self.sample_pdf_path)
        
        self.assertIsInstance(file, File)
        self.assertEqual(file.file_type, "pdf")
        self.assertIn("page_count", file.metadata)

    def test_load_text_document(self):
        """Test loading a text document."""
        file = self.repository.load_document(self.sample_txt_path)
        
        self.assertIsInstance(file, File)
        self.assertEqual(file.file_type, "text")
        self.assertIn("line_count", file.metadata)

    def test_load_markdown_document(self):
        """Test loading a markdown document."""
        file = self.repository.load_document(self.sample_md_path)
        
        self.assertIsInstance(file, File)
        self.assertEqual(file.file_type, "markdown")
        self.assertIn("title", file.metadata)

    def test_load_csv_document(self):
        """Test loading a CSV document."""
        file = self.repository.load_document(self.sample_csv_path)
        
        self.assertIsInstance(file, File)
        self.assertEqual(file.file_type, "csv")
        self.assertIn("row_count", file.metadata)
        self.assertIn("column_count", file.metadata)

    def test_save_document(self):
        """Test saving documents of different types."""
        # Load and save a text document
        txt_file = self.repository.load_document(self.sample_txt_path)
        txt_file.update_content(txt_file.content + " -- Modified")
        self.assertTrue(self.repository.save_document(txt_file))
        
        # Load and save a CSV document
        csv_file = self.repository.load_document(self.sample_csv_path)
        csv_file.update_content(csv_file.content + "\nNewRow,1,2,3,4")
        self.assertTrue(self.repository.save_document(csv_file))
        
        # Verify documents are saved correctly
        self.assertEqual(len(self.repository.list_documents()), 2)

    def test_get_document(self):
        """Test retrieving a document by ID."""
        # Load documents of different types
        txt_file = self.repository.load_document(self.sample_txt_path)
        csv_file = self.repository.load_document(self.sample_csv_path)
        
        # Get documents by ID
        txt_retrieved = self.repository.get_document(txt_file.id)
        csv_retrieved = self.repository.get_document(csv_file.id)
        
        # Validate retrieved documents
        self.assertEqual(txt_retrieved.id, txt_file.id)
        self.assertEqual(csv_retrieved.id, csv_file.id)
        
        # Test non-existent document
        self.assertIsNone(self.repository.get_document("non-existent-id"))

    def test_list_documents(self):
        """Test listing all documents."""
        # Initially repository should be empty
        self.assertEqual(len(self.repository.list_documents()), 0)
        
        # Load documents of different types
        self.repository.load_document(self.sample_txt_path)
        self.repository.load_document(self.sample_md_path)
        self.repository.load_document(self.sample_csv_path)
        self.repository.load_document(self.sample_pdf_path)
        
        # Check all documents are listed
        docs = self.repository.list_documents()
        self.assertEqual(len(docs), 4)
        
        # Check document types
        file_types = [doc.file_type for doc in docs]
        self.assertIn("text", file_types)
        self.assertIn("markdown", file_types)
        self.assertIn("csv", file_types)
        self.assertIn("pdf", file_types)

    def test_delete_document(self):
        """Test deleting documents."""
        # Load documents
        txt_file = self.repository.load_document(self.sample_txt_path)
        pdf_file = self.repository.load_document(self.sample_pdf_path)
        
        # Delete one document
        self.assertTrue(self.repository.delete_document(txt_file.id))
        
        # Verify it's deleted
        self.assertIsNone(self.repository.get_document(txt_file.id))
        
        # Verify the other document is still there
        self.assertIsNotNone(self.repository.get_document(pdf_file.id))
        
        # Test deleting non-existent document
        self.assertFalse(self.repository.delete_document("non-existent-id"))

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as temp:
            temp.write(b"This is an unsupported file type")
            temp_path = temp.name
        
        # Attempt to load the unsupported file
        with self.assertRaises(ValueError):
            self.repository.load_document(temp_path)
        
        # Clean up
        os.unlink(temp_path) 
