from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
import json
import asyncio
from services.embeddings import embed_query
from db.vector_store import LocalFaissStore
from services.qa import answer_with_context, answer_with_context_stream
from routers.rate_limit import get_client_identifier, rate_limiter
from utils.logger import log_rate_limit_violation

router = APIRouter(tags=["qa"])

MAX_QUESTION_LENGTH = 2000  # Maximum question length
REQUEST_TIMEOUT = 30  # Timeout for AI operations in seconds

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_LENGTH)
    use_web_search: bool = False
    top_k: int = Field(default=3, ge=1, le=10)
    stream: bool = False
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        if len(v) > MAX_QUESTION_LENGTH:
            raise ValueError(f'Question exceeds maximum length of {MAX_QUESTION_LENGTH} characters')
        return v.strip()

@router.post("/{doc_id}")
async def ask(doc_id: str, request: AskRequest, req: Request):
    client_ip = get_client_identifier(req).split(':')[0]  # Extract IP for logging
    user_agent = req.headers.get("user-agent", "Unknown")
    
    # Rate limiting: 20 requests per minute per IP
    identifier = get_client_identifier(req)
    is_allowed, remaining, reset_after = rate_limiter.is_allowed(identifier, max_requests=20, window_seconds=60)
    if not is_allowed:
        log_rate_limit_violation(client_ip, f"/api/{doc_id}", user_agent)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum 20 requests per minute. Try again in {reset_after} seconds.",
            headers={
                "X-RateLimit-Limit": "20",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_after)
            }
        )
    store = LocalFaissStore(doc_id)
    if not store.chunks or store.index is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    try:
        # Add timeout protection for AI operations
        q = await asyncio.wait_for(
            asyncio.to_thread(embed_query, request.question),
            timeout=REQUEST_TIMEOUT
        )
        hits = await asyncio.wait_for(
            asyncio.to_thread(store.search, q, request.top_k),
            timeout=REQUEST_TIMEOUT
        )
        contexts = [h[2] for h in hits]
        page_numbers_list = [h[3] if len(h) > 3 else [] for h in hits]
        
        # Determine if web search was used
        web_results = []
        if request.use_web_search:
            from services.web_search import search_web
            web_results = await asyncio.wait_for(
                asyncio.to_thread(search_web, request.question, 5),
                timeout=10  # Shorter timeout for web search
            )
        
        # Stream response if requested
        if request.stream:
            def generate():
                # Send initial metadata with page numbers
                contexts_with_pages = [
                    {"text": contexts[i], "page_numbers": page_numbers_list[i] if i < len(page_numbers_list) else []}
                    for i in range(len(contexts))
                ]
                yield f"data: {json.dumps({'type': 'start', 'sources': {'document': len(contexts) > 0, 'web': request.use_web_search and len(web_results) > 0}, 'contexts': contexts_with_pages})}\n\n"
                
                # Stream answer chunks
                try:
                    for chunk in answer_with_context_stream(request.question, contexts, use_web_search=request.use_web_search):
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while generating the answer.'})}\n\n"
                
                # Send end signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        # Non-streaming response with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(answer_with_context, request.question, contexts, request.use_web_search),
            timeout=REQUEST_TIMEOUT
        )
        
        # Return snippets with scores and page numbers for transparency
        return {
            "doc_id": doc_id,
            "answer": result["answer"],
            "sources": result["sources"],
            "contexts": [
                {
                    "rank": i+1, 
                    "score": s, 
                    "text": t,
                    "page_numbers": page_numbers_list[i] if i < len(page_numbers_list) else []
                } 
                for i, (_, s, t) in enumerate(hits)
            ]
        }
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request timeout. The operation took too long. Please try again with a simpler question."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again later."
        )
