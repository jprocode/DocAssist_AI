import uuid
import os
import re
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from services.pdf_parser import extract_pdf_text
from utils.chunker import chunk_text
from services.embeddings import embed_texts
from db.vector_store import LocalFaissStore
from routers.rate_limit import get_client_identifier, rate_limiter
from utils.logger import log_file_upload, log_rate_limit_violation

router = APIRouter(tags=["upload"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILENAME_LENGTH = 255

def validate_pdf_signature(file_bytes: bytes) -> bool:
    """Validate PDF file signature (magic bytes)"""
    # PDF files start with %PDF- followed by version number
    if len(file_bytes) < 4:
        return False
    return file_bytes[:4] == b'%PDF'

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks"""
    if not filename:
        return "untitled.pdf"
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove path traversal characters
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Limit length
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        max_name_length = MAX_FILENAME_LENGTH - len(ext)
        filename = name[:max_name_length] + ext
    
    # Ensure it ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename

@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    client_ip = get_client_identifier(request).split(':')[0]  # Extract IP for logging
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Rate limiting: 5 uploads per hour per IP
    identifier = get_client_identifier(request)
    is_allowed, remaining, reset_after = rate_limiter.is_allowed(identifier, max_requests=5, window_seconds=3600)
    if not is_allowed:
        log_rate_limit_violation(client_ip, "/api/upload", user_agent)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum 5 uploads per hour. Try again in {reset_after} seconds.",
            headers={
                "X-RateLimit-Limit": "5",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_after)
            }
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
    
    # Validate PDF signature (magic bytes)
    if not validate_pdf_signature(file_bytes):
        log_file_upload(client_ip, file.filename or "unknown", len(file_bytes), False)
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file. File signature does not match PDF format."
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename or "untitled.pdf")
    
    # Extract text from PDF with timeout protection
    try:
        text, pages, page_mapping = extract_pdf_text(file_bytes)
    except Exception as e:
        log_file_upload(client_ip, safe_filename, len(file_bytes), False)
        raise HTTPException(
            status_code=400,
            detail="Failed to extract text from PDF. The file may be corrupted or encrypted."
        )
    
    if not text.strip():
        log_file_upload(client_ip, safe_filename, len(file_bytes), False)
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
            "filename": safe_filename,
            "upload_date": datetime.utcnow().isoformat(),
            "pages": pages
        }
        store.add(chunks, vectors, chunk_metadata, metadata)
        
        log_file_upload(client_ip, safe_filename, len(file_bytes), True)

        return {
            "doc_id": doc_id, 
            "pages": pages, 
            "chunks": len(chunks), 
            "filename": safe_filename
        }
    except Exception as e:
        log_file_upload(client_ip, safe_filename, len(file_bytes), False)
        # Log the actual error for debugging
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"[ERROR] Upload failed: {error_msg}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        
        # In development, show the actual error; in production, show generic message
        is_dev = os.getenv("ENVIRONMENT", "development") == "development"
        detail_msg = f"Failed to process document: {error_msg}" if is_dev else "Failed to process document. Please try again later."
        
        raise HTTPException(
            status_code=500,
            detail=detail_msg
        )
