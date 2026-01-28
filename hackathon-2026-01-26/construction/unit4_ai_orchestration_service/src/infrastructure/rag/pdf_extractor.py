"""PDF text extraction service using PyPDF2."""

import io
import re
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ExtractedPage:
    """Represents extracted content from a PDF page."""
    page_number: int
    text: str
    

class PDFExtractor:
    """Extracts text content from PDF files."""

    def __init__(self):
        self._pypdf2_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if PyPDF2 is available."""
        try:
            import pypdf
            self._pypdf2_available = True
            print("[PDF Extractor] pypdf library available")
        except ImportError:
            try:
                import PyPDF2
                self._pypdf2_available = True
                print("[PDF Extractor] PyPDF2 library available")
            except ImportError:
                print("[PDF Extractor] WARNING: No PDF library found. Install pypdf or PyPDF2.")
                self._pypdf2_available = False

    def extract_from_bytes(self, pdf_bytes: bytes) -> List[ExtractedPage]:
        """Extract text from PDF bytes."""
        if not self._pypdf2_available:
            return []

        try:
            # Try pypdf first (newer)
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                pages = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    text = self._clean_text(text)
                    if text.strip():
                        pages.append(ExtractedPage(page_number=i + 1, text=text))
                return pages
            except ImportError:
                pass

            # Fallback to PyPDF2
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = self._clean_text(text)
                if text.strip():
                    pages.append(ExtractedPage(page_number=i + 1, text=text))
            return pages

        except Exception as e:
            print(f"[PDF Extractor] Error extracting PDF: {e}")
            return []

    def extract_full_text(self, pdf_bytes: bytes) -> str:
        """Extract all text from PDF as single string."""
        pages = self.extract_from_bytes(pdf_bytes)
        return "\n\n".join(page.text for page in pages)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that often appear in PDFs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()

    def is_available(self) -> bool:
        """Check if PDF extraction is available."""
        return self._pypdf2_available
