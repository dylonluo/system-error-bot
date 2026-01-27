"""Request DTOs for Document Repository Service."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchDocumentsRequest(BaseModel):
    """Request DTO for searching documents."""

    query: str = Field(..., min_length=2, description="Search query text")
    sources: Optional[List[str]] = Field(default=None, description="Filter by sources (s3, confluence)")
    document_types: Optional[List[str]] = Field(default=None, description="Filter by document types (sop, prd, guide, other)")
    formats: Optional[List[str]] = Field(default=None, description="Filter by formats (webpage, pdf, markdown)")
    access_levels: Optional[List[str]] = Field(default=None, description="Filter by access levels (public, basic, advanced)")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")


class GetDocumentRequest(BaseModel):
    """Request DTO for getting a specific document."""

    document_id: str = Field(..., description="Document ID")
