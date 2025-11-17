import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
VECTOR_DIR = os.getenv("VECTOR_DIR", "./data/vector_store")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Authentication configuration
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:3001"
).split(",")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

# Warn if password is not set (but don't fail, for development)
if not AUTH_PASSWORD and not AUTH_PASSWORD_HASH:
    import warnings
    warnings.warn("AUTH_PASSWORD or AUTH_PASSWORD_HASH not set. Authentication may not work.")
