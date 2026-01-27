from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceScore:
    """Confidence score for AI response (0.0-1.0)."""
    value: float

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")

    def should_escalate(self, threshold: float = 0.5) -> bool:
        """Returns True if confidence is below threshold."""
        return self.value < threshold

    def __float__(self) -> float:
        return self.value
