"""SearchDocumentsApplicationService."""

from datetime import datetime
from typing import List

from ...domain.aggregates.search_query import SearchQuery
from ...domain.events.domain_events import SearchExecuted
from ...domain.value_objects.document_access_level import AccessLevel
from ...domain.value_objects.document_format import DocFormat
from ...domain.value_objects.document_source import Source
from ...domain.value_objects.document_type import DocType
from ...domain.value_objects.query_id import QueryId
from ...domain.value_objects.query_text import QueryText
from ...domain.value_objects.search_filters import SearchFilters
from ..dtos.requests import SearchDocumentsRequest
from ..dtos.responses import (
    DocumentMetadataResponse,
    DocumentResponse,
    SearchResultsResponse,
)


class SearchDocumentsApplicationService:
    """Application service for searching documents."""

    def __init__(
        self,
        access_control_client,
        document_search_service,
        document_repository,
        search_query_repository,
        cache_provider,
        event_publisher,
    ):
        self._access_control_client = access_control_client
        self._document_search_service = document_search_service
        self._document_repository = document_repository
        self._search_query_repository = search_query_repository
        self._cache_provider = cache_provider
        self._event_publisher = event_publisher

    def execute(self, request: SearchDocumentsRequest, token: str) -> SearchResultsResponse:
        """Execute document search workflow."""
        start_time = datetime.now()

        # 1. Validate user authentication
        user = self._access_control_client.validate_token(token)
        user_id = user["user_id"]

        # 2. Build search filters
        filters = self._build_filters(request)

        # 3. Check cache for recent search
        cache_key = f"search:{request.query}:{user_id}"
        cached_results = self._cache_provider.get(cache_key)
        if cached_results:
            return cached_results

        # 4. Execute search via domain service
        query_text = QueryText(request.query)
        scored_documents = self._document_search_service.search(str(query_text), filters, user_id)

        # 5. Filter results by user access level
        documents_only = [doc for doc, score in scored_documents]
        filtered_docs = self._access_control_client.filter_documents(documents_only, user_id)

        # Rebuild scored list with filtered documents
        filtered_scored = [(doc, score) for doc, score in scored_documents if doc in filtered_docs]

        # 6. Limit results
        limited_results = filtered_scored[: request.limit]

        # 7. Create search query aggregate
        query_id = QueryId.generate()
        search_query = SearchQuery(
            query_id=query_id, query_text=query_text, filters=filters, requested_by=user_id, result_count=len(limited_results)
        )

        # Add results to query
        for doc, score in limited_results:
            search_query.add_result(doc, score)

        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        search_query.set_execution_time(execution_time)

        # 8. Save search query
        self._search_query_repository.save(search_query)

        # 9. Build response
        response = self._build_response(request.query, limited_results, execution_time)

        # 10. Cache results (5-minute TTL)
        self._cache_provider.set(cache_key, response, ttl=300)

        # 11. Publish SearchExecuted event
        event = SearchExecuted(
            query_id=query_id,
            query_text=request.query,
            user_id=user_id,
            result_count=len(limited_results),
            execution_time=execution_time,
        )
        self._event_publisher.publish(event)

        return response

    def _build_filters(self, request: SearchDocumentsRequest) -> SearchFilters:
        """Build search filters from request."""
        sources = [Source(s) for s in request.sources] if request.sources else []
        doc_types = [DocType(t) for t in request.document_types] if request.document_types else []
        formats = [DocFormat(f) for f in request.formats] if request.formats else []
        access_levels = [AccessLevel(a) for a in request.access_levels] if request.access_levels else []

        return SearchFilters(sources=sources, document_types=doc_types, formats=formats, access_levels=access_levels)

    def _build_response(self, query: str, scored_documents: List, execution_time: int) -> SearchResultsResponse:
        """Build search results response."""
        doc_responses = []

        for doc, score in scored_documents:
            metadata_response = None
            if doc.metadata:
                metadata_response = DocumentMetadataResponse(
                    author=doc.metadata.author,
                    created_at=doc.metadata.created_at,
                    last_modified=doc.metadata.last_modified,
                    file_size=doc.metadata.file_size,
                    tags=doc.metadata.tags,
                    category=doc.metadata.category,
                )

            doc_response = DocumentResponse(
                id=str(doc.document_id),
                title=str(doc.title),
                url=str(doc.url),
                source=str(doc.source.value.value),
                platform_id=doc.source.platform_id,
                document_type=str(doc.document_type.value.value),
                format=str(doc.format.value.value),
                access_level=str(doc.access_level.value.value),
                snippet=doc.snippet,
                relevance_score=score.value,
                metadata=metadata_response,
                last_modified=doc.last_modified,
                access_count=doc.access_count,
            )
            doc_responses.append(doc_response)

        return SearchResultsResponse(
            query=query, total_results=len(doc_responses), results=doc_responses, execution_time_ms=execution_time
        )
