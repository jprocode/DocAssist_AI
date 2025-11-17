from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from services.embeddings import embed_query
from db.vector_store import LocalFaissStore
from services.qa import answer_with_context, answer_with_context_stream
from routers.rate_limit import get_client_identifier, rate_limiter

router = APIRouter(tags=["qa"])

class AskRequest(BaseModel):
    question: str
    use_web_search: bool = False
    top_k: int = 3
    stream: bool = False

@router.post("/{doc_id}")
async def ask(doc_id: str, request: AskRequest, req: Request):
    # Rate limiting: 20 requests per minute per IP
    identifier = get_client_identifier(req)
    if not rate_limiter.is_allowed(identifier, max_requests=20, window_seconds=60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 20 requests per minute."
        )
    store = LocalFaissStore(doc_id)
    if not store.chunks or store.index is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    q = embed_query(request.question)
    hits = store.search(q, top_k=request.top_k)
    contexts = [h[2] for h in hits]
    page_numbers_list = [h[3] if len(h) > 3 else [] for h in hits]
    
    # Determine if web search was used
    web_results = []
    if request.use_web_search:
        from services.web_search import search_web
        web_results = search_web(request.question, max_results=5)
    
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
            for chunk in answer_with_context_stream(request.question, contexts, use_web_search=request.use_web_search):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Send end signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    # Non-streaming response
    result = answer_with_context(request.question, contexts, use_web_search=request.use_web_search)
    
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
