"""DocumentTitle value object."""


class DocumentTitle:
    """Document title with validation."""

    def __init__(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Document title cannot be empty")
        if len(value) > 500:
            raise ValueError("Document title cannot exceed 500 characters")
        self._value = value.strip()

    @property
    def value(self) -> str:
        return self._value

    def truncate(self, length: int) -> str:
        """Truncate title to specified length."""
        if len(self._value) <= length:
            return self._value
        return self._value[: length - 3] + "..."

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentTitle):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"DocumentTitle({self._value})"
