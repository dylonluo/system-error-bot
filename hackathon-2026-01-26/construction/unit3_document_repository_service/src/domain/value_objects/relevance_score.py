"""RelevanceScore value object."""


class RelevanceScore:
    """Relevance score for search results (0.0-1.0)."""

    def __init__(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Relevance score must be a number")
        if value < 0.0 or value > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        self._value = float(value)

    @property
    def value(self) -> float:
        return self._value

    def is_high_relevance(self) -> bool:
        """Check if score indicates high relevance (>= 0.7)."""
        return self._value >= 0.7

    def is_medium_relevance(self) -> bool:
        """Check if score indicates medium relevance (0.4-0.7)."""
        return 0.4 <= self._value < 0.7

    def is_low_relevance(self) -> bool:
        """Check if score indicates low relevance (< 0.4)."""
        return self._value < 0.4

    def compare_to(self, other: "RelevanceScore") -> int:
        """Compare scores. Returns -1, 0, or 1."""
        if self._value < other._value:
            return -1
        elif self._value > other._value:
            return 1
        return 0

    def __eq__(self, other) -> bool:
        if not isinstance(other, RelevanceScore):
            return False
        return abs(self._value - other._value) < 0.001

    def __lt__(self, other) -> bool:
        if not isinstance(other, RelevanceScore):
            return NotImplemented
        return self._value < other._value

    def __hash__(self) -> int:
        return hash(round(self._value, 3))

    def __str__(self) -> str:
        return f"{self._value:.2f}"

    def __repr__(self) -> str:
        return f"RelevanceScore({self._value})"
