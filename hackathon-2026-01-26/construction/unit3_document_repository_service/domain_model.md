# Domain Model - Unit 3: Document Repository Service

## Document Information
**Bounded Context:** Document Repository Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Technology:** Python/JavaScript  
**Database Schema:** `document_repository`

---

## Bounded Context Definition

**Purpose:** Search and retrieve documentation from external sources (S3, Confluence) and manage document metadata.

**Responsibilities:**
- Search documents across multiple platforms (S3, Confluence)
- Generate document links with metadata
- Rank search results by relevance
- Cache document metadata for performance
- Track document access patterns

**What This Context Does NOT Do:**
- Enforce user permissions (delegates to Access Control Context)
- Process AI queries (consumed by AI Orchestration Context)
- Store actual document content (documents live in external systems)

---

## Aggregates

### 1. Document (Aggregate Root)

**Description:** Represents a piece of documentation with its metadata and access information.

**Aggregate Root:** Document

**Entities:**
- Document (root)
- DocumentVersion (for tracking updates)

**Value Objects:**
- DocumentId
- DocumentTitle
- DocumentUrl
- DocumentAccessLevel
- DocumentType
- DocumentFormat
- DocumentSource
- RelevanceScore

**Invariants:**
- A document must have a valid URL
- A document must have a source (S3 or Confluence)
- A document must have an access level
- Document URL must be unique within a source
- Document metadata must be refreshed periodically

**Lifecycle:**
- Discovered during search from external systems
- Metadata cached in local database
- Updated when external document changes
- Marked as stale if not accessed for 90 days

---

### 2. SearchQuery (Aggregate Root)

**Description:** Represents a document search request with its parameters and results.

**Aggregate Root:** SearchQuery

**Entities:**
- SearchQuery (root)
- SearchResult (entity)

**Value Objects:**
- QueryId
- QueryText
- SearchFilters
- RelevanceScore

**Invariants:**
- Query text must not be empty
- Search results are ordered by relevance
- Maximum 50 results per query
- Results are cached for 5 minutes

**Lifecycle:**
- Created when search is requested
- Executed against external systems
- Results cached temporarily
- Logged for analytics

---

## Entities

### Document (Aggregate Root)

**Identity:** DocumentId (UUID)

**Attributes:**
- documentId: DocumentId
- title: DocumentTitle
- url: DocumentUrl
- source: DocumentSource (s3, confluence)
- documentType: DocumentType (sop, prd, guide)
- format: DocumentFormat (webpage, pdf)
- accessLevel: DocumentAccessLevel (public, basic, advanced)
- snippet: String (preview text)
- metadata: DocumentMetadata
- lastModified: Timestamp
- lastAccessed: Timestamp
- accessCount: Integer
- isStale: Boolean

**Behaviors:**
- updateMetadata(metadata): void
- markAsAccessed(): void
- isAccessibleBy(userAccessLevel): Boolean
- calculateRelevance(query): RelevanceScore
- refreshFromSource(): void
- markAsStale(): void

**Business Rules:**
- URL must be valid and accessible
- Metadata refreshed when document is accessed and older than 24 hours
- Documents not accessed for 90 days marked as stale
- Access count incremented on each retrieval
- Snippet limited to 200 characters

---

### DocumentVersion (Entity within Document)

**Identity:** VersionId (UUID)

**Attributes:**
- versionId: VersionId
- documentId: DocumentId
- versionNumber: Integer
- modifiedAt: Timestamp
- modifiedBy: String
- changeDescription: String

**Behaviors:**
- isLatest(): Boolean
- getChangesSince(version): String

**Business Rules:**
- Version number auto-incremented
- Latest version is the active one
- Version history retained for audit

---

### SearchQuery (Aggregate Root)

**Identity:** QueryId (UUID)

**Attributes:**
- queryId: QueryId
- queryText: QueryText
- filters: SearchFilters
- requestedBy: UserId
- executedAt: Timestamp
- resultCount: Integer
- executionTime: Duration

**Behaviors:**
- execute(): List<SearchResult>
- addResult(document, relevance): void
- rankResults(): void
- getCachedResults(): List<SearchResult>

**Business Rules:**
- Query text minimum 2 characters
- Maximum 50 results returned
- Results cached for 5 minutes
- Results ranked by relevance score

---

### SearchResult (Entity within SearchQuery)

**Identity:** ResultId (UUID)

**Attributes:**
- resultId: ResultId
- queryId: QueryId
- document: Document
- relevanceScore: RelevanceScore
- matchedTerms: List<String>
- position: Integer

