from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AIResponse:
    """Response from AI provider."""
    content: str
    raw_response: str
    tokens_used: int
    model: str
    generated_at: datetime

    @classmethod
    def create(cls, content: str, model: str, tokens_used: int = 0) -> "AIResponse":
        return cls(
            content=content,
            raw_response=content,
            tokens_used=tokens_used,
            model=model,
            generated_at=datetime.utcnow(),
        )
