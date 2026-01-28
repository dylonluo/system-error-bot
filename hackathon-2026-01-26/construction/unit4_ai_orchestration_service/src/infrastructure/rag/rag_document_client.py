"""RAG-enabled document client that retrieves actual document content from S3.

Supports multiple file formats:
- PDF files (.pdf) - extracted using pypdf
- Markdown files (.md) - read directly as plain text
- Text files (.txt) - read directly as plain text

When both MD and PDF versions exist for the same document, MD is preferred
for better text quality.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
import re
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
    """Document client with RAG capabilities - extracts and searches document content.
    
    Supports PDF, Markdown, and plain text files from S3.
    Prefers Markdown over PDF when both exist for the same document.
    """

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
        """Index all supported documents from S3 (PDF, Markdown, Text).
        
        Prefers Markdown over PDF when both exist for the same document.
        """
        try:
            paginator = self._s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self._bucket_name, Prefix=self._prefix)
            
            # First pass: collect all files and group by base name
            all_files: Dict[str, Dict[str, dict]] = {}  # base_name -> {ext -> s3_obj}
            
            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    key_lower = key.lower()
                    
                    # Determine file type and base name
                    if key_lower.endswith('.pdf'):
                        base_name = self._get_base_name(key, '.pdf')
                        file_type = 'pdf'
                    elif key_lower.endswith('.md'):
                        base_name = self._get_base_name(key, '.md')
                        file_type = 'md'
                    elif key_lower.endswith('.markdown'):
                        base_name = self._get_base_name(key, '.markdown')
                        file_type = 'md'
                    elif key_lower.endswith('.txt'):
                        base_name = self._get_base_name(key, '.txt')
                        file_type = 'txt'
                    else:
                        continue  # Skip unsupported files
                    
                    if base_name not in all_files:
                        all_files[base_name] = {}
                    all_files[base_name][file_type] = {'key': key, 'obj': obj}
            
            # Second pass: index files, preferring MD > TXT > PDF
            file_counts = {'pdf': 0, 'md': 0, 'txt': 0, 'skipped': 0}
            indexed_count = 0
            
            for base_name, formats in all_files.items():
                # Priority: md > txt > pdf
                if 'md' in formats:
                    chosen = formats['md']
                    file_type = 'md'
                    if 'pdf' in formats:
                        file_counts['skipped'] += 1
                        print(f"[RAG Client] Skipping PDF (MD exists): {formats['pdf']['key']}")
                elif 'txt' in formats:
                    chosen = formats['txt']
                    file_type = 'txt'
                    if 'pdf' in formats:
                        file_counts['skipped'] += 1
                        print(f"[RAG Client] Skipping PDF (TXT exists): {formats['pdf']['key']}")
                else:
                    chosen = formats['pdf']
                    file_type = 'pdf'
                
                file_counts[file_type] += 1
                if self._index_single_document(chosen['key'], chosen['obj'], file_type):
                    indexed_count += 1
            
            total_files = file_counts['pdf'] + file_counts['md'] + file_counts['txt']
            stats = self._content_store.get_stats()
            print(f"[RAG Client] Indexed {indexed_count}/{total_files} files")
            print(f"[RAG Client] File types: {file_counts['pdf']} PDFs, {file_counts['md']} Markdown, {file_counts['txt']} Text")
            if file_counts['skipped'] > 0:
                print(f"[RAG Client] Skipped {file_counts['skipped']} duplicate PDFs (MD/TXT preferred)")
            print(f"[RAG Client] Total chunks: {stats['total_chunks']}")
            
        except ClientError as e:
            print(f"[RAG Client] Error listing S3 objects: {e}")

    def _get_base_name(self, key: str, extension: str) -> str:
        """Extract base name from S3 key for deduplication.
        
        Removes extension and common suffixes like date stamps.
        Example: 'path/NS-Invoice-Guide-270126-071806.pdf' -> 'path/ns-invoice-guide'
        """
        # Remove extension (case-insensitive)
        base = re.sub(re.escape(extension) + '$', '', key, flags=re.IGNORECASE)
        
        # Remove common date suffixes like -270126-071806
        base = re.sub(r'-\d{6}-\d{6}$', '', base)
        
        # Normalize to lowercase for comparison
        return base.lower().strip()

    def _index_single_document(self, key: str, s3_obj: dict, file_type: str) -> bool:
        """Download and index a single document (PDF, MD, or TXT)."""
        doc_id = key  # Use S3 key as document ID
        
        if self._content_store.is_indexed(doc_id):
            return True
        
        try:
            # Download file
            response = self._s3_client.get_object(Bucket=self._bucket_name, Key=key)
            file_bytes = response['Body'].read()
            
            # Extract text based on file type
            if file_type == 'pdf':
                full_text = self._pdf_extractor.extract_full_text(file_bytes)
            else:
                # Markdown and text files - decode directly
                full_text = self._extract_text_file(file_bytes)
            
            if not full_text.strip():
                print(f"[RAG Client] No text extracted from: {key}")
                return False
            
            # Parse metadata from filename
            filename = key.replace(self._prefix, '')
            title, tags, category = self._parse_filename(filename, file_type)
            
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
                'file_type': file_type,
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
            
            print(f"[RAG Client] Indexed [{file_type.upper()}]: {title} ({chunk_count} chunks)")
            return True
            
        except Exception as e:
            print(f"[RAG Client] Error indexing {key}: {e}")
            return False

    def _extract_text_file(self, file_bytes: bytes) -> str:
        """Extract text from markdown or plain text files."""
        # Try common encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                text = file_bytes.decode(encoding)
                # Clean up the text
                text = self._clean_markdown(text)
                return text
            except UnicodeDecodeError:
                continue
        
        # Last resort - decode with errors ignored
        return file_bytes.decode('utf-8', errors='ignore')

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown text for better indexing."""
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove image references but keep alt text
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        
        # Convert links to just text [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove code block markers but keep content
        text = re.sub(r'```\w*\n?', '\n', text)
        
        # Remove inline code backticks
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    def _parse_filename(self, filename: str, file_type: str = 'pdf') -> tuple:
        """Parse document metadata from filename."""
        # Remove extension and date suffix based on file type
        if file_type == 'pdf':
            name = re.sub(r'-\d{6}-\d{6}\.pdf$', '', filename, flags=re.IGNORECASE)
            name = re.sub(r'\.pdf$', '', name, flags=re.IGNORECASE)
        elif file_type == 'md':
            name = re.sub(r'\.(md|markdown)$', '', filename, flags=re.IGNORECASE)
        else:  # txt
            name = re.sub(r'\.txt$', '', filename, flags=re.IGNORECASE)
        
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
        
        # Clean up title
        title = re.sub(r'\.(pdf|md|markdown|txt)$', '', name.strip(), flags=re.IGNORECASE)
        title = title or filename
        
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
                description = top_chunk.content[:200] + "..." if len(top_chunk.content) > 200 else top_chunk.content
            
            links.append(DocumentLink(
                document_id=doc_id,
                title=metadata.get('title', doc_id),
                url=metadata.get('url', ''),
                description=description,
                category=metadata.get('category', 'General'),
                relevance=min(score / 20.0, 1.0),
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
