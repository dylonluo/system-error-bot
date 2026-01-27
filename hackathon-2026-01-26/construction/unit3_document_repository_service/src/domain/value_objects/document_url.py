"""DocumentUrl value object."""

from urllib.parse import urlparse


class DocumentUrl:
    """Document URL with validation."""

    def __init__(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Document URL cannot be empty")

        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")

        if parsed.scheme not in ["http", "https"]:
            raise ValueError("URL must use HTTP or HTTPS protocol")

        self._value = value.strip()

    @property
    def value(self) -> str:
        return self._value

    def get_domain(self) -> str:
        """Extract domain from URL."""
        parsed = urlparse(self._value)
        return parsed.netloc

    def is_valid(self) -> bool:
        """Check if URL is valid."""
        return True  # Already validated in __init__

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentUrl):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"DocumentUrl({self._value})"
