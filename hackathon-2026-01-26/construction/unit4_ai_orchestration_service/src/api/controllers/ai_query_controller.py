from fastapi import APIRouter, Depends
from typing import Optional

from ...application.dtos import (
    ProcessQueryRequest,
    ProcessQueryResponse,
    DetectIntentRequest,
    DetectIntentResponse,
    QueryDetailsResponse,
)
from ...application.services import (
    ProcessAIQueryService,
    DetectIntentService,
    GetQueryDetailsService,
)
from ...domain.services import (
    IntentDetectionService,
    PromptEngineeringService,
    ResponseGenerationService,
    ConfidenceCalculationService,
)
from ...domain.repositories import IAIQueryRepository
from ...infrastructure.repositories import InMemoryAIQueryRepository
from ...infrastructure.ai_providers import MockAIProvider, BedrockAIProvider
from ...infrastructure.events import InMemoryEventPublisher
from ...infrastructure.rag import RAGDocumentClient
from ...application.clients import (
    MockDocumentSearchClient,
    MockConversationContextClient,
    DocumentRepositoryClient,
)
from ..middleware.error_handler import NotFoundError

router = APIRouter(prefix="/api/v1/ai", tags=["AI Orchestration"])

# Simple dependency injection (in production, use proper DI container)
_repository = InMemoryAIQueryRepository()
_event_publisher = InMemoryEventPublisher()

# Try to use Bedrock, fall back to Mock
try:
    _ai_provider = BedrockAIProvider(region="ap-southeast-1")
    if not _ai_provider.is_available():
        print("[AI Controller] Bedrock not available, using mock AI")
        _ai_provider = MockAIProvider()
except Exception as e:
    print(f"[AI Controller] Could not initialize Bedrock: {e}, using mock")
    _ai_provider = MockAIProvider()

# Try to use RAG Document Client (direct S3 access with embeddings)
# Falls back to Unit 3 client, then mock
_document_client = None
try:
    _document_client = RAGDocumentClient()
    if _document_client.is_available():
        stats = _document_client.get_stats()
        print(f"[AI Controller] Using RAG Document Client - {stats['documents_indexed']} docs indexed")
    else:
        _document_client = None
except Exception as e:
    print(f"[AI Controller] RAG Client failed: {e}")
    _document_client = None

if _document_client is None:
    # Fallback to Unit 3 service
    _document_client = DocumentRepositoryClient()
    if not _document_client.is_available():
        print("[AI Controller] Unit 3 not available, using mock documents")
        _document_client = MockDocumentSearchClient()


def get_process_service() -> ProcessAIQueryService:
    return ProcessAIQueryService(
        intent_service=IntentDetectionService(),
        prompt_service=PromptEngineeringService(),
        response_service=ResponseGenerationService(),
        confidence_service=ConfidenceCalculationService(),
        ai_provider=_ai_provider,
        document_client=_document_client,
        context_client=MockConversationContextClient(),
        repository=_repository,
        event_publisher=_event_publisher,
    )


def get_detect_service() -> DetectIntentService:
    return DetectIntentService(IntentDetectionService())


def get_query_service() -> GetQueryDetailsService:
    return GetQueryDetailsService(_repository)


@router.post("/process-query", response_model=ProcessQueryResponse)
async def process_query(
    request: ProcessQueryRequest,
    service: ProcessAIQueryService = Depends(get_process_service),
) -> ProcessQueryResponse:
    """Process a user query with AI."""
    return service.execute(request)


@router.post("/detect-intent", response_model=DetectIntentResponse)
async def detect_intent(
    request: DetectIntentRequest,
    service: DetectIntentService = Depends(get_detect_service),
) -> DetectIntentResponse:
    """Detect intent from query text."""
    return service.execute(request)


@router.get("/queries/{query_id}", response_model=QueryDetailsResponse)
async def get_query(
    query_id: str,
    service: GetQueryDetailsService = Depends(get_query_service),
) -> QueryDetailsResponse:
    """Get details of a processed query."""
    result = service.execute(query_id)
    if not result:
        raise NotFoundError(f"Query {query_id} not found")
    return result
