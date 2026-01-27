"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..application.services.get_document_metadata_service import (
    GetDocumentMetadataApplicationService,
)
from ..application.services.get_document_service import GetDocumentApplicationService
from ..application.services.search_documents_service import (
    SearchDocumentsApplicationService,
)
from ..domain.services.document_metadata_refresh_service import (
    DocumentMetadataRefreshService,
)
from ..domain.services.document_search_service import DocumentSearchService
from ..domain.services.relevance_ranking_service import RelevanceRankingService
from ..infrastructure.adapters.in_memory_cache_provider import InMemoryCacheProvider
from ..infrastructure.adapters.mock_access_control_client import MockAccessControlClient
from ..infrastructure.adapters.mock_s3_search_adapter import MockS3SearchAdapter

# Try to use real S3 adapter, fall back to mock if AWS credentials not available
try:
    from ..infrastructure.adapters.s3_search_adapter import S3SearchAdapter
    s3_adapter = S3SearchAdapter(
        bucket_name="cslr-hackathon-sg-test",
        prefix="Byte-Us-Rawr/PDF/",
        region="ap-southeast-1"
    )
    if not s3_adapter.is_available():
        print("[Main] Real S3 adapter not available, falling back to mock")
        s3_adapter = MockS3SearchAdapter()
except Exception as e:
    print(f"[Main] Could not initialize S3 adapter: {e}, using mock")
    s3_adapter = MockS3SearchAdapter()
from ..infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from ..infrastructure.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from ..infrastructure.repositories.in_memory_search_query_repository import (
    InMemorySearchQueryRepository,
)
from .controllers.document_search_controller import DocumentSearchController

# Initialize infrastructure components
document_repository = InMemoryDocumentRepository()
search_query_repository = InMemorySearchQueryRepository()
access_control_client = MockAccessControlClient()
cache_provider = InMemoryCacheProvider()
event_publisher = InMemoryEventPublisher()

# s3_adapter is initialized above (real or mock)

# Initialize domain services
ranking_service = RelevanceRankingService()
document_search_service = DocumentSearchService(s3_adapter=s3_adapter, ranking_service=ranking_service)
metadata_refresh_service = DocumentMetadataRefreshService(document_repository=document_repository, s3_adapter=s3_adapter)

# Initialize application services
search_documents_service = SearchDocumentsApplicationService(
    access_control_client=access_control_client,
    document_search_service=document_search_service,
    document_repository=document_repository,
    search_query_repository=search_query_repository,
    cache_provider=cache_provider,
    event_publisher=event_publisher,
)

get_document_service = GetDocumentApplicationService(
    access_control_client=access_control_client,
    document_repository=document_repository,
    metadata_refresh_service=metadata_refresh_service,
    event_publisher=event_publisher,
)

get_document_metadata_service = GetDocumentMetadataApplicationService(
    access_control_client=access_control_client, document_repository=document_repository
)

# Initialize controller
document_controller = DocumentSearchController(
    search_documents_service=search_documents_service,
    get_document_service=get_document_service,
    get_document_metadata_service=get_document_metadata_service,
)

# Create FastAPI app
app = FastAPI(
    title="Document Repository Service", description="Search and retrieve documentation from external sources", version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(document_controller.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "document-repository-service", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Document Repository Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/api/v1/documents/search",
            "get_document": "/api/v1/documents/{document_id}",
            "get_metadata": "/api/v1/documents/{document_id}/metadata",
        },
    }
