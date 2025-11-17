import os
import json
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Request
from utils.config import VECTOR_DIR
from routers.rate_limit import get_client_identifier, rate_limiter
from utils.logger import log_rate_limit_violation

router = APIRouter(tags=["documents"])

def get_document_metadata(doc_id: str) -> Dict:
    """Load document metadata from the meta.json file."""
    meta_path = os.path.join(VECTOR_DIR, f"{doc_id}.meta.json")
    if not os.path.exists(meta_path):
        return None
    
    with open(meta_path, "r") as f:
        return json.load(f)

@router.get("/documents")
def list_documents(request: Request):
    """List all uploaded documents."""
    client_ip = get_client_identifier(request).split(':')[0]
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Rate limiting: 30 requests per minute per IP
    identifier = get_client_identifier(request)
    is_allowed, remaining, reset_after = rate_limiter.is_allowed(identifier, max_requests=30, window_seconds=60)
    if not is_allowed:
        log_rate_limit_violation(client_ip, "/api/documents", user_agent)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum 30 requests per minute. Try again in {reset_after} seconds.",
            headers={
                "X-RateLimit-Limit": "30",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_after)
            }
        )
    
    if not os.path.exists(VECTOR_DIR):
        return {"documents": []}
    
    docs = []
    for filename in os.listdir(VECTOR_DIR):
        if filename.endswith(".meta.json"):
            doc_id = filename.replace(".meta.json", "")
            meta = get_document_metadata(doc_id)
            if meta:
                docs.append({
                    "doc_id": doc_id,
                    "filename": meta.get("filename", "Unknown"),
                    "upload_date": meta.get("upload_date", ""),
                    "pages": meta.get("pages", 0),
                    "chunks": len(meta.get("chunks", [])),
                    "dim": meta.get("dim", 1536)
                })
    
    # Sort by upload date, newest first
    docs.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    return {"documents": docs}

@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """Get document metadata."""
    meta = get_document_metadata(doc_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    return {
        "doc_id": doc_id,
        "filename": meta.get("filename", "Unknown"),
        "upload_date": meta.get("upload_date", ""),
        "pages": meta.get("pages", 0),
        "chunks": len(meta.get("chunks", [])),
        "dim": meta.get("dim", 1536)
    }

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete a document and its associated files."""
    meta_path = os.path.join(VECTOR_DIR, f"{doc_id}.meta.json")
    index_path = os.path.join(VECTOR_DIR, f"{doc_id}.faiss")
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Document not found.")
    
    try:
        if os.path.exists(meta_path):
            os.remove(meta_path)
        if os.path.exists(index_path):
            os.remove(index_path)
        return {"message": "Document deleted successfully", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

