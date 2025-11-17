from fastapi import APIRouter, HTTPException
from db.vector_store import LocalFaissStore
from services.summarizer import summarize_text

router = APIRouter(tags=["summarize"])

@router.post("/summarize")
def summarize(doc_id: str):
    store = LocalFaissStore(doc_id)
    if not store.chunks:
        raise HTTPException(status_code=404, detail="Document not found.")
    # Join a reasonable amount of text for summary
    joined = "\n".join(store.chunks[:20])
    summary = summarize_text(joined, max_words=220)
    return {"doc_id": doc_id, "summary": summary}
