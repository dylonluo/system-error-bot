"""Rate Limiter - In-memory rate limiting for brute force prevention."""
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AttemptRecord:
    """Record of a failed attempt."""
    timestamp: datetime


class RateLimiter:
    """In-memory rate limiter for failed login attempts."""
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        """
        Initialize RateLimiter.
        
        Args:
            max_attempts: Maximum failed attempts allowed
            window_minutes: Time window in minutes
        """
        self._max_attempts = max_attempts
        self._window_minutes = window_minutes
        self._attempts: Dict[str, List[AttemptRecord]] = {}
    
    def check_limit(self, identifier: str) -> bool:
        """
        Check if identifier has exceeded rate limit.
        
        Args:
            identifier: Identifier to check (e.g., username)
            
        Returns:
            True if within limit, False if exceeded
        """
        self._cleanup_old_attempts(identifier)
        
        if identifier not in self._attempts:
            return True
        
        return len(self._attempts[identifier]) < self._max_attempts
    
    def record_attempt(self, identifier: str) -> None:
        """
        Record a failed attempt.
        
        Args:
            identifier: Identifier to record (e.g., username)
        """
        if identifier not in self._attempts:
            self._attempts[identifier] = []
        
        self._attempts[identifier].append(AttemptRecord(datetime.utcnow()))
        self._cleanup_old_attempts(identifier)
    
    def reset_attempts(self, identifier: str) -> None:
        """
        Reset attempts for identifier (e.g., after successful login).
        
        Args:
            identifier: Identifier to reset
        """
        if identifier in self._attempts:
            del self._attempts[identifier]
    
    def _cleanup_old_attempts(self, identifier: str) -> None:
        """
        Remove attempts outside the time window.
        
        Args:
            identifier: Identifier to cleanup
        """
        if identifier not in self._attempts:
            return
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=self._window_minutes)
        self._attempts[identifier] = [
            attempt for attempt in self._attempts[identifier]
            if attempt.timestamp > cutoff_time
        ]
        
        # Remove empty lists
        if not self._attempts[identifier]:
            del self._attempts[identifier]
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining attempts before rate limit.
        
        Args:
            identifier: Identifier to check
            
        Returns:
            Number of remaining attempts
        """
        self._cleanup_old_attempts(identifier)
        
        if identifier not in self._attempts:
            return self._max_attempts
        
        return max(0, self._max_attempts - len(self._attempts[identifier]))
