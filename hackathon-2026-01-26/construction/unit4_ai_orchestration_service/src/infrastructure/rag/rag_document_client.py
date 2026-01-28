"""RAG-enabled document client that retrieves actual document content from S3."""

from typing import List, Optional, Dict
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .pdf_extractor import PDFExtractor
from .document_content_store import DocumentContentStore, DocumentChunk
from ...domain.services.response_generation_service import DocumentLink
from ...application.clients import IDocumentSearchClient


@dataclass
class RAGSearchResult:
    """Search result with document content for RAG."""
    document_link: DocumentLink
    relevant_chunks: List[DocumentChunk]
    combined_context: str


class RAGDocumentClient(IDocumentSearchClient):
    """Document client with RAG capabilities - extracts and searches actual PDF content."""

    def __init__(
        self,
        bucket_name: str = "cslr-hackathon-sg-test",
        prefix: str = "Byte-Us-Rawr/PDF/",
        region: str = "ap-southeast-1",
    ):
        self._bucket_name = bucket_name
        self._prefix = prefix
        self._region = region
        self._s3_client = None
        self._pdf_extractor = PDFExtractor()
        self._content_store = DocumentContentStore()
        self._document_metadata: Dict[str, dict] = {}
        self._available = False
        self._initialize()

    def _initialize(self):
        """Initialize S3 client and index documents."""
        try:
            self._s3_client = boto3.client('s3', region_name=self._region)
            print(f"[RAG Client] Connecting to s3://{self._bucket_name}/{self._prefix}")
            self._index_documents()
            self._available = True
        except NoCredentialsError:
            print("[RAG Client] AWS credentials not found")
            self._available = False
        except Exception as e:
            print(f"[RAG Client] Error initializing: {e}")
            self._available = False

    def _index_documents(self):
        """Index all PDF documents from S3."""
        try:
            paginator = self._s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self._bucket_name, Prefix=self._prefix)
            
            pdf_count = 0
            indexed_count = 0
            
            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if key.lower().endswith('.pdf'):
                        pdf_count += 1
                        if self._index_single_document(key, obj):
                            indexed_count += 1
            
            stats = self._content_store.get_stats()
            print(f"[RAG Client] Indexed {indexed_count}/{pdf_count} PDFs")
            print(f"[RAG Client] Total chunks: {stats['total_chunks']}")
            
        except ClientError as e:
            print(f"[RAG Client] Error listing S3 objects: {e}")

    def _index_single_document(self, key: str, s3_obj: dict) -> bool:
        """Download and index a single PDF document."""
        doc_id = key  # Use S3 key as document ID
        
        if self._content_store.is_indexed(doc_id):
            return True
        
        try:
            # Download PDF
            response = self._s3_client.get_object(Bucket=self._bucket_name, Key=key)
            pdf_bytes = response['Body'].read()
            
            # Extract text
            full_text = self._pdf_extractor.extract_full_text(pdf_bytes)
            
            if not full_text.strip():
                print(f"[RAG Client] No text extracted from: {key}")
                return False
            
            # Parse metadata from filename
            filename = key.replace(self._prefix, '')
            title, tags, category = self._parse_filename(filename)
            
            # Generate presigned URL
            try:
                url = self._s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self._bucket_name, 'Key': key},
                    ExpiresIn=3600
                )
            except Exception:
                url = f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{key}"
            
            # Store metadata
            self._document_metadata[doc_id] = {
                'title': title,
                'url': url,
                'tags': tags,
                'category': category,
                'size': s3_obj.get('Size', 0),
            }
            
            # Add to content store
            chunk_count = self._content_store.add_document(
                document_id=doc_id,
                title=title,
                url=url,
                content=full_text,
                tags=tags,
                category=category,
            )
            
            print(f"[RAG Client] Indexed: {title} ({chunk_count} chunks)")
            return True
            
        except Exception as e:
            print(f"[RAG Client] Error indexing {key}: {e}")
            return False

    def _parse_filename(self, filename: str) -> tuple:
        """Parse document metadata from filename."""
        import re
        
        # Remove .pdf extension and date suffix
        name = re.sub(r'-\d{6}-\d{6}\.pdf$', '', filename)
        name = re.sub(r'\.pdf$', '', name)
        
        tags = []
        category = "General"
        
        # NetSuite documents
        if name.startswith('NS-'):
            name = name[3:]
            tags.append("netsuite")
            category = "NetSuite"
            
            if re.match(r'\d{4}-\d{2}-\d{2}', name):
                tags.extend(["troubleshooting", "issue"])
                category = "NetSuite Issues"
        
        # TMS documents
        if 'tms' in name.lower():
            tags.extend(["tms", "integration"])
            category = "TMS Integration"
        
        # Invoice/Billing
        if any(kw in name.lower() for kw in ['invoice', 'bill', 'ap ', 'vendor']):
            tags.extend(["invoice", "billing"])
            category = "Billing"
        
        # Sales Order
        if 'sales order' in name.lower():
            tags.append("sales-order")
            category = "Sales"
        
        # Fulfillment
        if any(kw in name.lower() for kw in ['fulfillment', 'shipment', 'delivery']):
            tags.extend(["fulfillment", "shipping"])
            category = "Fulfillment"
        
        # Error/Troubleshooting
        if any(kw in name.lower() for kw in ['error', 'issue', 'fail', 'unable']):
            tags.extend(["error", "troubleshooting"])
        
        title = name.strip() or filename.replace('.pdf', '')
        
        return title, list(set(tags)), category

    def search(self, query: str, filters: Optional[dict] = None) -> List[DocumentLink]:
        """Search for documents and return links with relevance scores."""
        if not self._available:
            return self._fallback_search(query)
        
        # Search content store for relevant chunks
        chunks = self._content_store.search(query, top_k=10)
        
        # Group chunks by document and create links
        doc_scores: Dict[str, float] = {}
        doc_chunks: Dict[str, List[DocumentChunk]] = {}
        
        for chunk in chunks:
            doc_id = chunk.document_id
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_chunks[doc_id] = []
            doc_scores[doc_id] += chunk.relevance_score
            doc_chunks[doc_id].append(chunk)
        
        # Sort by total score and create links
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        links = []
        for doc_id, score in sorted_docs[:5]:  # Top 5 documents
            metadata = self._document_metadata.get(doc_id, {})
            
            # Create description from top chunk
            top_chunk = doc_chunks[doc_id][0] if doc_chunks[doc_id] else None
            description = ""
            if top_chunk:
                # Take first 200 chars of most relevant chunk
                description = top_chunk.content[:200] + "..." if len(top_chunk.content) > 200 else top_chunk.content
            
            links.append(DocumentLink(
                document_id=doc_id,
                title=metadata.get('title', doc_id),
                url=metadata.get('url', ''),
                description=description,
                category=metadata.get('category', 'General'),
                relevance=min(score / 20.0, 1.0),  # Normalize score
            ))
        
        return links

    def search_with_context(self, query: str, top_k: int = 5) -> List[RAGSearchResult]:
        """Search and return results with full context for RAG."""
        if not self._available:
            return []
        
        chunks = self._content_store.search(query, top_k=top_k * 2)
        
        # Group by document
        doc_chunks: Dict[str, List[DocumentChunk]] = {}
        for chunk in chunks:
            doc_id = chunk.document_id
            if doc_id not in doc_chunks:
                doc_chunks[doc_id] = []
            doc_chunks[doc_id].append(chunk)
        
        results = []
        for doc_id, chunks_list in list(doc_chunks.items())[:top_k]:
            metadata = self._document_metadata.get(doc_id, {})
            
            # Combine chunks into context
            combined = "\n\n".join(c.content for c in chunks_list[:3])
            
            link = DocumentLink(
                document_id=doc_id,
                title=metadata.get('title', doc_id),
                url=metadata.get('url', ''),
                description=combined[:200] + "..." if len(combined) > 200 else combined,
                category=metadata.get('category', 'General'),
                relevance=chunks_list[0].relevance_score / 20.0 if chunks_list else 0,
            )
            
            results.append(RAGSearchResult(
                document_link=link,
                relevant_chunks=chunks_list,
                combined_context=combined,
            ))
        
        return results

    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """Get combined document context for a query, suitable for prompt injection."""
        results = self.search_with_context(query, top_k=3)
        
        if not results:
            return ""
        
        context_parts = []
        total_chars = 0
        char_limit = max_tokens * 4  # Rough estimate: 4 chars per token
        
        for result in results:
            if total_chars >= char_limit:
                break
            
            doc_context = f"[From: {result.document_link.title}]\n{result.combined_context}"
            
            if total_chars + len(doc_context) > char_limit:
                # Truncate to fit
                remaining = char_limit - total_chars
                doc_context = doc_context[:remaining] + "..."
            
            context_parts.append(doc_context)
            total_chars += len(doc_context)
        
        return "\n\n---\n\n".join(context_parts)

    def _fallback_search(self, query: str) -> List[DocumentLink]:
        """Fallback when S3 is not available."""
        from uuid import uuid4
        return [
            DocumentLink(
                document_id=str(uuid4()),
                title="Documentation Unavailable",
                url="",
                description="Unable to search documents. Please try again later.",
                category="Error",
                relevance=0.0,
            )
        ]

    def is_available(self) -> bool:
        """Check if the client is available."""
        return self._available

    def get_stats(self) -> Dict:
        """Get indexing statistics."""
        return {
            "available": self._available,
            "documents_indexed": len(self._document_metadata),
            **self._content_store.get_stats(),
        }
