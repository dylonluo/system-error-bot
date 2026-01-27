"""Authentication Service - Handles authentication logic and security."""
from dataclasses import dataclass
from typing import Optional

from ..aggregates import User, Session
from ..value_objects import Username, SessionId, JWTToken
from ..repositories import IUserRepository


@dataclass
class AuthenticationResult:
    """Result of authentication attempt."""
    success: bool
    user: Optional[User] = None
    session: Optional[Session] = None
    error_message: str = ""


class AuthenticationService:
    """Domain service for authentication logic."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher,
        jwt_provider,
        rate_limiter
    ):
        """
        Initialize AuthenticationService.
        
        Args:
            user_repository: User repository
            password_hasher: Password hasher
            jwt_provider: JWT token provider
            rate_limiter: Rate limiter for brute force prevention
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._jwt_provider = jwt_provider
        self._rate_limiter = rate_limiter
    
    def authenticate(
        self,
        username: Username,
        plain_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuthenticationResult:
        """
        Authenticate a user.
        
        Args:
            username: Username
            plain_password: Plain text password
            ip_address: IP address of request
            user_agent: User agent string
            
        Returns:
            AuthenticationResult with success status and user/session if successful
        """
        # Check rate limit
        if not self._rate_limiter.check_limit(str(username)):
            return AuthenticationResult(
                success=False,
                error_message="Too many failed login attempts. Please try again later."
            )
        
        # Find user
        user = self._user_repository.find_by_username(username)
        if user is None:
            self._rate_limiter.record_attempt(str(username))
            return AuthenticationResult(
                success=False,
                error_message="Invalid credentials"
            )
        
        # Check if user is active
        if not user.is_active:
            return AuthenticationResult(
                success=False,
                error_message="User account is not active"
            )
        
        # Verify password
        try:
            if not user.authenticate(self._password_hasher, plain_password):
                self._rate_limiter.record_attempt(str(username))
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid credentials"
                )
        except ValueError as e:
            return AuthenticationResult(
                success=False,
                error_message=str(e)
            )
        
        # Create session with JWT tokens
        session = self._create_session(user, ip_address, user_agent)
        
        # Reset rate limiter on successful login
        self._rate_limiter.reset_attempts(str(username))
        
        # Update last login
        user.update_last_login()
        self._user_repository.save(user)
        
        return AuthenticationResult(
            success=True,
            user=user,
            session=session
        )
    
    def _create_session(
        self,
        user: User,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> Session:
        """
        Create a new session for user.
        
        Args:
            user: User to create session for
            ip_address: IP address
            user_agent: User agent
            
        Returns:
            New session
        """
        # Generate tokens
        access_token_str = self._jwt_provider.generate_access_token(user)
        refresh_token_str = self._jwt_provider.generate_refresh_token(user)
        
        # Create token value objects
        access_token = JWTToken.create(
            access_token_str,
            self._jwt_provider.access_token_expiry_seconds
        )
        refresh_token = JWTToken.create(
            refresh_token_str,
            self._jwt_provider.refresh_token_expiry_seconds
        )
        
        # Create session
        session = Session(
            session_id=SessionId.generate(),
            user_id=user.user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return session
    
    def validate_token(self, token: str) -> tuple[bool, Optional[dict]]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (is_valid, payload)
        """
        return self._jwt_provider.validate_token(token)
