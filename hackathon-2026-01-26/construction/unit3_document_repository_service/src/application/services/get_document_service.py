"""GetDocumentApplicationService."""

from ...domain.events.domain_events import DocumentAccessed
from ...domain.value_objects.document_id import DocumentId
from ..dtos.requests import GetDocumentRequest
from ..dtos.responses import DocumentMetadataResponse, DocumentResponse


class GetDocumentApplicationService:
    """Application service for retrieving a specific document."""

    def __init__(self, access_control_client, document_repository, metadata_refresh_service, event_publisher):
        self._access_control_client = access_control_client
        self._document_repository = document_repository
        self._metadata_refresh_service = metadata_refresh_service
        self._event_publisher = event_publisher

    def execute(self, request: GetDocumentRequest, token: str) -> DocumentResponse:
        """Execute get document workflow."""
        # 1. Validate user authentication
        user = self._access_control_client.validate_token(token)
        user_id = user["user_id"]
        user_access_level = user["access_level"]

        # 2. Retrieve document from repository
        document_id = DocumentId(request.document_id)
        document = self._document_repository.find_by_id(document_id)

        if not document:
            raise ValueError(f"Document not found: {request.document_id}")

        # 3. Verify user has access
        if not document.is_accessible_by(user_access_level):
            raise PermissionError(f"User does not have access to document: {request.document_id}")

        # 4. Mark document as accessed
        document.mark_as_accessed()

        # 5. Refresh metadata if stale (> 24 hours)
        if document.needs_metadata_refresh(hours=24):
            try:
                self._metadata_refresh_service.refresh_metadata(document_id)
            except Exception as e:
                print(f"Failed to refresh metadata: {e}")

        # 6. Save updated document
        self._document_repository.save(document)

        # 7. Publish DocumentAccessed event
        event = DocumentAccessed(document_id=document_id, user_id=user_id, source=document.source)
        self._event_publisher.publish(event)

        # 8. Build and return response
        return self._build_response(document)

    def _build_response(self, document) -> DocumentResponse:
        """Build document response."""
        metadata_response = None
        if document.metadata:
            metadata_response = DocumentMetadataResponse(
                author=document.metadata.author,
                created_at=document.metadata.created_at,
                last_modified=document.metadata.last_modified,
                file_size=document.metadata.file_size,
                tags=document.metadata.tags,
                category=document.metadata.category,
            )

        return DocumentResponse(
            id=str(document.document_id),
            title=str(document.title),
            url=str(document.url),
            source=str(document.source.value.value),
            platform_id=document.source.platform_id,
            document_type=str(document.document_type.value.value),
            format=str(document.format.value.value),
            access_level=str(document.access_level.value.value),
            snippet=document.snippet,
            metadata=metadata_response,
            last_modified=document.last_modified,
            access_count=document.access_count,
        )
