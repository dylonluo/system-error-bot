"""Document content store for RAG - stores extracted text and enables semantic search.

Uses sentence-transformers for vector embeddings and cosine similarity for search.
Falls back to keyword matching if sentence-transformers is not available.
"""

import re
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple


# Try to import sentence-transformers
EMBEDDINGS_AVAILABLE = False
_model = None

def _load_embedding_model():
    """Lazy load the embedding model."""
    global EMBEDDINGS_AVAILABLE, _model
    if _model is not None:
        return _model
    
    try:
        from sentence_transformers import SentenceTransformer
        # Use a lightweight but effective model
        # all-MiniLM-L6-v2: 384 dimensions, fast, good quality
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        EMBEDDINGS_AVAILABLE = True
        print("[ContentStore] Loaded sentence-transformers model: all-MiniLM-L6-v2")
        return _model
    except ImportError:
        print("[ContentStore] sentence-transformers not installed. Using keyword fallback.")
        print("[ContentStore] Install with: pip install sentence-transformers")
        EMBEDDINGS_AVAILABLE = False
        return None
    except Exception as e:
        print(f"[ContentStore] Error loading embedding model: {e}")
        EMBEDDINGS_AVAILABLE = False
        return None


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
    embedding: Optional[np.ndarray] = field(default=None, repr=False)


class DocumentContentStore:
    """In-memory store for document content with vector-based semantic search.
    
    Uses sentence-transformers to generate embeddings and cosine similarity
    for finding semantically similar content. Falls back to keyword matching
    if sentence-transformers is not available.
    """

    CHUNK_SIZE = 500  # Smaller chunks work better with embeddings
    CHUNK_OVERLAP = 100  # Overlap between chunks

    def __init__(self):
        self._chunks: Dict[str, List[DocumentChunk]] = {}  # doc_id -> chunks
        self._all_chunks: List[DocumentChunk] = []
        self._indexed_docs: Set[str] = set()
        self._embeddings_matrix: Optional[np.ndarray] = None  # For fast batch search
        self._model = _load_embedding_model()

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
            # Generate embedding for chunk
            embedding = self._generate_embedding(chunk_text, title, tags)
            
            chunk = DocumentChunk(
                document_id=document_id,
                document_title=title,
                document_url=url,
                chunk_index=i,
                content=chunk_text,
                tags=tags or [],
                category=category,
                embedding=embedding,
            )
            doc_chunks.append(chunk)
            self._all_chunks.append(chunk)

        self._chunks[document_id] = doc_chunks
        self._indexed_docs.add(document_id)
        
        # Rebuild embeddings matrix for fast search
        self._rebuild_embeddings_matrix()
        
        return len(doc_chunks)

    def _generate_embedding(
        self, 
        content: str, 
        title: str = "", 
        tags: List[str] = None
    ) -> Optional[np.ndarray]:
        """Generate embedding for a chunk of text."""
        if self._model is None:
            return None
        
        try:
            # Combine content with metadata for richer embedding
            # Title and tags provide important context
            tag_str = " ".join(tags) if tags else ""
            combined_text = f"{title}. {tag_str}. {content}"
            
            # Generate embedding
            embedding = self._model.encode(combined_text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"[ContentStore] Error generating embedding: {e}")
            return None

    def _rebuild_embeddings_matrix(self):
        """Rebuild the embeddings matrix for fast batch similarity search."""
        if not EMBEDDINGS_AVAILABLE:
            return
        
        embeddings = []
        for chunk in self._all_chunks:
            if chunk.embedding is not None:
                embeddings.append(chunk.embedding)
            else:
                # Create zero vector as placeholder
                embeddings.append(np.zeros(384))  # MiniLM dimension
        
        if embeddings:
            self._embeddings_matrix = np.vstack(embeddings)
            # Normalize for cosine similarity
            norms = np.linalg.norm(self._embeddings_matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            self._embeddings_matrix = self._embeddings_matrix / norms

    def search(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """Search for relevant document chunks using semantic similarity.
        
        Uses cosine similarity between query embedding and chunk embeddings.
        Falls back to keyword matching if embeddings are not available.
        """
        if EMBEDDINGS_AVAILABLE and self._model is not None and self._embeddings_matrix is not None:
            return self._semantic_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)

    def _semantic_search(self, query: str, top_k: int) -> List[DocumentChunk]:
        """Perform semantic search using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = self._model.encode(query, convert_to_numpy=True)
            
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm > 0:
                query_embedding = query_embedding / query_norm
            
            # Compute cosine similarities (dot product of normalized vectors)
            similarities = np.dot(self._embeddings_matrix, query_embedding)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Get more for filtering
            
            results = []
            seen_docs = set()
            
            for idx in top_indices:
                if len(results) >= top_k:
                    break
                    
                chunk = self._all_chunks[idx]
                score = float(similarities[idx])
                
                # Skip very low scores
                if score < 0.2:
                    continue
                
                # Create a copy with the relevance score
                result_chunk = DocumentChunk(
                    document_id=chunk.document_id,
                    document_title=chunk.document_title,
                    document_url=chunk.document_url,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    tags=chunk.tags,
                    category=chunk.category,
                    relevance_score=score,
                    embedding=None,  # Don't include embedding in results
                )
                results.append(result_chunk)
            
            print(f"[ContentStore] Semantic search found {len(results)} results for: {query[:50]}...")
            return results
            
        except Exception as e:
            print(f"[ContentStore] Semantic search error: {e}, falling back to keyword")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[DocumentChunk]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        query_words = set(self._tokenize(query_lower))
        
        scored_chunks = []
        
        for chunk in self._all_chunks:
            score = self._calculate_keyword_relevance(chunk, query_lower, query_words)
            if score > 0:
                result_chunk = DocumentChunk(
                    document_id=chunk.document_id,
                    document_title=chunk.document_title,
                    document_url=chunk.document_url,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    tags=chunk.tags,
                    category=chunk.category,
                    relevance_score=score / 20.0,  # Normalize to 0-1 range
                    embedding=None,
                )
                scored_chunks.append(result_chunk)
        
        scored_chunks.sort(key=lambda c: c.relevance_score, reverse=True)
        return scored_chunks[:top_k]

    def _calculate_keyword_relevance(
        self, 
        chunk: DocumentChunk, 
        query_lower: str, 
        query_words: Set[str]
    ) -> float:
        """Calculate keyword-based relevance score (fallback)."""
        score = 0.0
        content_lower = chunk.content.lower()
        title_lower = chunk.document_title.lower()
        
        if query_lower in content_lower:
            score += 10.0
        if query_lower in title_lower:
            score += 8.0
        
        content_words = set(self._tokenize(content_lower))
        matching_words = query_words & content_words
        score += len(matching_words) * 2.0
        
        title_words = set(self._tokenize(title_lower))
        title_matches = query_words & title_words
        score += len(title_matches) * 3.0
        
        chunk_tags = set(tag.lower() for tag in chunk.tags)
        tag_matches = query_words & chunk_tags
        score += len(tag_matches) * 4.0
        
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
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "embedding_dimensions": 384 if EMBEDDINGS_AVAILABLE else 0,
        }

    def clear(self):
        """Clear all stored content."""
        self._chunks.clear()
        self._all_chunks.clear()
        self._indexed_docs.clear()
        self._embeddings_matrix = None