**Behaviors:**
- getDocument(): Document
- getRelevanceScore(): RelevanceScore
- wasClicked(): Boolean

**Business Rules:**
- Relevance score between 0.0 and 1.0
- Position indicates ranking (1 = top result)
- Matched terms highlighted in snippet

---

## Value Objects

### DocumentId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): Boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### DocumentTitle

**Attributes:**
- value: String

**Behaviors:**
- equals(other): Boolean
- toString(): String
- truncate(length): String

**Invariants:**
- Length: 1-500 characters
- Cannot be empty

---

### DocumentUrl

**Attributes:**
- value: String (URL)

**Behaviors:**
- equals(other): Boolean
- toString(): String
- isValid(): Boolean
- getDomain(): String

**Invariants:**
- Must be valid URL format
- Must use HTTPS protocol
- Must be accessible

---

### DocumentAccessLevel

**Attributes:**
- value: Enum (PUBLIC, BASIC, ADVANCED)

**Behaviors:**
- isPublic(): Boolean
- isBasic(): Boolean
- isAdvanced(): Boolean
- isAccessibleBy(userAccessLevel): Boolean

**Invariants:**
- Must be one of the defined levels

**Access Level Rules:**
- PUBLIC: Accessible to all users
- BASIC: Accessible to End Users and Administrators
- ADVANCED: Accessible to Administrators only

---

### DocumentType

**Attributes:**
- value: Enum (SOP, PRD, GUIDE, OTHER)

**Behaviors:**
- isSOP(): Boolean
- isPRD(): Boolean
- isGuide(): Boolean
- toString(): String

**Invariants:**
- Must be one of the defined types

---

### DocumentFormat

**Attributes:**
- value: Enum (WEBPAGE, PDF, MARKDOWN)

**Behaviors:**
- isWebpage(): Boolean
- isPDF(): Boolean
- isMarkdown(): Boolean
- getMimeType(): String

**Invariants:**
- Must be one of the defined formats

---

### DocumentSource

**Attributes:**
- value: Enum (S3, CONFLUENCE)
- platformId: String (bucket name or space key)

**Behaviors:**
- isS3(): Boolean
- isConfluence(): Boolean
- getPlatformId(): String

**Invariants:**
- Must be one of the defined sources
- Platform ID must not be empty

---

### RelevanceScore

**Attributes:**
- value: Float (0.0-1.0)

**Behaviors:**
- compareTo(other): Integer
- isHighRelevance(): Boolean (>= 0.7)
- isMediumRelevance(): Boolean (0.4-0.7)
- isLowRelevance(): Boolean (< 0.4)

**Invariants:**
- Must be between 0.0 and 1.0
- Higher score = more relevant

---

### SearchFilters

**Attributes:**
- sources: List<DocumentSource> (optional)
- documentTypes: List<DocumentType> (optional)
- formats: List<DocumentFormat> (optional)
- accessLevels: List<DocumentAccessLevel> (optional)

**Behaviors:**
- matches(document): Boolean
- isEmpty(): Boolean

**Invariants:**
- At least one filter must be specified if not empty

---

### DocumentMetadata

**Attributes:**
- author: String
- createdAt: Timestamp
- lastModified: Timestamp
- fileSize: Integer (bytes)
- tags: List<String>
- category: String

**Behaviors:**
- hasTag(tag): Boolean
- isRecent(): Boolean (modified within 30 days)

---

## Domain Events

### DocumentDiscovered

**Attributes:**
- documentId: DocumentId
- source: DocumentSource
- title: DocumentTitle
- discoveredAt: Timestamp

**Triggered When:** New document found during search

**Consumers:** Internal (for caching and indexing)

---

### DocumentAccessed

**Attributes:**
- documentId: DocumentId
- userId: UserId
- accessedAt: Timestamp
- source: DocumentSource

**Triggered When:** User accesses a document

**Consumers:** 
- Internal (for access tracking)
- Communication & Analytics Context (for usage metrics)

---

### DocumentMetadataUpdated

**Attributes:**
- documentId: DocumentId
- previousVersion: Integer
- newVersion: Integer
- updatedAt: Timestamp

**Triggered When:** Document metadata is refreshed from source

**Consumers:** Internal (for version tracking)

---

### SearchExecuted

**Attributes:**
- queryId: QueryId
- queryText: String
- userId: UserId
- resultCount: Integer
- executionTime: Duration
- executedAt: Timestamp

**Triggered When:** Search query is executed

