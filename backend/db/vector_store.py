import os
import json
import faiss
import numpy as np
from typing import List, Dict, Tuple
from utils.config import VECTOR_DIR

os.makedirs(VECTOR_DIR, exist_ok=True)

class LocalFaissStore:
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.index_path = os.path.join(VECTOR_DIR, f"{doc_id}.faiss")
        self.meta_path = os.path.join(VECTOR_DIR, f"{doc_id}.meta.json")
        self.index = None
        self.chunks: List[str] = []
        self.chunk_metadata: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r") as f:
                meta = json.load(f)
                self.chunks = meta.get("chunks", [])
                self.chunk_metadata = meta.get("chunk_metadata", [])
                dim = meta.get("dim", 1536)
                if os.path.exists(self.index_path):
                    self.index = faiss.read_index(self.index_path)
                else:
                    self.index = faiss.IndexFlatIP(dim)
        else:
            # lazy init; dimension created on first add
            pass

    def _save(self, dim: int, metadata: dict = None):
        meta = {
            "doc_id": self.doc_id, 
            "dim": dim, 
            "chunks": self.chunks,
            "chunk_metadata": self.chunk_metadata
        }
        if metadata:
            meta.update(metadata)
        with open(self.meta_path, "w") as f:
            json.dump(meta, f)
        faiss.write_index(self.index, self.index_path)

    def add(self, chunk_texts: list[str], embeddings: np.ndarray, chunk_metadata: List[Dict] = None, metadata: dict = None):
        emb = np.asarray(embeddings, dtype="float32")
        faiss.normalize_L2(emb)

        if self.index is None:
            self.index = faiss.IndexFlatIP(emb.shape[1])

        self.index.add(emb)  # type: ignore
        self.chunks.extend(chunk_texts)
        if chunk_metadata:
            self.chunk_metadata.extend(chunk_metadata)
        else:
            # Create empty metadata for chunks without page info
            self.chunk_metadata.extend([{}] * len(chunk_texts))
        self._save(emb.shape[1], metadata)

    def search(self, query_embedding: np.ndarray, top_k: int = 3):
        if self.index is None:
            raise RuntimeError("Vector index not initialized.")

        q = np.asarray(query_embedding, dtype="float32")
        q = np.expand_dims(q, axis=0)
        faiss.normalize_L2(q)

        distances, indices = self.index.search(q, top_k)  # type: ignore

        out = []
        for idx, score in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            chunk_idx = int(idx)
            chunk_meta = self.chunk_metadata[chunk_idx] if chunk_idx < len(self.chunk_metadata) else {}
            page_numbers = chunk_meta.get("page_numbers", [])
            out.append((
                chunk_idx, 
                float(score), 
                self.chunks[chunk_idx],
                page_numbers
            ))
        return out
