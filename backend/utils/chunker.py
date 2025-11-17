from typing import List, Dict, Tuple
import tiktoken

def chunk_text(
    text: str, 
    max_tokens: int = 500, 
    model: str = "gpt-4o-mini",
    page_mapping: List[Dict[str, any]] = None
) -> Tuple[List[str], List[Dict[str, any]]]:
    """
    Chunk text and return chunks with page number metadata.
    Returns: (chunks, chunk_metadata)
    chunk_metadata contains page numbers for each chunk.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    chunk_metadata = []
    start = 0
    
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        
        # Determine which page this chunk belongs to
        chunk_start_char = len(enc.decode(tokens[:start]))
        chunk_end_char = len(enc.decode(tokens[:end]))
        
        page_nums = []
        if page_mapping:
            for page_info in page_mapping:
                if (chunk_start_char <= page_info['end_char'] and 
                    chunk_end_char >= page_info['start_char']):
                    page_nums.append(page_info['page_num'])
        
        chunk_metadata.append({
            'page_numbers': sorted(set(page_nums)) if page_nums else [],
            'start_char': chunk_start_char,
            'end_char': chunk_end_char
        })
        
        start = end
    
    return chunks, chunk_metadata