**Consumers:** Communication & Analytics Context (for search analytics)

---

### DocumentMarkedStale

**Attributes:**
- documentId: DocumentId
- lastAccessed: Timestamp
- markedStaleAt: Timestamp

**Triggered When:** Document not accessed for 90 days

**Consumers:** Internal (for cleanup)

---

## Repositories

### IDocumentRepository

**Purpose:** Persist and retrieve Document aggregates

**Methods:**
- save(document: Document): void
- findById(documentId: DocumentId): Document
- findByUrl(url: DocumentUrl): Document
- findBySource(source: DocumentSource, limit: Integer): List<Document>
- search(query: String, filters: SearchFilters): List<Document>
- findStale(days: Integer): List<Document>
- updateMetadata(documentId: DocumentId, metadata: DocumentMetadata): void
- delete(documentId: DocumentId): void

**Implementation Notes:**
- Uses `document_repository.documents` and `document_repository.document_versions` tables
- Implements full-text search indexing
- Caches frequently accessed documents

---

### ISearchQueryRepository

**Purpose:** Persist and retrieve SearchQuery aggregates

**Methods:**
- save(searchQuery: SearchQuery): void
- findById(queryId: QueryId): SearchQuery
- findRecent(userId: UserId, limit: Integer): List<SearchQuery>
- findCached(queryText: String, filters: SearchFilters): SearchQuery
- deleteOlderThan(minutes: Integer): Integer

**Implementation Notes:**
- Uses `document_repository.search_queries` and `document_repository.search_results` tables
- Implements TTL for cache expiration
- Indexes on queryText for fast lookup

---

## Domain Services

### DocumentSearchService

**Purpose:** Orchestrate document search across multiple sources

**Methods:**
- search(queryText: String, filters: SearchFilters, userId: UserId): List<SearchResult>
- searchS3(queryText: String): List<Document>
- searchConfluence(queryText: String): List<Document>
- mergeResults(s3Results, confluenceResults): List<Document>
- rankByRelevance(documents, query): List<SearchResult>

**Business Rules:**
- Search both S3 and Confluence in parallel
- Merge and deduplicate results
- Rank by relevance score
- Maximum 50 results
- Cache results for 5 minutes

**Rationale:** This is a domain service because it orchestrates search across multiple sources and applies ranking logic.

---

### RelevanceRankingService

**Purpose:** Calculate relevance scores for search results

**Methods:**
- calculateRelevance(document: Document, query: String): RelevanceScore
- extractKeywords(query: String): List<String>
- scoreKeywordMatch(document, keywords): Float
- scoreRecency(document): Float
- scorePopularity(document): Float

**Business Rules:**
- Keyword match: 60% weight
- Recency: 20% weight
- Popularity (access count): 20% weight
- Exact title match gets bonus score

**Rationale:** This is a domain service because it contains complex ranking algorithms that don't belong to a single aggregate.

---

### DocumentMetadataRefreshService

**Purpose:** Keep document metadata up-to-date

**Methods:**
- refreshMetadata(documentId: DocumentId): void
- refreshStaleDocuments(): Integer
- fetchMetadataFromSource(document: Document): DocumentMetadata

**Business Rules:**
- Refresh metadata when accessed and older than 24 hours
- Batch refresh stale documents daily
- Mark as stale if source no longer accessible

**Rationale:** This is a domain service because it manages metadata lifecycle across multiple documents.

---

## Application Services

### SearchDocumentsApplicationService

**Purpose:** Orchestrate document search workflow

**Responsibilities:**
1. Validate user authentication (call Access Control Context)
2. Validate search query
3. Execute search (call DocumentSearchService)
4. Filter results by user access level (call Access Control Context)
5. Publish SearchExecuted event
6. Return filtered results

**Not a Domain Service because:** It orchestrates across contexts and handles infrastructure concerns.

---

### GetDocumentApplicationService

**Purpose:** Retrieve a specific document

**Responsibilities:**
1. Validate user authentication
2. Retrieve document
3. Verify user has access (call Access Control Context)
4. Mark document as accessed
5. Refresh metadata if stale
6. Publish DocumentAccessed event
7. Return document

---

## Policies

### MetadataRefreshPolicy

**Rule:** Document metadata must be refreshed when accessed and older than 24 hours

**Implementation:**
- Checked in Document.markAsAccessed()
- Calls DocumentMetadataRefreshService if needed
- Asynchronous refresh to avoid blocking

---

### StaleDocumentPolicy

**Rule:** Documents not accessed for 90 days are marked as stale

