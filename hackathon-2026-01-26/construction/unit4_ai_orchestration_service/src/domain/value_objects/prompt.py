from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Prompt:
    """Prompt structure for AI provider."""
    system_prompt: str
    user_prompt: str
    context: List[str]
    temperature: float = 0.3
    max_tokens: int = 500

    def to_full_prompt(self) -> str:
        """Combine all parts into a single prompt string."""
        parts = [f"System: {self.system_prompt}"]
        if self.context:
            parts.append("Context:\n" + "\n".join(self.context))
        parts.append(f"User: {self.user_prompt}")
        return "\n\n".join(parts)
