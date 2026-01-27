"""DocumentFormat value object."""

from enum import Enum


class DocFormat(str, Enum):
    """Document format enumeration."""

    WEBPAGE = "webpage"
    PDF = "pdf"
    MARKDOWN = "markdown"


class DocumentFormat:
    """Document format specification."""

    def __init__(self, value: DocFormat):
        if not isinstance(value, DocFormat):
            raise ValueError(f"Invalid document format: {value}")
        self._value = value

    @property
    def value(self) -> DocFormat:
        return self._value

    def is_webpage(self) -> bool:
        return self._value == DocFormat.WEBPAGE

    def is_pdf(self) -> bool:
        return self._value == DocFormat.PDF

    def is_markdown(self) -> bool:
        return self._value == DocFormat.MARKDOWN

    def get_mime_type(self) -> str:
        """Get MIME type for the format."""
        mime_types = {DocFormat.WEBPAGE: "text/html", DocFormat.PDF: "application/pdf", DocFormat.MARKDOWN: "text/markdown"}
        return mime_types[self._value]

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentFormat):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value.value

    def __repr__(self) -> str:
        return f"DocumentFormat({self._value.value})"
