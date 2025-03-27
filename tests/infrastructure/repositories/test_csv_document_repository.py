"""
Unit tests for the CSVDocumentRepository.
"""
import os
import tempfile
import unittest
from datetime import datetime

import pytest

from src.entities.file import File
from src.infrastructure.repositories.csv_document_repository import CSVDocumentRepository


class TestCSVDocumentRepository(unittest.TestCase):
    """Tests for the CSVDocumentRepository class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize repository with the temporary directory
        self.repository = CSVDocumentRepository(self.temp_dir)
        
        # Path to sample CSV file
        self.sample_csv_path = os.path.join(
            os.path.dirname(__file__), 
            "test_files", 
            "sample.csv"
        )
        
        # Ensure the sample file exists
        if not os.path.exists(self.sample_csv_path):
            pytest.skip("Sample CSV file not found")

    def tearDown(self):
        """Clean up after each test."""
        # Clean up created files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
            
        # Remove the temporary directory
        os.rmdir(self.temp_dir)

    def test_load_document(self):
        """Test loading a CSV document."""
        # Load the sample CSV
        file = self.repository.load_document(self.sample_csv_path)
        
        # Validate the file entity
        self.assertIsInstance(file, File)
        self.assertEqual(file.name, os.path.basename(self.sample_csv_path))
        self.assertEqual(file.path, self.sample_csv_path)
        self.assertEqual(file.file_type, "csv")
        self.assertIsInstance(file.uploaded_at, datetime)
        self.assertIsNotNone(file.content)
        
        # Check that metadata was extracted
        self.assertIn("row_count", file.metadata)
        self.assertIn("column_count", file.metadata)
        self.assertIn("columns", file.metadata)
        self.assertIn("dtypes", file.metadata)
        self.assertIn("sample", file.metadata)
        
        # Validate metadata values
        self.assertEqual(file.metadata["row_count"], 5)  # 5 data rows
        self.assertEqual(file.metadata["column_count"], 5)  # 5 columns
        self.assertEqual(len(file.metadata["columns"]), 5)
        self.assertIn("Name", file.metadata["columns"])
        
        # Validate sample data
        self.assertIsInstance(file.metadata["sample"], list)
        self.assertTrue(len(file.metadata["sample"]) > 0)

    def test_save_document(self):
        """Test saving a CSV document."""
        # First load the document
        file = self.repository.load_document(self.sample_csv_path)
        
        # Make some changes to the content
        original_content = file.content
        new_content = file.content + "\nNewPerson,25,Austin,Student,0"
        file.update_content(new_content)
        
        # Save the document
        result = self.repository.save_document(file)
        
        # Validate the result
        self.assertTrue(result)
        
        # Validate that the file is in the repository
        saved_file = self.repository.get_document(file.id)
        self.assertEqual(saved_file.content, new_content)
        
        # Restore original content for other tests
        file.update_content(original_content)

    def test_get_document(self):
        """Test retrieving a document by ID."""
        # First load a document
        file = self.repository.load_document(self.sample_csv_path)
        
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
        file = self.repository.load_document(self.sample_csv_path)
        
        # Check that the document is in the list
        documents = self.repository.list_documents()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].id, file.id)

    def test_delete_document(self):
        """Test deleting a document."""
        # First load a document
        file = self.repository.load_document(self.sample_csv_path)
        
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
        # Create a temporary text file (not a valid CSV)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
            temp.write(b"This is not a CSV file")
            temp_path = temp.name
        
        # Attempt to load the text file as a CSV
        with self.assertRaises(ValueError):
            self.repository.load_document(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
    def test_get_table_data(self):
        """Test getting structured table data."""
        # First load a document
        file = self.repository.load_document(self.sample_csv_path)
        
        # Get the table data
        table_data = self.repository.get_table_data(file.id)
        
        # Validate the data
        self.assertIsInstance(table_data, list)
        self.assertEqual(len(table_data), 5)  # 5 rows
        self.assertIsInstance(table_data[0], dict)
        self.assertIn("Name", table_data[0])
        self.assertIn("Age", table_data[0])
        self.assertIn("City", table_data[0])
        
        # Test with non-existent file ID
        with self.assertRaises(ValueError):
            self.repository.get_table_data("non-existent-id")
        
        # Test with wrong file type
        # Create a fake non-CSV document in the repository
        fake_file = File(
            id="fake-id",
            name="fake.txt",
            path="/path/to/fake.txt",
            content="Not a CSV",
            file_type="text"
        )
        self.repository.documents["fake-id"] = fake_file
        
        with self.assertRaises(ValueError):
            self.repository.get_table_data("fake-id") 
