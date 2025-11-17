from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, summarize, ask, documents
from utils.config import ENVIRONMENT, ALLOWED_ORIGINS

app = FastAPI(title="AI Document Assistant")

# Middleware to inject Request into upload endpoint
@app.middleware("http")
async def add_request_to_upload(request: Request, call_next):
    # Store request in state for use in upload endpoint
    response = await call_next(request)
    return response

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

app.include_router(upload.router, prefix="/api")
app.include_router(summarize.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
