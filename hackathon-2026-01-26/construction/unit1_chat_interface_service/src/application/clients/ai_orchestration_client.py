"""AI Orchestration Context client (mock)"""
from dataclasses import dataclass
from typing import List
from uuid import UUID


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
    """Mock client for AI Orchestration Context"""

    def process_query(self, query: str, context: str, user_id: UUID) -> AIResponse:
        """Process user query and return AI response"""
        # Mock implementation with realistic-looking response
        mock_links = [
            AIDocumentationLink(
                title="AWS S3 Getting Started Guide",
                url="https://docs.aws.amazon.com/s3/getting-started",
                description="Learn how to create your first S3 bucket and upload objects",
                source="s3",
                format="webpage",
                relevance=0.95
            ),
            AIDocumentationLink(
                title="S3 Best Practices",
                url="https://confluence.example.com/s3-best-practices",
                description="Internal guide for S3 usage patterns and optimization",
                source="confluence",
                format="webpage",
                relevance=0.87
            ),
            AIDocumentationLink(
                title="S3 Security Configuration",
                url="https://docs.aws.amazon.com/s3/security.pdf",
                description="Comprehensive guide to securing your S3 buckets",
                source="s3",
                format="pdf",
                relevance=0.82
            )
        ]

        return AIResponse(
            content=f"Based on your query '{query[:50]}...', here's what I found:\n\n"
                   f"Amazon S3 (Simple Storage Service) is an object storage service that offers "
                   f"industry-leading scalability, data availability, security, and performance. "
                   f"To get started, you'll need to create a bucket and configure appropriate permissions. "
                   f"I've included relevant documentation links below that cover setup, best practices, "
                   f"and security considerations.",
            documentation_links=mock_links,
            confidence=0.92
        )
