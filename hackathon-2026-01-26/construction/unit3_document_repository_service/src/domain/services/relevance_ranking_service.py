"""RelevanceRankingService domain service."""

from typing import List

from ..value_objects.relevance_score import RelevanceScore


class RelevanceRankingService:
    """Service for calculating document relevance scores."""

    def calculate_relevance(self, document, query: str) -> RelevanceScore:
        """Calculate relevance score for a document given a query."""
        query_lower = query.lower()
        title_lower = str(document.title).lower()
        snippet_lower = document.snippet.lower()

        # Extract keywords from query
        keywords = self.extract_keywords(query)

        # Calculate component scores
        keyword_score = self.score_keyword_match(document, keywords)
        recency_score = self.score_recency(document)
        popularity_score = self.score_popularity(document)

        # Weighted combination (60% keyword, 20% recency, 20% popularity)
        final_score = keyword_score * 0.6 + recency_score * 0.2 + popularity_score * 0.2

        # Bonus for exact title match
        if query_lower in title_lower:
            final_score = min(final_score + 0.2, 1.0)

        return RelevanceScore(final_score)

    def extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple tokenization (split by spaces, lowercase)
        keywords = query.lower().split()
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        return keywords

    def score_keyword_match(self, document, keywords: List[str]) -> float:
        """Score based on keyword matches."""
        if not keywords:
            return 0.0

        title_lower = str(document.title).lower()
        snippet_lower = document.snippet.lower()

        matches = 0
        for keyword in keywords:
            if keyword in title_lower:
                matches += 2  # Title matches worth more
            elif keyword in snippet_lower:
                matches += 1

        # Normalize by number of keywords
        max_possible = len(keywords) * 2
        return min(matches / max_possible, 1.0) if max_possible > 0 else 0.0

    def score_recency(self, document) -> float:
        """Score based on document recency."""
        if not document.metadata:
            return 0.5  # Default score

        if document.metadata.is_recent(30):
            return 1.0
        elif document.metadata.is_recent(90):
            return 0.7
        elif document.metadata.is_recent(180):
            return 0.4
        else:
            return 0.2

    def score_popularity(self, document) -> float:
        """Score based on document popularity (access count)."""
        access_count = document.access_count

        # Logarithmic scaling
        if access_count == 0:
            return 0.0
        elif access_count < 10:
            return 0.3
        elif access_count < 50:
            return 0.6
        elif access_count < 100:
            return 0.8
        else:
            return 1.0
