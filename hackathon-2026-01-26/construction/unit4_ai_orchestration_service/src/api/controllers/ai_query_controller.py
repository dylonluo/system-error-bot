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
from ...infrastructure.ai_providers import MockAIProvider
from ...infrastructure.events import InMemoryEventPublisher
from ...application.clients import (
    MockDocumentSearchClient,
    MockConversationContextClient,
)
from ..middleware.error_handler import NotFoundError

router = APIRouter(prefix="/api/v1/ai", tags=["AI Orchestration"])

# Simple dependency injection (in production, use proper DI container)
_repository = InMemoryAIQueryRepository()
_event_publisher = InMemoryEventPublisher()


def get_process_service() -> ProcessAIQueryService:
    return ProcessAIQueryService(
        intent_service=IntentDetectionService(),
        prompt_service=PromptEngineeringService(),
        response_service=ResponseGenerationService(),
        confidence_service=ConfidenceCalculationService(),
        ai_provider=MockAIProvider(),
        document_client=MockDocumentSearchClient(),
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
