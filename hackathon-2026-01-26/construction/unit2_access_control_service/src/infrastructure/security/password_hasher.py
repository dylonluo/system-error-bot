"""Password Hasher - Bcrypt-based password hashing."""
import bcrypt


class PasswordHasher:
    """Infrastructure service for password hashing using bcrypt."""
    
    def __init__(self, cost_factor: int = 12):
        """
        Initialize PasswordHasher.
        
        Args:
            cost_factor: Bcrypt cost factor (default 12)
        """
        self._cost_factor = cost_factor
    
    def hash(self, plain_password: str) -> str:
        """
        Hash a plain password.
        
        Args:
            plain_password: Plain text password
            
        Returns:
            Bcrypt hashed password string
        """
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self._cost_factor)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against hashed password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password
            
        Returns:
            True if password matches
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
