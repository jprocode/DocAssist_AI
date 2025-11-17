import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from services.pdf_parser import extract_pdf_text
from utils.chunker import chunk_text
from services.embeddings import embed_texts
from db.vector_store import LocalFaissStore
from routers.rate_limit import get_client_identifier, rate_limiter

router = APIRouter(tags=["upload"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/upload")
async def upload(file: UploadFile = File(...), req: Request = None):
    # Rate limiting: 5 uploads per hour per IP
    identifier = get_client_identifier(req) if req else "unknown"
    if not rate_limiter.is_allowed(identifier, max_requests=5, window_seconds=3600):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 5 uploads per hour."
        )
    # Validate file type
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported. Please upload a valid PDF file."
        )
    
    # Read and validate file size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024):.0f}MB."
        )
    
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    # Extract text from PDF
    try:
        text, pages, page_mapping = extract_pdf_text(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )
    
    if not text.strip():
        raise HTTPException(
            status_code=400, 
            detail="No extractable text found in PDF. The PDF may be image-based or corrupted."
        )

    # Process document
    try:
        doc_id = str(uuid.uuid4())
        chunks, chunk_metadata = chunk_text(text, max_tokens=500, page_mapping=page_mapping)
        vectors = embed_texts(chunks)

        store = LocalFaissStore(doc_id)
        metadata = {
            "filename": file.filename or "untitled.pdf",
            "upload_date": datetime.utcnow().isoformat(),
            "pages": pages
        }
        store.add(chunks, vectors, chunk_metadata, metadata)

        return {
            "doc_id": doc_id, 
            "pages": pages, 
            "chunks": len(chunks), 
            "filename": file.filename or "untitled.pdf"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )
