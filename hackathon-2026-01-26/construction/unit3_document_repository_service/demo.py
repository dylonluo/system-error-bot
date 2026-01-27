"""Demo script for Document Repository Service."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.application.dtos.requests import GetDocumentRequest, SearchDocumentsRequest
from src.application.services.get_document_service import GetDocumentApplicationService
from src.application.services.search_documents_service import (
    SearchDocumentsApplicationService,
)
from src.domain.services.document_metadata_refresh_service import (
    DocumentMetadataRefreshService,
)
from src.domain.services.document_search_service import DocumentSearchService
from src.domain.services.relevance_ranking_service import RelevanceRankingService
from src.infrastructure.adapters.in_memory_cache_provider import InMemoryCacheProvider
from src.infrastructure.adapters.mock_access_control_client import (
    MockAccessControlClient,
)
from src.infrastructure.adapters.mock_s3_search_adapter import MockS3SearchAdapter
from src.infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from src.infrastructure.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from src.infrastructure.repositories.in_memory_search_query_repository import (
    InMemorySearchQueryRepository,
)


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def demo_search_documents():
    """Demo: Search for documents."""
    print_separator()
    print("DEMO 1: Search Documents")
    print_separator()

    # Setup
    document_repository = InMemoryDocumentRepository()
    search_query_repository = InMemorySearchQueryRepository()
    s3_adapter = MockS3SearchAdapter()
    access_control_client = MockAccessControlClient()
    cache_provider = InMemoryCacheProvider()
    event_publisher = InMemoryEventPublisher()

    ranking_service = RelevanceRankingService()
    document_search_service = DocumentSearchService(s3_adapter=s3_adapter, ranking_service=ranking_service)

    search_service = SearchDocumentsApplicationService(
        access_control_client=access_control_client,
        document_search_service=document_search_service,
        document_repository=document_repository,
        search_query_repository=search_query_repository,
        cache_provider=cache_provider,
        event_publisher=event_publisher,
    )

    # Test 1: Search for "NetSuite" as end user
    print("Test 1: Search for 'NetSuite' as End User (basic access)")
    request = SearchDocumentsRequest(query="NetSuite", limit=10)
    token = "user-123"  # End user token

    try:
        response = search_service.execute(request, token)
        print(f"✓ Query: {response.query}")
        print(f"✓ Total Results: {response.total_results}")
        print(f"✓ Execution Time: {response.execution_time_ms}ms")
        print(f"\nResults:")
        for i, doc in enumerate(response.results, 1):
            print(f"  {i}. {doc.title}")
            print(f"     URL: {doc.url}")
            print(f"     Type: {doc.document_type}, Access: {doc.access_level}")
            print(f"     Relevance: {doc.relevance_score:.2f}")
            print()
    except Exception as e:
        print(f"✗ Error: {e}")

    print_separator()

    # Test 2: Search for "TMS" as administrator
    print("Test 2: Search for 'TMS' as Administrator (all access)")
    request = SearchDocumentsRequest(query="TMS", limit=10)
    token = "admin-456"  # Admin token

    try:
        response = search_service.execute(request, token)
        print(f"✓ Query: {response.query}")
        print(f"✓ Total Results: {response.total_results}")
        print(f"✓ Execution Time: {response.execution_time_ms}ms")
        print(f"\nResults:")
        for i, doc in enumerate(response.results, 1):
            print(f"  {i}. {doc.title}")
            print(f"     URL: {doc.url}")
            print(f"     Type: {doc.document_type}, Access: {doc.access_level}")
            print(f"     Relevance: {doc.relevance_score:.2f}")
            print()
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_get_document_by_id():
    """Demo: Get document by ID."""
    print_separator()
    print("DEMO 2: Get Document by ID")
    print_separator()

    # Setup
    document_repository = InMemoryDocumentRepository()
    s3_adapter = MockS3SearchAdapter()
    access_control_client = MockAccessControlClient()
    event_publisher = InMemoryEventPublisher()

    metadata_refresh_service = DocumentMetadataRefreshService(document_repository=document_repository, s3_adapter=s3_adapter)

    get_document_service = GetDocumentApplicationService(
        access_control_client=access_control_client,
        document_repository=document_repository,
        metadata_refresh_service=metadata_refresh_service,
        event_publisher=event_publisher,
    )

    # Pre-populate repository with sample documents from S3 adapter
    for doc in s3_adapter._documents:
        document_repository.save(doc)

    # Test: Get a specific document
    print("Test: Get NetSuite Error Troubleshooting Guide")
    doc_id = str(s3_adapter._documents[0].document_id)
    request = GetDocumentRequest(document_id=doc_id)
    token = "user-123"  # End user token

    try:
        response = get_document_service.execute(request, token)
        print(f"✓ Document ID: {response.id}")
        print(f"✓ Title: {response.title}")
        print(f"✓ URL: {response.url}")
        print(f"✓ Source: {response.source}")
        print(f"✓ Type: {response.document_type}")
        print(f"✓ Access Level: {response.access_level}")
        print(f"✓ Access Count: {response.access_count}")
        print(f"\nMetadata:")
        if response.metadata:
            print(f"  Author: {response.metadata.author}")
            print(f"  Tags: {', '.join(response.metadata.tags)}")
            print(f"  Category: {response.metadata.category}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_access_level_filtering():
    """Demo: Access level filtering."""
    print_separator()
    print("DEMO 3: Access Level Filtering")
    print_separator()

    # Setup
    document_repository = InMemoryDocumentRepository()
    search_query_repository = InMemorySearchQueryRepository()
    s3_adapter = MockS3SearchAdapter()
    access_control_client = MockAccessControlClient()
    cache_provider = InMemoryCacheProvider()
    event_publisher = InMemoryEventPublisher()

    ranking_service = RelevanceRankingService()
    document_search_service = DocumentSearchService(s3_adapter=s3_adapter, ranking_service=ranking_service)

    search_service = SearchDocumentsApplicationService(
        access_control_client=access_control_client,
        document_search_service=document_search_service,
        document_repository=document_repository,
        search_query_repository=search_query_repository,
        cache_provider=cache_provider,
        event_publisher=event_publisher,
    )

    # Test 1: End user searching (should NOT see ADVANCED documents)
    print("Test 1: End User searching for 'integration' (basic access)")
    request = SearchDocumentsRequest(query="integration", limit=10)
    token = "user-123"

    try:
        response = search_service.execute(request, token)
        print(f"✓ Total Results: {response.total_results}")
        print(f"\nResults (End User can see):")
        for doc in response.results:
            print(f"  - {doc.title} [Access: {doc.access_level}]")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "-" * 80 + "\n")

    # Test 2: Administrator searching (should see ALL documents)
    print("Test 2: Administrator searching for 'integration' (all access)")
    request = SearchDocumentsRequest(query="integration", limit=10)
    token = "admin-456"

    try:
        response = search_service.execute(request, token)
        print(f"✓ Total Results: {response.total_results}")
        print(f"\nResults (Administrator can see):")
        for doc in response.results:
            print(f"  - {doc.title} [Access: {doc.access_level}]")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "-" * 80 + "\n")

    # Test 3: Try to access ADVANCED document as end user (should fail)
    print("Test 3: End User trying to access ADVANCED document")

    # Find an ADVANCED document
    advanced_doc = None
    for doc in s3_adapter._documents:
        if str(doc.access_level) == "advanced":
            advanced_doc = doc
            document_repository.save(doc)
            break

    if advanced_doc:
        get_document_service = GetDocumentApplicationService(
            access_control_client=access_control_client,
            document_repository=document_repository,
            metadata_refresh_service=DocumentMetadataRefreshService(
                document_repository=document_repository, s3_adapter=s3_adapter
            ),
            event_publisher=event_publisher,
        )

        request = GetDocumentRequest(document_id=str(advanced_doc.document_id))
        token = "user-123"  # End user

        try:
            response = get_document_service.execute(request, token)
            print(f"✗ Should have failed but got: {response.title}")
        except PermissionError as e:
            print(f"✓ Correctly denied access: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print(" " * 20 + "DOCUMENT REPOSITORY SERVICE DEMO")
    print("=" * 80)

    # Run demos
    demo_search_documents()
    demo_get_document_by_id()
    demo_access_level_filtering()

    print_separator()
    print("✓ All demos completed successfully!")
    print_separator()


if __name__ == "__main__":
    main()
