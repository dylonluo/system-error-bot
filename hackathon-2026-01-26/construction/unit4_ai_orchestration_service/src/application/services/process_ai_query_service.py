import time
from typing import List

from ...domain.aggregates import AIQuery
from ...domain.services import (
    IntentDetectionService,
    PromptEngineeringService,
    ResponseGenerationService,
    ConfidenceCalculationService,
)
from ...domain.services.response_generation_service import DocumentLink
from ...domain.repositories import IAIQueryRepository
from ...domain.events import QueryProcessed, OffTopicQueryDetected, LowConfidenceDetected
from ...domain.value_objects import ProcessingMetrics, ConfidenceScore
from ...infrastructure.ai_providers import IAIProvider
from ...infrastructure.events import InMemoryEventPublisher
from ..clients import IDocumentSearchClient, IConversationContextClient
from ..dtos import ProcessQueryRequest, ProcessQueryResponse, DocumentationLinkResponse


class ProcessAIQueryService:
    """Main application service for processing AI queries."""

    def __init__(
        self,
        intent_service: IntentDetectionService,
        prompt_service: PromptEngineeringService,
        response_service: ResponseGenerationService,
        confidence_service: ConfidenceCalculationService,
        ai_provider: IAIProvider,
        document_client: IDocumentSearchClient,
        context_client: IConversationContextClient,
        repository: IAIQueryRepository,
        event_publisher: InMemoryEventPublisher,
    ):
        self._intent_service = intent_service
        self._prompt_service = prompt_service
        self._response_service = response_service
        self._confidence_service = confidence_service
        self._ai_provider = ai_provider
        self._document_client = document_client
        self._context_client = context_client
        self._repository = repository
        self._event_publisher = event_publisher

    def execute(self, request: ProcessQueryRequest) -> ProcessQueryResponse:
        """Process an AI query end-to-end."""
        start_time = time.time()

        # Create aggregate
        ai_query = AIQuery.create(
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            query_text=request.query,
        )

        # Load conversation context
        context_messages = self._context_client.get_conversation_history(
            request.conversation_id, limit=5
        )
        ai_query.add_context(context_messages)

        # Detect intent
        intent = self._intent_service.detect_intent(request.query)
        ai_query.set_intent(intent)

        # Handle off-topic queries
        if intent.is_off_topic():
            return self._handle_off_topic(ai_query, start_time)

        # Build prompt and call AI
        ai_start = time.time()
        prompt = self._prompt_service.build_prompt(
            request.query, intent, context_messages
        )
        ai_response = self._ai_provider.generate_response(prompt)
        ai_query.set_ai_response(ai_response)
        ai_time_ms = int((time.time() - ai_start) * 1000)

        # Search documents
        doc_start = time.time()
        documents = self._document_client.search(request.query)
        doc_time_ms = int((time.time() - doc_start) * 1000)

        # Generate response
        response_data = self._response_service.generate_response(ai_response, documents)

        # Calculate confidence
        confidence = self._confidence_service.calculate_confidence(
            ai_response, documents, intent
        )
        ai_query.set_confidence(confidence)

        # Record metrics
        total_time_ms = int((time.time() - start_time) * 1000)
        metrics = ProcessingMetrics.create(
            total_time_ms=total_time_ms,
            ai_processing_time_ms=ai_time_ms,
            document_search_time_ms=doc_time_ms,
            tokens_used=ai_response.tokens_used,
        )
        ai_query.record_metrics(metrics)

        # Save and publish events
        self._repository.save(ai_query)
        self._publish_events(ai_query, total_time_ms)

        return self._build_response(ai_query, response_data, documents, total_time_ms)

    def _handle_off_topic(self, ai_query: AIQuery, start_time: float) -> ProcessQueryResponse:
        """Handle off-topic queries without calling AI."""
        response_data = self._response_service.generate_off_topic_response()
        
        # Set low confidence for off-topic
        ai_query.set_confidence(ConfidenceScore(value=0.0))
        
        total_time_ms = int((time.time() - start_time) * 1000)
        metrics = ProcessingMetrics.create(total_time_ms=total_time_ms)
        ai_query.record_metrics(metrics)

        self._repository.save(ai_query)
        self._event_publisher.publish(OffTopicQueryDetected(
            query_id=ai_query.query_id.value,
            query_text=str(ai_query.query_text),
        ))

        return ProcessQueryResponse(
            query_id=ai_query.query_id.value,
            response=response_data["content"],
            documentation_links=[],
            confidence=0.0,
            suggest_escalation=False,
            processing_time_ms=total_time_ms,
            intent="off_topic",
        )

    def _publish_events(self, ai_query: AIQuery, processing_time_ms: int) -> None:
        """Publish domain events."""
        self._event_publisher.publish(QueryProcessed(
            query_id=ai_query.query_id.value,
            conversation_id=ai_query.conversation_id,
            user_id=ai_query.user_id,
            intent=ai_query.intent.intent_type.value if ai_query.intent else "",
            confidence=ai_query.confidence_score.value if ai_query.confidence_score else 0.0,
            processing_time_ms=processing_time_ms,
        ))

        if ai_query.should_escalate():
            self._event_publisher.publish(LowConfidenceDetected(
                query_id=ai_query.query_id.value,
                confidence=ai_query.confidence_score.value if ai_query.confidence_score else 0.0,
            ))

    def _build_response(
        self,
        ai_query: AIQuery,
        response_data: dict,
        documents: List[DocumentLink],
        processing_time_ms: int,
    ) -> ProcessQueryResponse:
        """Build the final response."""
        return ProcessQueryResponse(
            query_id=ai_query.query_id.value,
            response=response_data["content"],
            documentation_links=[
                DocumentationLinkResponse(
                    title=link["title"],
                    url=link["url"],
                    description=link["description"],
                    category=link["category"],
                )
                for link in response_data["documentation_links"]
            ],
            confidence=ai_query.confidence_score.value if ai_query.confidence_score else 0.0,
            suggest_escalation=ai_query.should_escalate(),
            processing_time_ms=processing_time_ms,
            intent=ai_query.intent.intent_type.value if ai_query.intent else "",
        )
