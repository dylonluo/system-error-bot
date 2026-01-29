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
        "I'm sorry, but I can only assist with NetSuite and TMS-related questions at this time. "
        "This includes topics like:\n\n"
        "• Invoice and billing issues\n"
        "• Order fulfillment and shipping\n"
        "• Sync errors between systems\n"
        "• Returns and RMA processing\n"
        "• System configuration and troubleshooting\n\n"
        "If you have a question about any of these topics, please feel free to ask!"
    )
    
    NO_DOCS_FOUND_MESSAGE = (
        "I searched through our documentation but couldn't find specific information related to your question. "
        "This could mean:\n\n"
        "• The topic might not be covered in our current documentation\n"
        "• The search terms might need to be more specific\n\n"
        "Please consider escalating this to the support team for further assistance."
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

    def generate_no_docs_response(self) -> Dict:
        """Generate response when no relevant documentation is found."""
        return {
            "content": self.NO_DOCS_FOUND_MESSAGE,
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
