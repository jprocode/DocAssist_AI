from typing import Tuple, List, Dict
import pdfplumber
import io

def extract_pdf_text(file_bytes: bytes) -> Tuple[str, int, List[Dict[str, any]]]:
    """
    Return extracted text, page count, and page mapping.
    Returns: (full_text, page_count, page_mapping)
    page_mapping is a list of dicts with 'start_char', 'end_char', 'page_num'
    """
    pages = 0
    text_parts = []
    page_mapping = []
    current_char = 0
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text:
                start_char = current_char
                end_char = current_char + len(page_text)
                page_mapping.append({
                    'start_char': start_char,
                    'end_char': end_char,
                    'page_num': page_num
                })
                text_parts.append(page_text)
                current_char = end_char + 1  # +1 for newline separator
    
    full_text = "\n".join(text_parts).strip()
    return full_text, pages, page_mapping
