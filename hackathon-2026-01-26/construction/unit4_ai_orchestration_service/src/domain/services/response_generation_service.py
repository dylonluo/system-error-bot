from dataclasses import dataclass
from typing import List, Dict
from ..value_objects import AIResponse


@dataclass
class DocumentLink:
    """A documentation link."""
    document_id: str
    title: str
    url: str
    description: str
    category: str
    relevance: float


class ResponseGenerationService:
    """Generates final response with documentation links."""

    MAX_LINKS = 5
    OFF_TOPIC_MESSAGE = (
        "I can only help with NetSuite and TMS-related questions. "
        "For other topics, please contact general support."
    )

    def generate_response(
        self,
        ai_response: AIResponse,
        documents: List[DocumentLink],
    ) -> Dict:
        """Generate final response with formatted links."""
        limited_docs = self._limit_links(documents)
        grouped_docs = self._group_by_category(limited_docs)
        
        return {
            "content": ai_response.content,
            "documentation_links": [
                {
                    "title": doc.title,
                    "url": doc.url,
                    "description": doc.description,
                    "category": doc.category,
                    "relevance": doc.relevance,  # Include actual relevance score
                }
                for doc in limited_docs
            ],
            "links_by_category": grouped_docs,
        }

    def generate_off_topic_response(self) -> Dict:
        """Generate response for off-topic queries."""
        return {
            "content": self.OFF_TOPIC_MESSAGE,
            "documentation_links": [],
            "links_by_category": {},
        }

    def _limit_links(self, documents: List[DocumentLink]) -> List[DocumentLink]:
        """Limit to top N most relevant links."""
        sorted_docs = sorted(documents, key=lambda d: d.relevance, reverse=True)
        return sorted_docs[:self.MAX_LINKS]

    def _group_by_category(self, documents: List[DocumentLink]) -> Dict[str, List[Dict]]:
        """Group links by category."""
        grouped: Dict[str, List[Dict]] = {}
        for doc in documents:
            if doc.category not in grouped:
                grouped[doc.category] = []
            grouped[doc.category].append({
                "title": doc.title,
                "url": doc.url,
            })
        return grouped
