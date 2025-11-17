from fastapi import Request, HTTPException
from functools import lru_cache
from collections import defaultdict
from datetime import datetime, timedelta
import time
import hashlib
from utils.logger import log_rate_limit_violation

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

    def is_allowed(self, identifier: str, max_requests: int, window_seconds: int) -> tuple:
        """
        Check if request is allowed
        
        Returns:
            (is_allowed, remaining_requests, reset_after_seconds)
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Filter out old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[identifier])
        if request_count >= max_requests:
            # Calculate reset time
            oldest_request = min(self.requests[identifier]) if self.requests[identifier] else current_time
            reset_after = int(window_seconds - (current_time - oldest_request))
            return False, 0, reset_after
        
        # Add current request
        self.requests[identifier].append(current_time)
        remaining = max_requests - request_count - 1
        reset_after = window_seconds
        return True, remaining, reset_after

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_identifier(request: Request) -> str:
    """
    Get a unique identifier for the client using multiple factors
    Combines IP, User-Agent, and other headers for better identification
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    
    # Create a combined identifier hash for better tracking
    # In production, consider using Redis with IP + fingerprint
    combined = f"{client_ip}:{user_agent}"
    identifier_hash = hashlib.md5(combined.encode()).hexdigest()
    
    # Return IP for logging, but use hash for rate limiting
    return f"{client_ip}:{identifier_hash[:8]}"

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

