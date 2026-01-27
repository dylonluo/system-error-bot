"""DocumentSearchService domain service."""

from typing import List

from .relevance_ranking_service import RelevanceRankingService


class DocumentSearchService:
    """Service for orchestrating document search across sources."""

    def __init__(self, s3_adapter, ranking_service: RelevanceRankingService):
        self._s3_adapter = s3_adapter
        self._ranking_service = ranking_service

    def search(self, query_text: str, filters, user_id: str) -> List:
        """Search documents across all sources."""
        all_documents = []

        # Search S3 (focus on S3 only as per requirements)
        if self._s3_adapter and self._s3_adapter.is_available():
            s3_results = self.search_s3(query_text)
            all_documents.extend(s3_results)

        # Merge and deduplicate results
        merged_documents = self.merge_results(all_documents)

        # Apply filters
        filtered_documents = [doc for doc in merged_documents if filters.matches(doc)]

        # Rank by relevance
        ranked_results = self.rank_by_relevance(filtered_documents, query_text)

        return ranked_results

    def search_s3(self, query_text: str) -> List:
        """Search documents in S3."""
        try:
            return self._s3_adapter.search(query_text)
        except Exception as e:
            print(f"S3 search failed: {e}")
            return []

    def merge_results(self, documents: List) -> List:
        """Merge and deduplicate results from multiple sources."""
        # Use URL as unique identifier
        seen_urls = set()
        merged = []

        for doc in documents:
            url_str = str(doc.url)
            if url_str not in seen_urls:
                seen_urls.add(url_str)
                merged.append(doc)

        return merged

    def rank_by_relevance(self, documents: List, query: str) -> List:
        """Rank documents by relevance score."""
        # Calculate relevance for each document
        scored_docs = []
        for doc in documents:
            score = self._ranking_service.calculate_relevance(doc, query)
            scored_docs.append((doc, score))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1].value, reverse=True)

        # Return documents with scores
        return scored_docs
