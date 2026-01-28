"""AI Orchestration Service client (Unit 4)"""
import requests
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from .document_repository_client import DocumentRepositoryClient, DocumentResult


@dataclass
class AIDocumentationLink:
    """Documentation link from AI"""
    title: str
    url: str
    description: str
    source: str
    format: str
    relevance: float


@dataclass
class AIResponse:
    """AI response model"""
    content: str
    documentation_links: List[AIDocumentationLink]
    confidence: float


class AIOrchestrationClient:
    """Client for AI Orchestration Service (Unit 4)
    
    This client:
    1. Calls Unit 4 for AI-powered responses (with Bedrock/Claude)
    2. Falls back to Unit 3 document search if Unit 4 unavailable
    """

    def __init__(self, unit4_url: str = "http://localhost:8003"):
        self._unit4_url = unit4_url
        self._unit4_available = False
        self._doc_client = DocumentRepositoryClient()
        self._check_unit4_availability()

    def _check_unit4_availability(self):
        """Check if Unit 4 is available."""
        try:
            response = requests.get(f"{self._unit4_url}/health", timeout=2)
            self._unit4_available = response.status_code == 200
            if self._unit4_available:
                print(f"[AI Client] Connected to Unit 4 (AI Orchestration) at {self._unit4_url}")
            else:
                print(f"[AI Client] Unit 4 not available, will use fallback")
        except Exception as e:
            print(f"[AI Client] Unit 4 not available: {e}, will use fallback")
            self._unit4_available = False

    def process_query(self, query: str, context: str, user_id: UUID, conversation_id: UUID = None) -> AIResponse:
        """Process user query using Unit 4 or fallback.
        
        Args:
            query: The user's question
            context: Previous conversation context (messages)
            user_id: The user's ID
            conversation_id: The conversation ID (important for follow-ups!)
        """
        # Try Unit 4 first
        if self._unit4_available:
            result = self._call_unit4(query, str(user_id), context, conversation_id)
            if result:
                return result
        
        # Fallback: Use Unit 3 for documents + generate simple response
        return self._fallback_response(query)

    def _call_unit4(self, query: str, user_id: str, context: str, conversation_id: UUID = None) -> Optional[AIResponse]:
        """Call Unit 4 AI Orchestration Service."""
        try:
            import uuid
            # Use provided conversation_id or generate new one
            conv_id = str(conversation_id) if conversation_id else str(uuid.uuid4())
            
            print(f"[AI Client] Calling Unit 4 with query: {query[:50]}...")
            print(f"[AI Client] Conversation ID: {conv_id}")
            
            # Build request with context
            request_data = {
                "query": query,
                "user_id": user_id,
                "conversation_id": conv_id,
            }
            
            # Include conversation context if provided
            if context and context.strip():
                request_data["context"] = context
                print(f"[AI Client] Including context: {len(context)} chars")
            
            response = requests.post(
                f"{self._unit4_url}/api/v1/ai/process-query",
                json=request_data,
                timeout=60  # Increased timeout - AI + RAG can take time
            )

            if response.status_code != 200:
                print(f"[AI Client] Unit 4 returned {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            print(f"[AI Client] Unit 4 response received, confidence: {data.get('confidence', 0)}")
            
            # Convert response
            doc_links = [
                AIDocumentationLink(
                    title=link.get("title", ""),
                    url=link.get("url", ""),
                    description=link.get("description", ""),
                    source="s3",
                    format="pdf",
                    relevance=link.get("relevance", 0.5)  # Use actual relevance from Unit 4
                )
                for link in data.get("documentation_links", [])
            ]

            return AIResponse(
                content=data.get("response", ""),
                documentation_links=doc_links,
                confidence=data.get("confidence", 0.5)
            )

        except requests.Timeout:
            print("[AI Client] Unit 4 request timed out after 60s")
            return None
        except Exception as e:
            print(f"[AI Client] Error calling Unit 4: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _fallback_response(self, query: str) -> AIResponse:
        """Fallback response using Unit 3 documents."""
        query_lower = query.lower()
        
        # Search for documents using Unit 3
        doc_results = self._doc_client.search_documents(query, limit=5)
        
        if doc_results:
            return self._build_response_with_docs(query, doc_results)
        
        # Check if on-topic
        if self._is_on_topic(query_lower):
            return self._build_no_results_response(query)
        else:
            return self._off_topic_response()

    def _build_response_with_docs(self, query: str, docs: List[DocumentResult]) -> AIResponse:
        """Build response with documents from Unit 3."""
        doc_links = [
            AIDocumentationLink(
                title=doc.title,
                url=doc.url,
                description=doc.snippet,
                source=doc.source,
                format=doc.format,
                relevance=doc.relevance_score
            )
            for doc in docs
        ]
        
        categories = [doc.category for doc in docs if doc.category]
        primary_category = categories[0] if categories else "General"
        
        response_content = self._generate_response_content(query, primary_category, len(docs))
        
        return AIResponse(
            content=response_content,
            documentation_links=doc_links,
            confidence=0.7
        )

    def _generate_response_content(self, query: str, category: str, doc_count: int) -> str:
        """Generate contextual response."""
        category_intros = {
            "Returns": "I found documentation related to Return Merchandise Authorization (RMA) and returns processes.",
            "NetSuite": "I found NetSuite documentation that should help with your query.",
            "NetSuite Issues": "I found troubleshooting documentation for NetSuite issues.",
            "TMS Integration": "I found documentation related to TMS integration.",
            "Billing": "I found documentation related to invoicing and billing.",
            "Sales": "I found documentation related to Sales Order management.",
            "Fulfillment": "I found documentation related to fulfillment and shipping.",
            "General": "I found relevant documentation for your query.",
        }
        
        intro = category_intros.get(category, category_intros["General"])
        
        response = f"{intro}\n\n"
        response += f"Based on your question, I've found {doc_count} relevant document{'s' if doc_count > 1 else ''}.\n\n"
        response += "Please review the documentation links below for detailed information.\n\n"
        response += "If these don't fully address your question, you can ask a follow-up or escalate to human support."
        
        return response

    def _build_no_results_response(self, query: str) -> AIResponse:
        """Response when no documents found."""
        return AIResponse(
            content=f"I couldn't find specific documentation for '{query[:50]}'. Try rephrasing or escalate to human support.",
            documentation_links=[],
            confidence=0.3
        )

    def _is_on_topic(self, query: str) -> bool:
        """Check if query is on-topic."""
        keywords = ["netsuite", "tms", "order", "invoice", "shipment", "rma", "return", "sync", "error", "sales", "fulfillment"]
        return any(kw in query for kw in keywords)

    def _off_topic_response(self) -> AIResponse:
        """Response for off-topic queries."""
        return AIResponse(
            content="I can only help with NetSuite, TMS, and their integrations. Please rephrase your question or escalate to human support.",
            documentation_links=[],
            confidence=0.2
        )
