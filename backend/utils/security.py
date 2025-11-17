import bcrypt
import hashlib
import os
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Password hashing utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def get_password_hash() -> Optional[str]:
    """Get password hash from environment variable."""
    return os.getenv("AUTH_PASSWORD_HASH")

def verify_auth_password(password: str) -> bool:
    """Verify password against stored hash."""
    stored_hash = get_password_hash()
    if not stored_hash:
        # Fallback to plain text for backward compatibility during migration
        expected = os.getenv("AUTH_PASSWORD", "")
        return password == expected
    return verify_password(password, stored_hash)

# Brute force protection
class BruteForceProtection:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.locked_ips = {}
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes in seconds
        self.base_delay = 1  # Base delay in seconds
    
    def record_failed_attempt(self, ip: str):
        """Record a failed login attempt."""
        current_time = datetime.now()
        self.failed_attempts[ip].append(current_time)
        
        # Clean old attempts (older than lockout duration)
        cutoff = current_time - timedelta(seconds=self.lockout_duration)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip]
            if attempt > cutoff
        ]
        
        # Check if IP should be locked
        if len(self.failed_attempts[ip]) >= self.max_attempts:
            self.locked_ips[ip] = current_time + timedelta(seconds=self.lockout_duration)
    
    def record_success(self, ip: str):
        """Record successful login and clear attempts."""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        if ip in self.locked_ips:
            del self.locked_ips[ip]
    
    def is_locked(self, ip: str) -> bool:
        """Check if IP is currently locked."""
        if ip not in self.locked_ips:
            return False
        
        if datetime.now() > self.locked_ips[ip]:
            # Lockout expired
            del self.locked_ips[ip]
            return False
        
        return True
    
    def get_remaining_lockout_time(self, ip: str) -> int:
        """Get remaining lockout time in seconds."""
        if ip not in self.locked_ips:
            return 0
        
        remaining = (self.locked_ips[ip] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def get_delay(self, ip: str) -> float:
        """Get exponential backoff delay based on failed attempts."""
        attempt_count = len(self.failed_attempts.get(ip, []))
        if attempt_count == 0:
            return 0
        
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
        delay = min(self.base_delay * (2 ** (attempt_count - 1)), 16)
        return delay

# Global brute force protection instance
brute_force_protection = BruteForceProtection()

