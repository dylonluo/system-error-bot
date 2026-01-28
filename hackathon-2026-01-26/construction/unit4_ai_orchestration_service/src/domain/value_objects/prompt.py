from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Prompt:
    """Prompt structure for AI provider."""
    system_prompt: str
    user_prompt: str
    context: List[str]
    temperature: float = 0.3
    max_tokens: int = 500
    image_url: Optional[str] = None  # URL of attached screenshot for vision analysis
    image_base64: Optional[str] = None  # Base64 encoded image data
    image_media_type: Optional[str] = None  # e.g., "image/png", "image/jpeg"

    def to_full_prompt(self) -> str:
        """Combine all parts into a single prompt string."""
        parts = [f"System: {self.system_prompt}"]
        if self.context:
            parts.append("Context:\n" + "\n".join(self.context))
        parts.append(f"User: {self.user_prompt}")
        if self.image_url:
            parts.append(f"[Screenshot attached: {self.image_url}]")
        return "\n\n".join(parts)
    
    def has_image(self) -> bool:
        """Check if prompt has an image attached."""
        return bool(self.image_base64 or self.image_url)
