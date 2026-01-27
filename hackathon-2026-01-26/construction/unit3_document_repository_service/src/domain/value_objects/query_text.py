"""QueryText value object."""


class QueryText:
    """Search query text with validation."""

    def __init__(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ValueError("Query text must be at least 2 characters")
        self._value = value.strip()

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if not isinstance(other, QueryText):
            return False
        return self._value.lower() == other._value.lower()

    def __hash__(self) -> int:
        return hash(self._value.lower())

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"QueryText({self._value})"
