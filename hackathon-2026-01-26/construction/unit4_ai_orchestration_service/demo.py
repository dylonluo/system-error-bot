"""
AI Orchestration Service Demo with RAG
======================================
Run: python demo.py

This demo shows the AI service with RAG (Retrieval-Augmented Generation),
which extracts and uses actual content from your S3 PDF documents.
"""
import sys
from uuid import uuid4

from src.domain.services import (
    IntentDetectionService,
    PromptEngineeringService,
    ResponseGenerationService,
    ConfidenceCalculationService,
)
from src.infrastructure.repositories import InMemoryAIQueryRepository
from src.infrastructure.ai_providers import MockAIProvider, BedrockAIProvider
from src.infrastructure.events import InMemoryEventPublisher
from src.application.clients import (
    MockDocumentSearchClient,
    MockConversationContextClient,
)
from src.application.services import ProcessAIQueryService, DetectIntentService
from src.application.dtos import ProcessQueryRequest, DetectIntentRequest


def create_services(use_rag: bool = True, use_bedrock: bool = True):
    """Create all services with dependencies.
    
    Args:
        use_rag: If True, use RAG client that reads actual S3 documents
        use_bedrock: If True, use Amazon Bedrock for AI responses
    """
    repository = InMemoryAIQueryRepository()
    event_publisher = InMemoryEventPublisher()

    # Choose document client
    if use_rag:
        try:
            from src.infrastructure.rag import RAGDocumentClient
            document_client = RAGDocumentClient(
                bucket_name="cslr-hackathon-sg-test",
                prefix="Byte-Us-Rawr/PDF/",
                region="ap-southeast-1",
            )
            print(f"\n[Setup] RAG Client initialized")
            stats = document_client.get_stats()
            print(f"[Setup] Documents indexed: {stats['documents_indexed']}")
            print(f"[Setup] Total chunks: {stats['total_chunks']}")
        except Exception as e:
            print(f"\n[Setup] RAG Client failed: {e}")
            print("[Setup] Falling back to mock document client")
            document_client = MockDocumentSearchClient()
    else:
        document_client = MockDocumentSearchClient()
        print("\n[Setup] Using mock document client")

    # Choose AI provider
    if use_bedrock:
        ai_provider = BedrockAIProvider(region="ap-southeast-1")
        if ai_provider.is_available():
            print(f"[Setup] Using Bedrock AI: {ai_provider.get_model_name()}")
        else:
            print("[Setup] Bedrock unavailable, using mock AI")
            ai_provider = MockAIProvider()
    else:
        ai_provider = MockAIProvider()
        print("[Setup] Using mock AI provider")

    process_service = ProcessAIQueryService(
        intent_service=IntentDetectionService(),
        prompt_service=PromptEngineeringService(),
        response_service=ResponseGenerationService(),
        confidence_service=ConfidenceCalculationService(),
        ai_provider=ai_provider,
        document_client=document_client,
        context_client=MockConversationContextClient(),
        repository=repository,
        event_publisher=event_publisher,
    )

    detect_service = DetectIntentService(IntentDetectionService())

    return process_service, detect_service, event_publisher, document_client


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_rag_query(process_service, query: str, title: str = "RAG Query"):
    """Demo: Query with RAG - AI uses actual document content."""
    print_separator(title)
    
    request = ProcessQueryRequest(
        query=query,
        conversation_id=uuid4(),
        user_id=uuid4(),
    )
    
    response = process_service.execute(request)
    
    print(f"Query: {request.query}")
    print(f"\nIntent: {response.intent}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Suggest Escalation: {response.suggest_escalation}")
    print(f"Processing Time: {response.processing_time_ms}ms")
    print(f"\n{'─'*40}")
    print("AI RESPONSE (based on your documents):")
    print('─'*40)
    print(response.response)
    print(f"\n{'─'*40}")
    print(f"Documentation Links ({len(response.documentation_links)}):")
    print('─'*40)
    for link in response.documentation_links:
        print(f"  📄 [{link.category}] {link.title}")
        if link.description:
            desc = link.description[:100] + "..." if len(link.description) > 100 else link.description
            print(f"     {desc}")


def demo_off_topic_query(process_service):
    """Demo: Off-topic query rejection."""
    print_separator("Off-Topic Query (Rejected)")
    
    request = ProcessQueryRequest(
        query="What's the weather like today?",
        conversation_id=uuid4(),
        user_id=uuid4(),
    )
    
    response = process_service.execute(request)
    
    print(f"Query: {request.query}")
    print(f"\nIntent: {response.intent}")
    print(f"Response: {response.response}")


def demo_document_search(document_client, query: str):
    """Demo: Direct document search to see what's being retrieved."""
    print_separator(f"Document Search: '{query}'")
    
    if hasattr(document_client, 'search_with_context'):
        results = document_client.search_with_context(query, top_k=3)
        print(f"Found {len(results)} relevant documents:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.document_link.title}")
            print(f"   Category: {result.document_link.category}")
            print(f"   Relevance: {result.document_link.relevance:.2f}")
            print(f"   Content preview:")
            preview = result.combined_context[:300] + "..." if len(result.combined_context) > 300 else result.combined_context
            for line in preview.split('\n')[:5]:
                print(f"   | {line[:80]}")
            print()
    else:
        results = document_client.search(query)
        print(f"Found {len(results)} documents (mock client - no content)")
        for doc in results:
            print(f"  - {doc.title}")


def interactive_mode(process_service, document_client):
    """Interactive mode - ask questions and get RAG-powered answers."""
    print_separator("Interactive Mode")
    print("Ask questions about NetSuite/TMS. Type 'quit' to exit.")
    print("Type 'search: <query>' to see raw document search results.")
    print()
    
    while True:
        try:
            query = input("\n🔍 Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
            
        if not query:
            continue
        if query.lower() in ('quit', 'exit', 'q'):
            break
        
        if query.lower().startswith('search:'):
            search_query = query[7:].strip()
            demo_document_search(document_client, search_query)
        else:
            demo_rag_query(process_service, query, "Your Query")


def main():
    print("\n" + "="*60)
    print("  AI ORCHESTRATION SERVICE - RAG DEMO")
    print("  (Retrieval-Augmented Generation)")
    print("="*60)
    
    # Parse command line args
    use_rag = "--no-rag" not in sys.argv
    use_bedrock = "--no-bedrock" not in sys.argv
    interactive = "--interactive" in sys.argv or "-i" in sys.argv
    
    print(f"\nOptions: RAG={'ON' if use_rag else 'OFF'}, Bedrock={'ON' if use_bedrock else 'OFF'}")
    
    process_service, detect_service, event_publisher, document_client = create_services(
        use_rag=use_rag,
        use_bedrock=use_bedrock,
    )
    
    if interactive:
        interactive_mode(process_service, document_client)
    else:
        # Run demo queries
        demo_queries = [
            ("NetSuite Error Query", "I'm getting an error when trying to sync invoices in NetSuite"),
            ("Sales Order Query", "How do I create a sales order in NetSuite?"),
            ("TMS Integration Query", "What is the process for TMS integration?"),
        ]
        
        for title, query in demo_queries:
            demo_rag_query(process_service, query, title)
        
        # Show document search
        demo_document_search(document_client, "invoice error")
        
        # Off-topic
        demo_off_topic_query(process_service)
        
        print_separator("Demo Complete!")
        print("\nTo try interactive mode, run: python demo.py --interactive")
        print("To disable RAG: python demo.py --no-rag")
        print("To disable Bedrock: python demo.py --no-bedrock\n")


if __name__ == "__main__":
    main()
