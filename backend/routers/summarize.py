from fastapi import APIRouter, HTTPException, Request, Query
from db.vector_store import LocalFaissStore
from services.summarizer import summarize_text
from routers.rate_limit import get_client_identifier, rate_limiter
from utils.logger import log_rate_limit_violation

router = APIRouter(tags=["summarize"])

@router.post("/summarize")
async def summarize(
    doc_id: str, 
    request: Request,
    expanded: bool = Query(default=False, description="Generate an expanded, detailed summary")
):
    client_ip = get_client_identifier(request).split(':')[0]  # Extract IP for logging
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Rate limiting: 10 requests per minute per IP
    identifier = get_client_identifier(request)
    is_allowed, remaining, reset_after = rate_limiter.is_allowed(identifier, max_requests=10, window_seconds=60)
    if not is_allowed:
        log_rate_limit_violation(client_ip, "/api/summarize", user_agent)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum 10 requests per minute. Try again in {reset_after} seconds.",
            headers={
                "X-RateLimit-Limit": "10",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_after)
            }
        )
    
    store = LocalFaissStore(doc_id)
    if not store.chunks:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # Use more chunks for expanded summaries
    num_chunks = 50 if expanded else 20
    joined = "\n".join(store.chunks[:num_chunks])
    summary = summarize_text(joined, max_words=220, expanded=expanded)
    return {"doc_id": doc_id, "summary": summary, "expanded": expanded}
