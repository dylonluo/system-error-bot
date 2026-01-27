"""Authorization Controller - Handles authorization endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from ...application.dtos import FilterDocumentsRequest, FilteredDocumentsResponse
from ...application.services import FilterDocumentsApplicationService
from ..middleware.jwt_authentication_middleware import get_current_user


router = APIRouter(prefix="/api/v1/auth", tags=["authorization"])

# Service will be injected via dependency injection in main.py
_filter_documents_service: FilterDocumentsApplicationService = None


def set_services(filter_documents_service: FilterDocumentsApplicationService):
    """Set service dependencies."""
    global _filter_documents_service
    _filter_documents_service = filter_documents_service


@router.post("/filter-documents", response_model=FilteredDocumentsResponse)
async def filter_documents(
    request_data: FilterDocumentsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Filter documents based on user's access level.
    
    Args:
        request_data: Documents to filter
        current_user: Current authenticated user
        
    Returns:
        FilteredDocumentsResponse with accessible documents
    """
    return _filter_documents_service.execute(request_data, current_user["user_id"])
