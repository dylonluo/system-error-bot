"""DocumentationLink value object"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentationLink:
    """Link to documentation resource"""
    title: str
    url: str
    description: str
    source: str  # s3, confluence
    format: str  # webpage, pdf
    relevance: float  # 0.0-1.0

    def is_accessible(self) -> bool:
        """Check if URL is accessible (basic validation)"""
        return bool(self.url and self.url.startswith(('http://', 'https://')))

    def get_display_text(self) -> str:
        """Get display text for UI"""
        return f"{self.title} ({self.source})"

    def __post_init__(self):
        """Validate documentation link on creation"""
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")
        if not (0.0 <= self.relevance <= 1.0):
            raise ValueError(f"Relevance must be between 0.0 and 1.0, got {self.relevance}")
