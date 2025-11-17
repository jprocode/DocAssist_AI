import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.pdf_parser import extract_pdf_text

def test_extract_pdf_text_structure():
    """Test that extract_pdf_text returns correct structure."""
    # Note: This test would require a sample PDF file
    # For now, we test the function signature
    import inspect
    sig = inspect.signature(extract_pdf_text)
    assert len(sig.parameters) == 1
    # Function should return tuple of (text, pages, page_mapping)
    # This is a structural test

