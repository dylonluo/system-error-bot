"""Document content store for RAG - stores extracted text and enables semantic search."""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime


@dataclass
class DocumentChunk:
    """A chunk of document content for retrieval."""
    document_id: str
    document_title: str
    document_url: str
    chunk_index: int
    content: str
    tags: List[str] = field(default_factory=list)
    category: str = ""
    relevance_score: float = 0.0


class DocumentContentStore:
    """In-memory store for document content with keyword-based search.
    
    For production, this should be replaced with a vector database
    like Pinecone, FAISS, or OpenSearch with embeddings.
    """

    CHUNK_SIZE = 1000  # Characters per chunk
    CHUNK_OVERLAP = 200  # Overlap between chunks

    def __init__(self):
        self._chunks: Dict[str, List[DocumentChunk]] = {}  # doc_id -> chunks
        self._all_chunks: List[DocumentChunk] = []
        self._indexed_docs: Set[str] = set()

    def add_document(
        self,
        document_id: str,
        title: str,
        url: str,
        content: str,
        tags: List[str] = None,
        category: str = "",
    ) -> int:
        """Add a document's content to the store, chunked for retrieval."""
        if document_id in self._indexed_docs:
            return 0  # Already indexed

        chunks = self._chunk_content(content)
        doc_chunks = []

        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                document_title=title,
                document_url=url,
                chunk_index=i,
                content=chunk_text,
                tags=tags or [],
                category=category,
            )
            doc_chunks.append(chunk)
            self._all_chunks.append(chunk)

        self._chunks[document_id] = doc_chunks
        self._indexed_docs.add(document_id)
        
        return len(doc_chunks)

    def search(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """Search for relevant document chunks using keyword matching.
        
        For production, replace with vector similarity search.
        """
        query_lower = query.lower()
        query_words = set(self._tokenize(query_lower))
        
        scored_chunks = []
        
        for chunk in self._all_chunks:
            score = self._calculate_relevance(chunk, query_lower, query_words)
            if score > 0:
                chunk.relevance_score = score
                scored_chunks.append(chunk)
        
        # Sort by relevance and return top_k
        scored_chunks.sort(key=lambda c: c.relevance_score, reverse=True)
        return scored_chunks[:top_k]

    def _calculate_relevance(
        self, 
        chunk: DocumentChunk, 
        query_lower: str, 
        query_words: Set[str]
    ) -> float:
        """Calculate relevance score for a chunk."""
        score = 0.0
        content_lower = chunk.content.lower()
        title_lower = chunk.document_title.lower()
        
        # Exact phrase match in content (highest weight)
        if query_lower in content_lower:
            score += 10.0
        
        # Exact phrase match in title
        if query_lower in title_lower:
            score += 8.0
        
        # Word matches in content
        content_words = set(self._tokenize(content_lower))
        matching_words = query_words & content_words
        score += len(matching_words) * 2.0
        
        # Word matches in title
        title_words = set(self._tokenize(title_lower))
        title_matches = query_words & title_words
        score += len(title_matches) * 3.0
        
        # Tag matches
        chunk_tags = set(tag.lower() for tag in chunk.tags)
        tag_matches = query_words & chunk_tags
        score += len(tag_matches) * 4.0
        
        # Boost for specific keywords
        boost_keywords = {
            'error': 2.0, 'issue': 1.5, 'problem': 1.5,
            'netsuite': 2.0, 'tms': 2.0,
            'sync': 1.5, 'integration': 1.5,
            'invoice': 1.5, 'order': 1.5,
        }
        for keyword, boost in boost_keywords.items():
            if keyword in query_lower and keyword in content_lower:
                score += boost
        
        return score

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization - split on non-alphanumeric."""
        return [w for w in re.split(r'\W+', text) if len(w) > 2]

    def _chunk_content(self, content: str) -> List[str]:
        """Split content into overlapping chunks."""
        if len(content) <= self.CHUNK_SIZE:
            return [content] if content.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.CHUNK_SIZE
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence end within last 100 chars
                search_start = max(end - 100, start)
                last_period = content.rfind('.', search_start, end)
                if last_period > start:
                    end = last_period + 1
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.CHUNK_OVERLAP
            if start >= len(content):
                break
        
        return chunks

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a specific document."""
        return self._chunks.get(document_id, [])

    def is_indexed(self, document_id: str) -> bool:
        """Check if a document is already indexed."""
        return document_id in self._indexed_docs

    def get_stats(self) -> Dict:
        """Get store statistics."""
        return {
            "total_documents": len(self._indexed_docs),
            "total_chunks": len(self._all_chunks),
            "avg_chunks_per_doc": len(self._all_chunks) / max(len(self._indexed_docs), 1),
        }

    def clear(self):
        """Clear all stored content."""
        self._chunks.clear()
        self._all_chunks.clear()
        self._indexed_docs.clear()
