"""
Simple rate limiting using in-memory storage for login attempts.
For production, consider using Redis for distributed rate limiting.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status
from app.core.config import settings


# In-memory storage: IP -> (timestamp, count)
_rate_limit_storage: Dict[str, Tuple[datetime, int]] = {}


def check_rate_limit(request: Request, max_requests: int = 5, window_seconds: int = 60):
    """
    Check if the request should be rate limited.
    
    Args:
        request: FastAPI request object
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Get current time
    now = datetime.utcnow()
    
    # Clean up old entries (older than window)
    cutoff_time = now - timedelta(seconds=window_seconds * 2)
    to_delete = [ip for ip, (timestamp, _) in _rate_limit_storage.items() if timestamp < cutoff_time]
    for ip in to_delete:
        del _rate_limit_storage[ip]
    
    # Check rate limit for this IP
    if client_ip in _rate_limit_storage:
        last_request_time, count = _rate_limit_storage[client_ip]
        time_diff = (now - last_request_time).total_seconds()
        
        if time_diff < window_seconds:
            # Within the window
            if count >= max_requests:
                # Rate limit exceeded
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                    headers={"Retry-After": str(int(window_seconds - time_diff))}
                )
            # Increment counter
            _rate_limit_storage[client_ip] = (last_request_time, count + 1)
        else:
            # Window expired, reset
            _rate_limit_storage[client_ip] = (now, 1)
    else:
        # First request from this IP
        _rate_limit_storage[client_ip] = (now, 1)


def login_rate_limit_dependency(request: Request):
    """
    Dependency function for login rate limiting.
    Can be used with Depends() in FastAPI routes.
    """
    check_rate_limit(request, max_requests=5, window_seconds=60)
