from dataclasses import dataclass


@dataclass(frozen=True)
class QueryText:
    """User query text with validation (2-2000 chars)."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Query text must be at least 2 characters")
        if len(self.value) > 2000:
            raise ValueError("Query text must not exceed 2000 characters")

    def __str__(self) -> str:
        return self.value
