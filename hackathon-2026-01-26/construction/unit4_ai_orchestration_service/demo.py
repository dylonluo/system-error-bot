"""
AI Orchestration Service Demo
=============================
Run: python demo.py
"""
from uuid import uuid4

from src.domain.services import (
    IntentDetectionService,
    PromptEngineeringService,
    ResponseGenerationService,
    ConfidenceCalculationService,
)
from src.infrastructure.repositories import InMemoryAIQueryRepository
from src.infrastructure.ai_providers import MockAIProvider
from src.infrastructure.events import InMemoryEventPublisher
from src.application.clients import (
    MockDocumentSearchClient,
    MockConversationContextClient,
)
from src.application.services import ProcessAIQueryService, DetectIntentService
from src.application.dtos import ProcessQueryRequest, DetectIntentRequest


def create_services():
    """Create all services with dependencies."""
    repository = InMemoryAIQueryRepository()
    event_publisher = InMemoryEventPublisher()

    process_service = ProcessAIQueryService(
        intent_service=IntentDetectionService(),
        prompt_service=PromptEngineeringService(),
        response_service=ResponseGenerationService(),
        confidence_service=ConfidenceCalculationService(),
        ai_provider=MockAIProvider(),
        document_client=MockDocumentSearchClient(),
        context_client=MockConversationContextClient(),
        repository=repository,
        event_publisher=event_publisher,
    )

    detect_service = DetectIntentService(IntentDetectionService())

    return process_service, detect_service, event_publisher


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_error_query(process_service):
    """Demo: NetSuite error troubleshooting query."""
    print_separator("Demo 1: NetSuite Error Query (On-Topic)")
    
    request = ProcessQueryRequest(
        query="I'm getting NS_ERROR_INVALID_RECORD when trying to save a customer record",
        conversation_id=uuid4(),
        user_id=uuid4(),
    )
    
    response = process_service.execute(request)
    
    print(f"Query: {request.query}")
    print(f"\nIntent: {response.intent}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Suggest Escalation: {response.suggest_escalation}")
    print(f"Processing Time: {response.processing_time_ms}ms")
    print(f"\nResponse:\n{response.response}")
    print(f"\nDocumentation Links ({len(response.documentation_links)}):")
    for link in response.documentation_links:
        print(f"  - [{link.category}] {link.title}")
        print(f"    {link.url}")


def demo_task_query(process_service):
    """Demo: TMS task guidance query."""
    print_separator("Demo 2: TMS Task Query (On-Topic)")
    
    request = ProcessQueryRequest(
        query="How do I configure a new carrier in TMS?",
        conversation_id=uuid4(),
        user_id=uuid4(),
    )
    
    response = process_service.execute(request)
    
    print(f"Query: {request.query}")
    print(f"\nIntent: {response.intent}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Suggest Escalation: {response.suggest_escalation}")
    print(f"Processing Time: {response.processing_time_ms}ms")
    print(f"\nResponse:\n{response.response}")
    print(f"\nDocumentation Links ({len(response.documentation_links)}):")
    for link in response.documentation_links:
        print(f"  - [{link.category}] {link.title}")


def demo_off_topic_query(process_service):
    """Demo: Off-topic query rejection."""
    print_separator("Demo 3: Off-Topic Query (Rejected)")
    
    request = ProcessQueryRequest(
        query="What's the weather like in Shenzhen today?",
        conversation_id=uuid4(),
        user_id=uuid4(),
    )
    
    response = process_service.execute(request)
    
    print(f"Query: {request.query}")
    print(f"\nIntent: {response.intent}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Processing Time: {response.processing_time_ms}ms")
    print(f"\nResponse:\n{response.response}")
    print(f"\nDocumentation Links: {len(response.documentation_links)} (none for off-topic)")


def demo_intent_detection(detect_service):
    """Demo: Standalone intent detection."""
    print_separator("Demo 4: Intent Detection")
    
    queries = [
        "NS_ERROR_PERMISSION_DENIED when accessing reports",
        "How to create a saved search in NetSuite?",
        "What is the TMS shipment workflow?",
        "Tell me a joke",
    ]
    
    for query in queries:
        request = DetectIntentRequest(query=query)
        response = detect_service.execute(request)
        print(f"\nQuery: {query}")
        print(f"  Intent: {response.intent}")
        print(f"  Confidence: {response.confidence:.2f}")
        if response.entities:
            print(f"  Entities: {response.entities}")


def demo_events(event_publisher):
    """Demo: Published domain events."""
    print_separator("Demo 5: Published Events")
    
    events = event_publisher.get_published_events()
    print(f"Total events published: {len(events)}")
    for event in events:
        print(f"  - {type(event).__name__}")


def main():
    print("\n" + "="*60)
    print("  AI ORCHESTRATION SERVICE - DEMO")
    print("="*60)
    
    process_service, detect_service, event_publisher = create_services()
    
    demo_error_query(process_service)
    demo_task_query(process_service)
    demo_off_topic_query(process_service)
    demo_intent_detection(detect_service)
    demo_events(event_publisher)
    
    print_separator("Demo Complete!")
    print("All scenarios executed successfully.\n")


if __name__ == "__main__":
    main()
