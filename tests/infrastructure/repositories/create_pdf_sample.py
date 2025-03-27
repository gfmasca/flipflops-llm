"""
Script to generate a sample PDF file for testing.
"""
import os
from fpdf import FPDF

def create_sample_pdf(output_path):
    """Create a sample PDF file."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Sample PDF Document')
    pdf.ln(20)
    
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, 'This is a sample PDF document created for testing purposes. '
                         'It contains some text content that will be extracted by the '
                         'PDFDocumentRepository.')
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, 'PDF documents can contain various elements such as text, '
                         'images, tables, and more. This simple example only includes text.')
    
    # Create a simple table
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Sample Table', 0, 1, 'C')
    pdf.ln(5)
    
    # Table headers
    pdf.set_font('Arial', 'B', 12)
    col_width = 40
    pdf.cell(col_width, 10, 'Name', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Age', 1, 0, 'C')
    pdf.cell(col_width, 10, 'City', 1, 1, 'C')
    
    # Table data
    pdf.set_font('Arial', '', 12)
    table_data = [
        ['John Doe', '32', 'New York'],
        ['Jane Smith', '28', 'San Francisco'],
        ['Bob Johnson', '45', 'Chicago']
    ]
    
    for row in table_data:
        pdf.cell(col_width, 10, row[0], 1, 0, 'L')
        pdf.cell(col_width, 10, row[1], 1, 0, 'C')
        pdf.cell(col_width, 10, row[2], 1, 1, 'L')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the PDF
    pdf.output(output_path)
    print(f"Sample PDF created at: {output_path}")

if __name__ == "__main__":
    create_sample_pdf("./tests/infrastructure/repositories/test_files/sample.pdf") 