**Implementation:**
- Scheduled job runs daily
- Calls DocumentMetadataRefreshService.refreshStaleDocuments()
- Publishes DocumentMarkedStale events

---

### SearchCachePolicy

**Rule:** Search results are cached for 5 minutes

**Implementation:**
- Checked in SearchQuery.getCachedResults()
- Cache key: queryText + filters
- Automatic expiration after 5 minutes

---

### ResultLimitPolicy

**Rule:** Maximum 50 search results per query

**Implementation:**
- Enforced in DocumentSearchService.search()
- Top 50 results by relevance score
- Remaining results discarded

---

## Business Rules Summary

### Document Rules
1. URL must be valid and unique within source
2. Must have an access level (public, basic, advanced)
3. Metadata refreshed when accessed and older than 24 hours
4. Documents not accessed for 90 days marked as stale
5. Access count incremented on each retrieval
6. Snippet limited to 200 characters

### Search Rules
1. Query text minimum 2 characters
2. Maximum 50 results per query
3. Results ranked by relevance score
4. Results cached for 5 minutes
5. Search executes across all sources in parallel
6. Results deduplicated by URL

### Access Rules
1. PUBLIC documents accessible to all users
2. BASIC documents accessible to End Users and Administrators
3. ADVANCED documents accessible to Administrators only
4. Access level checked before returning results

### Relevance Ranking Rules
1. Keyword match: 60% weight
2. Recency: 20% weight
3. Popularity: 20% weight
4. Exact title match gets bonus score
5. Score normalized to 0.0-1.0 range

---

## Aggregate Relationships

```
Document (Aggregate Root)
├── documentId: DocumentId (identity)
├── title: DocumentTitle (value object)
├── url: DocumentUrl (value object, unique)
├── source: DocumentSource (value object)
├── documentType: DocumentType (value object)
├── format: DocumentFormat (value object)
├── accessLevel: DocumentAccessLevel (value object)
├── metadata: DocumentMetadata (value object)
├── DocumentVersions (entities, 1-to-many)
│   ├── DocumentVersion 1
│   │   ├── versionId: VersionId
│   │   ├── versionNumber: Integer
│   │   └── modifiedAt: Timestamp
│   ├── DocumentVersion 2
│   └── DocumentVersion N
└── Timestamps (lastModified, lastAccessed)

SearchQuery (Aggregate Root)
├── queryId: QueryId (identity)
├── queryText: QueryText (value object)
├── filters: SearchFilters (value object)
├── SearchResults (entities, 1-to-many)
│   ├── SearchResult 1
│   │   ├── resultId: ResultId
│   │   ├── document: Document (reference)
│   │   ├── relevanceScore: RelevanceScore
│   │   └── position: Integer
│   ├── SearchResult 2
│   └── SearchResult N
└── Timestamps (executedAt)
```

---

## Consistency Boundaries

**Strong Consistency (within aggregate):**
- Document metadata updates are atomic
- Search results are consistent within a query

**Eventual Consistency (across aggregates):**
- Document metadata refresh is asynchronous
- Search cache may be slightly stale
- Access tracking is asynchronous

---

## Integration Points

### Inbound (APIs this context provides)

**REST Endpoints:**
- GET /api/v1/documents/search - Search documents
- GET /api/v1/documents/{documentId} - Get document details
- GET /api/v1/documents/{documentId}/metadata - Get document metadata

### Outbound (APIs this context consumes)

**Access Control Context:**
- POST /api/v1/auth/validate - Validate user token
- POST /api/v1/auth/filter-documents - Filter documents by access

**External Systems (via Infrastructure):**
- AWS S3 API - Search and retrieve documents from S3
- Confluence API - Search and retrieve documents from Confluence

---

## Infrastructure Concerns

**Not part of domain model, but noted for completeness:**

- S3 client integration (boto3 for Python, AWS SDK for JS)
- Confluence API client
- Full-text search indexing (Elasticsearch or PostgreSQL full-text)
- Document metadata caching (Redis)
- Search result caching (Redis with TTL)
- Pre-signed URL generation for S3 documents
- Rate limiting for external API calls

---

## Notes

- This context acts as a gateway to external document systems
- Does not store actual document content (only metadata)
- Implements caching for performance
- Relevance ranking is a key differentiator
- Access control is delegated to Access Control Context
- MVP focuses on S3 and Confluence (ClickUp and SuiteAnswers deferred)
- **Orchestration-only**: This service orchestrates document search and retrieval but does NOT implement business rules beyond search relevance

