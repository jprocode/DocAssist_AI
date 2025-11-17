from typing import List
import numpy as np
import tiktoken
from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

# Maximum tokens per batch (safely under OpenAI's 300k limit)
MAX_TOKENS_PER_BATCH = 250000

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed texts with automatic batching to handle large documents.
    Batches chunks to stay under OpenAI's token limit.
    """
    if not texts:
        return np.array([], dtype="float32")
    
    # Use tiktoken to count tokens accurately
    enc = tiktoken.get_encoding("cl100k_base")
    
    # Batch texts to stay under token limit
    batches = []
    current_batch = []
    current_tokens = 0
    
    for text in texts:
        text_tokens = len(enc.encode(text))
        
        # If adding this text would exceed the limit, start a new batch
        if current_tokens + text_tokens > MAX_TOKENS_PER_BATCH and current_batch:
            batches.append(current_batch)
            current_batch = [text]
            current_tokens = text_tokens
        else:
            current_batch.append(text)
            current_tokens += text_tokens
    
    # Add the last batch if it has items
    if current_batch:
        batches.append(current_batch)
    
    # Process each batch and combine results
    all_embeddings = []
    for batch in batches:
        resp = _client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=batch)
        batch_embeddings = [d.embedding for d in resp.data]
        all_embeddings.extend(batch_embeddings)
    
    return np.array(all_embeddings, dtype="float32")

def embed_query(text: str) -> np.ndarray:
    resp = _client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=[text])
    return np.array(resp.data[0].embedding, dtype="float32")
