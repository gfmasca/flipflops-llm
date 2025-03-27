"""
Repository implementation for CSV documents.
"""
import os
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

from src.entities.file import File
from src.infrastructure.repositories.base_document_repository import BaseDocumentRepository


class CSVDocumentRepository(BaseDocumentRepository):
    """Repository for handling CSV documents."""

    def load_document(self, path: str) -> File:
        """
        Load a CSV document from the given path and create a File entity.
        
        Args:
            path: Path to the CSV file
            
        Returns:
            File entity with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ValueError: If the file is not a valid CSV
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        mime_type = self._get_mime_type(path)
        if not (mime_type.startswith('text/csv') or 
                mime_type.startswith('text/plain')):
            ext = os.path.splitext(path)[1].lower()
            if ext != '.csv':
                raise ValueError(
                    f"Not a CSV file: {path} (MIME: {mime_type}, ext: {ext})"
                )
        
        try:
            # Use pandas to read the CSV for metadata extraction
            df = pd.read_csv(path)
            
            # Read raw content for storage
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            file_id = self._generate_id()
            filename = os.path.basename(path)
            
            metadata = self._extract_metadata_from_csv(df)
            
            file = File(
                id=file_id,
                name=filename,
                path=path,
                content=content,
                file_type="csv",
                uploaded_at=datetime.now(),
                metadata=metadata
            )
            
            self.documents[file_id] = file
            return file
            
        except pd.errors.ParserError as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            raise IOError(f"Error reading CSV file: {str(e)}")

    def save_document(self, file: File) -> bool:
        """
        Save a CSV document to storage.
        
        Args:
            file: File entity to save
            
        Returns:
            True if the document was saved successfully, False otherwise
            
        Raises:
            IOError: If there's an error writing the file
            ValueError: If the file is not a CSV
        """
        if file.file_type != "csv":
            raise ValueError(f"Not a CSV file: {file.name}")
        
        try:
            # Create the storage path
            storage_path = self._get_storage_path(file.name, "csv")
            
            # Write the content to the file
            with open(storage_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
            
            # Update the file path
            file.path = storage_path
            
            # Store the document in memory
            self.documents[file.id] = file
            
            return True
            
        except Exception as e:
            raise IOError(f"Error saving CSV file: {str(e)}")

    def _extract_metadata_from_csv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract metadata from a CSV file.
        
        Args:
            df: Pandas DataFrame object
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Sample data (first 5 rows as a dictionary)
        if len(df) > 0:
            sample_rows = min(5, len(df))
            metadata["sample"] = df.head(sample_rows).to_dict(orient="records")
        
        return metadata
    
    def get_table_data(self, file_id: str) -> List[Dict[str, Any]]:
        """
        Get structured table data from a CSV file.
        
        Args:
            file_id: Document identifier
            
        Returns:
            List of dictionaries representing the CSV data
            
        Raises:
            ValueError: If the file is not found or not a CSV
        """
        file = self.get_document(file_id)
        if not file:
            raise ValueError(f"Document not found: {file_id}")
        
        if file.file_type != "csv":
            raise ValueError(f"Not a CSV file: {file.name}")
        
        try:
            # Use pandas to read the CSV as structured data
            df = pd.read_csv(file.path)
            return df.to_dict(orient="records")
        except Exception as e:
            raise IOError(f"Error reading CSV data: {str(e)}") 
