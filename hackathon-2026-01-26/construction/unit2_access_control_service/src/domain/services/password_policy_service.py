"""Password Policy Service - Enforces password security requirements."""
from ..value_objects import Password


class PasswordPolicyService:
    """Domain service for password policy enforcement."""
    
    def __init__(self, password_hasher):
        """
        Initialize PasswordPolicyService.
        
        Args:
            password_hasher: Infrastructure password hasher
        """
        self._password_hasher = password_hasher
    
    def validate_password(self, plain_password: str) -> tuple[bool, str]:
        """
        Validate password meets requirements.
        
        Args:
            plain_password: Plain text password
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            Password.validate_plain_password(plain_password)
            return True, ""
        except ValueError as e:
            return False, str(e)
    
    def hash_password(self, plain_password: str) -> Password:
        """
        Hash a plain password.
        
        Args:
            plain_password: Plain text password
            
        Returns:
            Password value object with hashed value
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        # Validate first
        Password.validate_plain_password(plain_password)
        
        # Hash the password
        hashed = self._password_hasher.hash(plain_password)
        
        return Password(hashed)
    
    def verify_password(self, plain_password: str, hashed_password: Password) -> bool:
        """
        Verify a plain password against hashed password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches
        """
        return self._password_hasher.verify(plain_password, hashed_password.hashed_value)
