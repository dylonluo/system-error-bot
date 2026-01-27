"""GetDocumentMetadataApplicationService."""

from ...domain.value_objects.document_id import DocumentId
from ..dtos.requests import GetDocumentRequest
from ..dtos.responses import DocumentMetadataResponse


class GetDocumentMetadataApplicationService:
    """Application service for retrieving document metadata."""

    def __init__(self, access_control_client, document_repository):
        self._access_control_client = access_control_client
        self._document_repository = document_repository

    def execute(self, request: GetDocumentRequest, token: str) -> DocumentMetadataResponse:
        """Execute get document metadata workflow."""
        # 1. Validate user authentication
        user = self._access_control_client.validate_token(token)
        user_access_level = user["access_level"]

        # 2. Retrieve document from repository
        document_id = DocumentId(request.document_id)
        document = self._document_repository.find_by_id(document_id)

        if not document:
            raise ValueError(f"Document not found: {request.document_id}")

        # 3. Verify user has access
        if not document.is_accessible_by(user_access_level):
            raise PermissionError(f"User does not have access to document: {request.document_id}")

        # 4. Build and return metadata response
        if not document.metadata:
            raise ValueError(f"No metadata available for document: {request.document_id}")

        return DocumentMetadataResponse(
            author=document.metadata.author,
            created_at=document.metadata.created_at,
            last_modified=document.metadata.last_modified,
            file_size=document.metadata.file_size,
            tags=document.metadata.tags,
            category=document.metadata.category,
        )
