import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.chunker import chunk_text

def test_chunk_text_basic():
    """Test basic text chunking functionality."""
    text = "This is a test document. " * 100  # Create a long text
    chunks, metadata = chunk_text(text, max_tokens=50)
    
    assert len(chunks) > 0
    assert len(chunks) == len(metadata)
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(isinstance(meta, dict) for meta in metadata)

def test_chunk_text_with_page_mapping():
    """Test chunking with page mapping."""
    text = "Page 1 content. " * 50 + "Page 2 content. " * 50
    page_mapping = [
        {"start_char": 0, "end_char": len("Page 1 content. " * 50), "page_num": 1},
        {"start_char": len("Page 1 content. " * 50) + 1, "end_char": len(text), "page_num": 2}
    ]
    
    chunks, metadata = chunk_text(text, max_tokens=100, page_mapping=page_mapping)
    
    assert len(chunks) > 0
    # Check that metadata contains page numbers
    assert any("page_numbers" in meta for meta in metadata)

def test_chunk_text_empty():
    """Test chunking empty text."""
    chunks, metadata = chunk_text("", max_tokens=50)
    assert len(chunks) == 0
    assert len(metadata) == 0

