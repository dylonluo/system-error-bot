"""JWT Provider - JWT token generation and validation."""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class JWTProvider:
    """Infrastructure service for JWT token operations."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expiry_seconds: int = 300,  # 5 minutes for demo
        refresh_token_expiry_seconds: int = 3600  # 1 hour for demo
    ):
        """
        Initialize JWTProvider.
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default HS256)
            access_token_expiry_seconds: Access token expiry in seconds
            refresh_token_expiry_seconds: Refresh token expiry in seconds
        """
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expiry_seconds = access_token_expiry_seconds
        self._refresh_token_expiry_seconds = refresh_token_expiry_seconds
    
    @property
    def access_token_expiry_seconds(self) -> int:
        """Get access token expiry in seconds."""
        return self._access_token_expiry_seconds
    
    @property
    def refresh_token_expiry_seconds(self) -> int:
        """Get refresh token expiry in seconds."""
        return self._refresh_token_expiry_seconds
    
    def generate_access_token(self, user) -> str:
        """
        Generate access token for user.
        
        Args:
            user: User aggregate
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self._access_token_expiry_seconds)
        
        payload = {
            'user_id': str(user.user_id),
            'username': str(user.username),
            'role': str(user.role),
            'access_level': str(user.access_level),
            'token_type': 'access',
            'iat': now,
            'exp': expires_at
        }
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def generate_refresh_token(self, user) -> str:
        """
        Generate refresh token for user.
        
        Args:
            user: User aggregate
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self._refresh_token_expiry_seconds)
        
        payload = {
            'user_id': str(user.user_id),
            'token_type': 'refresh',
            'iat': now,
            'exp': expires_at
        }
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def validate_token(self, token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (is_valid, payload)
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm]
            )
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without validation (for inspection).
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None if invalid
        """
        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_signature": False}
            )
        except Exception:
            return None
