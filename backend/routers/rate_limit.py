from fastapi import Request, HTTPException
from functools import lru_cache
from collections import defaultdict
from datetime import datetime, timedelta
import time

# Simple in-memory rate limiter
# For production, consider using Redis or a proper rate limiting library
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()

    def _cleanup_old_entries(self):
        """Remove entries older than 1 hour"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 3600  # 1 hour
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > cutoff_time
                ]
                if not self.requests[key]:
                    del self.requests[key]
            self.last_cleanup = current_time

    def is_allowed(self, identifier: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed"""
        self._cleanup_old_entries()
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Filter out old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_identifier(request: Request) -> str:
    """Get a unique identifier for the client"""
    # Use IP address as identifier
    client_ip = request.client.host if request.client else "unknown"
    return client_ip

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting decorator/middleware
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if request:
                identifier = get_client_identifier(request)
                if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

