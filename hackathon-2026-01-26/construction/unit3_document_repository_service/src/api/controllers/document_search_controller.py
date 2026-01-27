"""DocumentSearchController - REST API endpoints."""

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status

from ...application.dtos.requests import GetDocumentRequest, SearchDocumentsRequest
from ...application.dtos.responses import (
    DocumentMetadataResponse,
    DocumentResponse,
    SearchResultsResponse,
)


class DocumentSearchController:
    """Controller for document search endpoints."""

    def __init__(self, search_documents_service, get_document_service, get_document_metadata_service):
        self.router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
        self._search_documents_service = search_documents_service
        self._get_document_service = get_document_service
        self._get_document_metadata_service = get_document_metadata_service

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register all routes."""

        @self.router.get("/search", response_model=SearchResultsResponse)
        async def search_documents(
            query: str,
            sources: Optional[str] = None,
            document_types: Optional[str] = None,
            formats: Optional[str] = None,
            access_levels: Optional[str] = None,
            limit: int = 50,
            authorization: str = Header(...),
        ):
            """Search for documents."""
            try:
                # Parse comma-separated filters
                request = SearchDocumentsRequest(
                    query=query,
                    sources=sources.split(",") if sources else None,
                    document_types=document_types.split(",") if document_types else None,
                    formats=formats.split(",") if formats else None,
                    access_levels=access_levels.split(",") if access_levels else None,
                    limit=limit,
                )

                return self._search_documents_service.execute(request, authorization)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            except PermissionError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.get("/{document_id}", response_model=DocumentResponse)
        async def get_document(document_id: str, authorization: str = Header(...)):
            """Get a specific document by ID."""
            try:
                request = GetDocumentRequest(document_id=document_id)
                return self._get_document_service.execute(request, authorization)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.get("/{document_id}/metadata", response_model=DocumentMetadataResponse)
        async def get_document_metadata(document_id: str, authorization: str = Header(...)):
            """Get metadata for a specific document."""
            try:
                request = GetDocumentRequest(document_id=document_id)
                return self._get_document_metadata_service.execute(request, authorization)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
