"""Filter Documents Application Service - Filters documents by access level."""
from ...domain.services import AuthorizationService
from ...domain.value_objects import UserId
from ..dtos import FilterDocumentsRequest, FilteredDocumentsResponse


class FilterDocumentsApplicationService:
    """Application service for filtering documents by access level."""
    
    def __init__(self, authorization_service: AuthorizationService):
        """
        Initialize FilterDocumentsApplicationService.
        
        Args:
            authorization_service: Authorization domain service
        """
        self._authorization_service = authorization_service
    
    def execute(
        self,
        request: FilterDocumentsRequest,
        user_id: str
    ) -> FilteredDocumentsResponse:
        """
        Execute document filtering.
        
        Args:
            request: Filter documents request
            user_id: User ID string
            
        Returns:
            FilteredDocumentsResponse with filtered documents
        """
        # Convert user_id to UserId
        user_id_obj = UserId(user_id)
        
        # Filter documents
        total_count = len(request.documents)
        filtered_docs = self._authorization_service.filter_documents_by_access(
            request.documents,
            user_id_obj
        )
        removed_count = total_count - len(filtered_docs)
        
        return FilteredDocumentsResponse(
            filtered_documents=filtered_docs,
            removed_count=removed_count,
            total_count=total_count
        )
