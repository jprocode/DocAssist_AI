from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from routers import upload, summarize, ask, documents
from utils.config import ENVIRONMENT, ALLOWED_ORIGINS
import time

app = FastAPI(title="AI Document Assistant")

# CORS configuration - tighter for production
if ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
else:
    # Development: allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Request size limiting middleware
MAX_REQUEST_SIZE = 50 * 1024 * 1024  # 50MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large. Maximum size is {MAX_REQUEST_SIZE / (1024 * 1024):.0f}MB."}
            )
    
    response = await call_next(request)
    return response

app.include_router(upload.router, prefix="/api")
app.include_router(summarize.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/health")
def health():
    """Health check endpoint with rate limiting consideration."""
    # Note: Health checks should be rate limited in production
    return {"status": "ok", "timestamp": time.time()}
