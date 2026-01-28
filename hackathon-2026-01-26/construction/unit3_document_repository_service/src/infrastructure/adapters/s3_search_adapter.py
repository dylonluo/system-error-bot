"""Real S3 search adapter connecting to AWS S3 bucket."""

import io
import re
from datetime import datetime, timezone
from typing import List, Optional, Dict
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ...domain.aggregates.document import Document
from ...domain.ports.document_search_provider import IDocumentSearchProvider
from ...domain.value_objects.document_access_level import (
    AccessLevel,
    DocumentAccessLevel,
)
from ...domain.value_objects.document_format import DocFormat, DocumentFormat
from ...domain.value_objects.document_id import DocumentId
from ...domain.value_objects.document_metadata import DocumentMetadata
from ...domain.value_objects.document_source import DocumentSource, Source
from ...domain.value_objects.document_title import DocumentTitle
from ...domain.value_objects.document_type import DocType, DocumentType
from ...domain.value_objects.document_url import DocumentUrl

# PDF extraction
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[S3 Adapter] pypdf not installed, PDF content extraction disabled")


class S3SearchAdapter(IDocumentSearchProvider):
    """Real S3 adapter for document search from AWS S3 bucket."""

    def __init__(
        self,
        bucket_name: str = "cslr-hackathon-sg-test",
        prefix: str = "Byte-Us-Rawr/PDF/",
        region: str = "ap-southeast-1"
    ):
        self._bucket_name = bucket_name
        self._prefix = prefix
        self._region = region
        self._s3_client = None
        self._documents: Dict[str, Document] = {}
        self._document_keys: Dict[str, str] = {}  # Map document_id to S3 key
        self._content_cache: Dict[str, str] = {}  # Cache extracted content
        self._available = False
        self._initialize()

    def _initialize(self):
        """Initialize S3 client and load documents."""
        try:
            self._s3_client = boto3.client('s3', region_name=self._region)
            self._load_documents_from_s3()
            self._available = True
            print(f"[S3 Adapter] Connected to s3://{self._bucket_name}/{self._prefix}")
            print(f"[S3 Adapter] Loaded {len(self._documents)} documents")
        except NoCredentialsError:
            print("[S3 Adapter] AWS credentials not found. Using mock data.")
            self._available = False
        except Exception as e:
            print(f"[S3 Adapter] Error initializing: {e}")
            self._available = False

    def _load_documents_from_s3(self):
        """Load document metadata from S3 bucket."""
        try:
            paginator = self._s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self._bucket_name, Prefix=self._prefix)

            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if key.endswith('.pdf'):
                        doc = self._create_document_from_s3_object(obj)
                        if doc:
                            doc_id = str(doc.document_id)
                            self._documents[doc_id] = doc
                            self._document_keys[doc_id] = key  # Store S3 key

        except ClientError as e:
            print(f"[S3 Adapter] Error listing objects: {e}")
            raise

    def _create_document_from_s3_object(self, s3_object: dict) -> Optional[Document]:
        """Create a Document from S3 object metadata."""
        key = s3_object['Key']
        filename = key.replace(self._prefix, '')
        
        if not filename or filename.startswith('.'):
            return None

        # Parse document info from filename
        title, doc_type, access_level, tags, category = self._parse_filename(filename)
        
        # Generate presigned URL (valid for 1 hour)
        try:
            url = self._s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': key},
                ExpiresIn=3600
            )
        except Exception:
            # Fallback to direct S3 URL
            url = f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{key}"

        # Create snippet from filename
        snippet = self._generate_snippet(title, tags)

        return Document(
            document_id=DocumentId.generate(),
            title=DocumentTitle(title),
            url=DocumentUrl(url),
            source=DocumentSource(Source.S3, self._bucket_name),
            document_type=DocumentType(doc_type),
            format=DocumentFormat(DocFormat.PDF),
            access_level=DocumentAccessLevel(access_level),
            snippet=snippet,
            metadata=DocumentMetadata(
                author="Castlery Team",
                created_at=s3_object.get('LastModified', datetime.now(timezone.utc)).replace(tzinfo=None),
                last_modified=s3_object.get('LastModified', datetime.now(timezone.utc)).replace(tzinfo=None),
                file_size=s3_object.get('Size', 0),
                tags=tags,
                category=category,
            ),
            access_count=0,
        )

    def _parse_filename(self, filename: str) -> tuple:
        """Parse document metadata from filename.
        
        Filename patterns:
        - NS-2024-03-15 Some Title-270126-071806.pdf -> NetSuite dated issue
        - NS-Sales Order-270126-084851.pdf -> NetSuite SOP
        - INV with partial set... -> Invoice related
        """
        # Remove .pdf extension and date suffix
        name = re.sub(r'-\d{6}-\d{6}\.pdf$', '', filename)
        name = re.sub(r'\.pdf$', '', name)
        
        # Determine category and type based on prefix
        tags = []
        category = "General"
        doc_type = DocType.GUIDE
        access_level = AccessLevel.BASIC
        
        # NetSuite documents
        if name.startswith('NS-'):
            name = name[3:]  # Remove NS- prefix
            tags.append("netsuite")
            category = "NetSuite"
            
            # Check for dated issues (troubleshooting docs)
            if re.match(r'\d{4}-\d{2}-\d{2}', name):
                doc_type = DocType.GUIDE
                tags.append("troubleshooting")
                tags.append("issue")
                category = "NetSuite Issues"
            # Check for SOPs
            elif any(kw in name.lower() for kw in ['sop', 'process', 'procedure']):
                doc_type = DocType.SOP
                tags.append("sop")
            # Check for PRDs
            elif any(kw in name.lower() for kw in ['prd', 'requirement', 'brd']):
                doc_type = DocType.PRD
                tags.append("prd")
                access_level = AccessLevel.ADVANCED
            else:
                doc_type = DocType.GUIDE
                tags.append("guide")
        
        # TMS documents
        if 'tms' in name.lower():
            tags.append("tms")
            tags.append("integration")
            category = "TMS Integration"
        
        # Invoice/Billing documents
        if any(kw in name.lower() for kw in ['invoice', 'bill', 'ap ', 'vendor bill']):
            tags.append("invoice")
            tags.append("billing")
            category = "Billing"
        
        # RMA/Returns documents
        if any(kw in name.lower() for kw in ['rma', 'return', 'refund']):
            tags.append("rma")
            tags.append("returns")
            category = "Returns"
        
        # Sales Order documents
        if 'sales order' in name.lower():
            tags.append("sales-order")
            category = "Sales"
        
        # Fulfillment documents
        if any(kw in name.lower() for kw in ['fulfillment', 'shipment', 'delivery']):
            tags.append("fulfillment")
            tags.append("shipping")
            category = "Fulfillment"
        
        # Sync/Integration documents
        if any(kw in name.lower() for kw in ['sync', 'integration', 'api']):
            tags.append("sync")
            tags.append("integration")
        
        # Error/Troubleshooting documents
        if any(kw in name.lower() for kw in ['error', 'issue', 'fail', 'unable']):
            tags.append("error")
            tags.append("troubleshooting")
        
        # Clean up title
        title = name.strip()
        if not title:
            title = filename.replace('.pdf', '')
        
        return title, doc_type, access_level, list(set(tags)), category

    def _generate_snippet(self, title: str, tags: List[str]) -> str:
        """Generate a descriptive snippet from title and tags."""
        tag_str = ", ".join(tags[:3]) if tags else "documentation"
        return f"Documentation about {title.lower()}. Related topics: {tag_str}."

    def search(self, query: str) -> List[Document]:
        """Search for documents matching the query."""
        if not self._available:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []
        scored_results = []

        for doc in self._documents.values():
            score = 0
            title_lower = str(doc.title).lower()
            snippet_lower = doc.snippet.lower()
            tags = [tag.lower() for tag in doc.metadata.tags]
            category_lower = doc.metadata.category.lower()

            # Title match (highest weight)
            for word in query_words:
                if len(word) > 2:  # Skip short words
                    if word in title_lower:
                        score += 3
                    if word in snippet_lower:
                        score += 1
                    if any(word in tag for tag in tags):
                        score += 2
                    if word in category_lower:
                        score += 1

            # Exact phrase match bonus
            if query_lower in title_lower:
                score += 5
            if query_lower in snippet_lower:
                score += 2

            if score > 0:
                scored_results.append((score, doc))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top 20 results
        return [doc for _, doc in scored_results[:20]]

    def get_document(self, document_id) -> Optional[Document]:
        """Get a specific document by ID."""
        doc_id_str = str(document_id)
        return self._documents.get(doc_id_str)

    def get_metadata(self, document_id) -> Optional[DocumentMetadata]:
        """Get metadata for a document."""
        doc = self.get_document(document_id)
        return doc.metadata if doc else None

    def is_available(self) -> bool:
        """Check if the provider is available."""
        return self._available

    def refresh_documents(self):
        """Refresh document list from S3."""
        self._documents.clear()
        self._load_documents_from_s3()

    def get_all_documents(self) -> List[Document]:
        """Get all loaded documents."""
        return list(self._documents.values())

    def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self._documents)

    def get_document_content(self, document_id: str, max_chars: int = 8000) -> Optional[str]:
        """Extract text content from a PDF document.
        
        Args:
            document_id: The document ID
            max_chars: Maximum characters to extract (default 8000 for context window)
            
        Returns:
            Extracted text content or None if extraction fails
        """
        if not PDF_AVAILABLE:
            print("[S3 Adapter] PDF extraction not available")
            return None
            
        # Check cache first
        if document_id in self._content_cache:
            return self._content_cache[document_id][:max_chars]
        
        # Get S3 key
        s3_key = self._document_keys.get(document_id)
        if not s3_key:
            print(f"[S3 Adapter] No S3 key found for document {document_id}")
            return None
        
        try:
            # Download PDF from S3
            print(f"[S3 Adapter] Downloading PDF: {s3_key}")
            response = self._s3_client.get_object(Bucket=self._bucket_name, Key=s3_key)
            pdf_bytes = response['Body'].read()
            
            # Extract text using pypdf
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
                except Exception as e:
                    print(f"[S3 Adapter] Error extracting page {page_num}: {e}")
                    continue
            
            content = "\n\n".join(text_parts)
            
            # Cache the content
            self._content_cache[document_id] = content
            print(f"[S3 Adapter] Extracted {len(content)} chars from {s3_key}")
            
            return content[:max_chars]
            
        except ClientError as e:
            print(f"[S3 Adapter] Error downloading PDF: {e}")
            return None
        except Exception as e:
            print(f"[S3 Adapter] Error extracting PDF content: {e}")
            return None

    def get_documents_content(self, document_ids: List[str], max_chars_per_doc: int = 4000) -> Dict[str, str]:
        """Extract content from multiple documents.
        
        Args:
            document_ids: List of document IDs
            max_chars_per_doc: Max chars per document
            
        Returns:
            Dict mapping document_id to content
        """
        results = {}
        for doc_id in document_ids[:3]:  # Limit to top 3 docs for context
            content = self.get_document_content(doc_id, max_chars_per_doc)
            if content:
                results[doc_id] = content
        return results
