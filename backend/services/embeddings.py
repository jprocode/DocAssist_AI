from typing import List
import numpy as np
from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

def embed_texts(texts: List[str]) -> np.ndarray:
    resp = _client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype="float32")

def embed_query(text: str) -> np.ndarray:
    resp = _client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=[text])
    return np.array(resp.data[0].embedding, dtype="float32")
