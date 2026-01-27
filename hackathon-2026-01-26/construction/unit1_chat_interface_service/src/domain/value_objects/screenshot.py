"""Screenshot value object"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Screenshot:
    """Metadata reference to uploaded screenshot"""
    filename: str
    storage_url: str
    mime_type: str
    size: int
    uploaded_at: datetime

    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

    def is_valid_format(self) -> bool:
        """Check if MIME type is valid"""
        return self.mime_type in self.ALLOWED_MIME_TYPES

    def is_within_size_limit(self) -> bool:
        """Check if size is within limit"""
        return self.size <= self.MAX_SIZE

    def get_storage_url(self) -> str:
        """Get storage URL"""
        return self.storage_url

    def __post_init__(self):
        """Validate screenshot on creation"""
        if not self.filename:
            raise ValueError("Filename cannot be empty")
        if not self.is_valid_format():
            raise ValueError(f"Invalid MIME type: {self.mime_type}")
        if not self.is_within_size_limit():
            raise ValueError(f"Screenshot size {self.size} exceeds limit {self.MAX_SIZE}")
