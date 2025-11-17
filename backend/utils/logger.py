import logging
import sys
from datetime import datetime
from typing import Optional

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

def log_failed_login(ip: str, user_agent: Optional[str] = None):
    """Log a failed login attempt."""
    user_agent_str = user_agent or "Unknown"
    security_logger.warning(
        f"Failed login attempt - IP: {ip}, User-Agent: {user_agent_str}"
    )

def log_successful_login(ip: str, user_agent: Optional[str] = None):
    """Log a successful login."""
    user_agent_str = user_agent or "Unknown"
    security_logger.info(
        f"Successful login - IP: {ip}, User-Agent: {user_agent_str}"
    )

def log_rate_limit_violation(ip: str, endpoint: str, user_agent: Optional[str] = None):
    """Log a rate limit violation."""
    user_agent_str = user_agent or "Unknown"
    security_logger.warning(
        f"Rate limit exceeded - IP: {ip}, Endpoint: {endpoint}, User-Agent: {user_agent_str}"
    )

def log_suspicious_activity(ip: str, activity: str, user_agent: Optional[str] = None):
    """Log suspicious activity."""
    user_agent_str = user_agent or "Unknown"
    security_logger.warning(
        f"Suspicious activity - IP: {ip}, Activity: {activity}, User-Agent: {user_agent_str}"
    )

def log_file_upload(ip: str, filename: str, size: int, success: bool):
    """Log file upload attempt."""
    status = "success" if success else "failed"
    security_logger.info(
        f"File upload {status} - IP: {ip}, Filename: {filename}, Size: {size} bytes"
    )

