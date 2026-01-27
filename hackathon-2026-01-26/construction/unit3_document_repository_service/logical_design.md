# Logical Design - Unit 3: Document Repository Service

## Document Information
**Bounded Context:** Document Repository Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Architecture Style:** Hexagonal Architecture (Ports & Adapters)  
**Technology Stack:** Python/FastAPI or Node.js/Express (framework-agnostic design)

---

## 1. Architecture Overview

### 1.1 Architectural Style
**Hexagonal Architecture** - Domain at center, external systems as adapters:

```
┌─────────────────────────────────────────────────────────────┐
│                    Inbound Adapters                          │
│              (REST API Controllers)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Inbound Ports                              │
│         (Application Service Interfaces)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Domain Core                                 │
│  (Aggregates, Entities, Value Objects, Domain Services)      │
│                                                              │
│  Defines Outbound Ports (Interfaces):                        │
│  - IDocumentSearchProvider                                   │
│  - IDocumentRepository                                       │
│  - IAccessControlClient                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Outbound Adapters                            │
│  - S3SearchAdapter (implements IDocumentSearchProvider)      │
│  - ConfluenceSearchAdapter (implements IDocumentSearchProvider)│
│  - PostgreSQLRepository (implements IDocumentRepository)     │
│  - AccessControlHTTPClient (implements IAccessControlClient) │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Why Hexagonal for This Service?

**Multiple External Systems:**
- S3 document storage
- Confluence API
- Access Control Context
- Future: ClickUp, SuiteAnswers (post-MVP)

**Benefits:**
- Easy to swap document sources
- Domain logic isolated from external APIs
- Highly testable with mock adapters
- Can add new document sources without changing domain

---

## 2. Component Structure

### 2.1 Inbound Adapters (API Layer)

#### REST Controllers

**DocumentSearchController**
- **Responsibility:** Handle HTTP requests for document search
- **Endpoints:**
  - `GET /api/v1/documents/search` → searchDocuments()
  - `GET /api/v1/documents/{documentId}` → getDocument()
  - `GET /api/v1/documents/{documentId}/metadata` → getDocumentMetadata()

#### DTOs (Data Transfer Objects)

**Request DTOs:**
- SearchDocumentsRequest (query, platforms, documentType, limit)
- GetDocumentRequest (documentId)

**Response DTOs:**
- SearchResultsResponse (results, totalResults, query)
- DocumentResponse (id, title, url, platform, format, accessLevel, metadata)
- DocumentMetadataResponse (author, created, lastModified, fileSize, tags)

---

### 2.2 Inbound Ports (Application Service Interfaces)

#### Application Service Interfaces

**ISearchDocumentsUseCase**
- searchDocuments(query, filters, userId) → SearchResults

**IGetDocumentUseCase**
- getDocument(documentId, userId) → Document

**IGetDocumentMetadataUseCase**
- getDocumentMetadata(documentId, userId) → DocumentMetadata

---

### 2.3 Domain Core

#### Aggregates

**Document (Aggregate Root)**
- **Identity:** DocumentId
- **Entities:** DocumentVersion (collection)
- **Value Objects:** DocumentTitle, DocumentUrl, DocumentAccessLevel, DocumentType, DocumentFormat, DocumentSource, RelevanceScore
- **Key Methods:**
  - updateMetadata(metadata) → void
  - markAsAccessed() → void
  - isAccessibleBy(userAccessLevel) → Boolean
  - calculateRelevance(query) → RelevanceScore
  - refreshFromSource() → void
  - markAsStale() → void

**SearchQuery (Aggregate Root)**
- **Identity:** QueryId
- **Entities:** SearchResult (collection)
- **Value Objects:** QueryText, SearchFilters, RelevanceScore
- **Key Methods:**
  - execute() → List<SearchResult>
  - addResult(document, relevance) → void
  - rankResults() → void
  - getCachedResults() → List<SearchResult>

#### Entities

**DocumentVersion**
- **Identity:** VersionId
- **Attributes:** versionNumber, modifiedAt, modifiedBy, changeDescription
- **Key Methods:**
  - isLatest() → Boolean
  - getChangesSince(version) → String

**SearchResult**
- **Identity:** ResultId
- **Attributes:** document, relevanceScore, matchedTerms, position
- **Key Methods:**
  - getDocument() → Document
  - getRelevanceScore() → RelevanceScore

#### Value Objects

**DocumentId** - UUID wrapper
**DocumentTitle** - String (1-500 chars)
**DocumentUrl** - URL with validation
**DocumentAccessLevel** - Enum (PUBLIC, BASIC, ADVANCED)
**DocumentType** - Enum (SOP, PRD, GUIDE, OTHER)
**DocumentFormat** - Enum (WEBPAGE, PDF, MARKDOWN)
**DocumentSource** - Enum (S3, CONFLUENCE) + platformId
**RelevanceScore** - Float (0.0-1.0)
**SearchFilters** - sources, documentTypes, formats, accessLevels
**DocumentMetadata** - author, createdAt, lastModified, fileSize, tags, category

#### Domain Services

**DocumentSearchService**
- **Responsibility:** Orchestrate document search across sources
- **Operations:**
  - search(queryText, filters, userId) → List<SearchResult>
  - searchS3(queryText) → List<Document>
  - searchConfluence(queryText) → List<Document>
  - mergeResults(s3Results, confluenceResults) → List<Document>
  - rankByRelevance(documents, query) → List<SearchResult>

**RelevanceRankingService**
- **Responsibility:** Calculate relevance scores
- **Operations:**
  - calculateRelevance(document, query) → RelevanceScore
  - extractKeywords(query) → List<String>
  - scoreKeywordMatch(document, keywords) → Float
  - scoreRecency(document) → Float
  - scorePopularity(document) → Float
- **Algorithm:**
  - Keyword match: 60% weight
  - Recency: 20% weight
  - Popularity (access count): 20% weight

**DocumentMetadataRefreshService**
- **Responsibility:** Keep metadata up-to-date
- **Operations:**
  - refreshMetadata(documentId) → void
  - refreshStaleDocuments() → Integer
  - fetchMetadataFromSource(document) → DocumentMetadata

#### Domain Events

- DocumentDiscovered
- DocumentAccessed
- DocumentMetadataUpdated
- SearchExecuted
- DocumentMarkedStale

---

### 2.4 Outbound Ports (Interfaces Defined by Domain)

#### Repository Interfaces

**IDocumentRepository**
- save(document) → void
- findById(documentId) → Document
- findByUrl(url) → Document
- findBySource(source, limit) → List<Document>
- search(query, filters) → List<Document>
- findStale(days) → List<Document>
- updateMetadata(documentId, metadata) → void
- delete(documentId) → void

**ISearchQueryRepository**
- save(searchQuery) → void
- findById(queryId) → SearchQuery
- findRecent(userId, limit) → List<SearchQuery>
- findCached(queryText, filters) → SearchQuery
- deleteOlderThan(minutes) → Integer

#### External Service Interfaces

**IDocumentSearchProvider**
- **Purpose:** Abstract document search from external sources
- **Operations:**
  - search(query) → List<Document>
  - getDocument(documentId) → Document
  - getMetadata(documentId) → DocumentMetadata
  - isAvailable() → Boolean

**IAccessControlClient**
- **Purpose:** Communicate with Access Control Context
- **Operations:**
  - validateToken(token) → User
  - filterDocuments(documents, userId) → List<Document>

**ICacheProvider**
- **Purpose:** Cache search results and metadata
- **Operations:**
  - get(key) → Value
  - set(key, value, ttl) → void
  - delete(key) → void
  - exists(key) → Boolean

---

### 2.5 Outbound Adapters (Implementations)

#### Document Search Adapters

**S3SearchAdapter (implements IDocumentSearchProvider)**
- **Responsibility:** Search documents in S3
- **Operations:**
  - search(query) → List<Document>
    - Connect to S3 using boto3 (Python) or AWS SDK (Node.js)
    - Search bucket metadata and tags
    - Generate pre-signed URLs
    - Map S3 objects to Document entities
  - getDocument(documentId) → Document
  - getMetadata(documentId) → DocumentMetadata
  - isAvailable() → Boolean
- **Configuration:** S3 bucket name, region, credentials

**ConfluenceSearchAdapter (implements IDocumentSearchProvider)**
- **Responsibility:** Search documents in Confluence
- **Operations:**
  - search(query) → List<Document>
    - Call Confluence REST API
    - Use CQL (Confluence Query Language)
    - Map Confluence pages to Document entities
  - getDocument(documentId) → Document
  - getMetadata(documentId) → DocumentMetadata
  - isAvailable() → Boolean
- **Configuration:** Confluence URL, API token, space keys

#### Repository Adapters

**PostgreSQLDocumentRepository (implements IDocumentRepository)**
- **Responsibility:** Persist documents in PostgreSQL
- **Implementation:** Uses `document_repository` schema
- **Features:**
  - Full-text search indexing
  - Caching layer for frequently accessed documents
  - Optimistic locking for concurrent updates

**PostgreSQLSearchQueryRepository (implements ISearchQueryRepository)**
- **Responsibility:** Persist search queries
- **Implementation:** Uses `document_repository` schema
- **Features:**
  - TTL-based cache expiration
  - Indexes on queryText for fast lookup

#### External Service Adapters

**AccessControlHTTPClient (implements IAccessControlClient)**
- **Responsibility:** Communicate with Access Control Context
- **Operations:**
  - validateToken(token) → User
    - POST /api/v1/auth/validate
  - filterDocuments(documents, userId) → List<Document>
    - POST /api/v1/auth/filter-documents
- **Error Handling:** Retry on transient failures, circuit breaker pattern

**RedisCacheAdapter (implements ICacheProvider)**
- **Responsibility:** Cache search results and metadata
- **Operations:**
  - get(key), set(key, value, ttl), delete(key), exists(key)
- **Configuration:** Redis host, port, TTL settings

---

### 2.6 Application Services (Implement Inbound Ports)

**SearchDocumentsApplicationService (implements ISearchDocumentsUseCase)**
- **Responsibility:** Orchestrate document search workflow
- **Dependencies:**
  - IAccessControlClient
  - DocumentSearchService
  - IDocumentRepository
  - ICacheProvider
- **Workflow:**
  1. Validate user authentication
  2. Check cache for recent search
  3. If not cached, execute search via DocumentSearchService
  4. Filter results by user access level
  5. Cache results (5-minute TTL)
  6. Publish SearchExecuted event
  7. Return results

**GetDocumentApplicationService (implements IGetDocumentUseCase)**
- **Responsibility:** Retrieve specific document
- **Dependencies:**
  - IAccessControlClient
  - IDocumentRepository
  - DocumentMetadataRefreshService
- **Workflow:**
  1. Validate user authentication
  2. Retrieve document from repository
  3. Verify user has access
  4. Mark document as accessed
  5. Refresh metadata if stale (> 24 hours)
  6. Publish DocumentAccessed event
  7. Return document

---

## 3. Data Flow Diagrams

### 3.1 Search Documents Flow

```
User Request (query, filters)
    ↓
DocumentSearchController.searchDocuments()
    ↓
SearchDocumentsApplicationService.execute()
    ├─→ AccessControlHTTPClient.validateToken()
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return User
    ├─→ CacheProvider.get(cacheKey)
    │       ↓
    │   If cached → Return cached results
    ├─→ DocumentSearchService.search()
    │   ├─→ S3SearchAdapter.search(query) [Parallel]
    │   │       ↓
    │   │   [AWS S3 API]
    │   │       ↓
    │   │   Return S3 Documents
    │   ├─→ ConfluenceSearchAdapter.search(query) [Parallel]
    │   │       ↓
    │   │   [Confluence API]
    │   │       ↓
    │   │   Return Confluence Documents
    │   ├─→ mergeResults(s3Results, confluenceResults)
    │   ├─→ RelevanceRankingService.rankByRelevance()
    │   └─→ Return ranked documents
    ├─→ AccessControlHTTPClient.filterDocuments(documents, userId)
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return filtered documents
    ├─→ DocumentRepository.save(documents) - Cache metadata
    ├─→ CacheProvider.set(cacheKey, results, 5min)
    ├─→ EventPublisher.publish(SearchExecuted)
    ↓
Return SearchResultsResponse
```

### 3.2 Get Document Flow

```
User Request (documentId)
    ↓
DocumentSearchController.getDocument()
    ↓
GetDocumentApplicationService.execute()
    ├─→ AccessControlHTTPClient.validateToken()
    ├─→ DocumentRepository.findById(documentId)
    │       ↓
    │   If not found → Return 404
    ├─→ Document.isAccessibleBy(user.accessLevel)
    │       ↓
    │   If not accessible → Return 403
    ├─→ Document.markAsAccessed()
    ├─→ If metadata stale (> 24 hours):
    │   ├─→ DocumentMetadataRefreshService.refreshMetadata()
    │   │   ├─→ Determine source (S3 or Confluence)
    │   │   ├─→ Call appropriate adapter.getMetadata()
    │   │   └─→ Document.updateMetadata()
    │   └─→ DocumentRepository.save(document)
    ├─→ EventPublisher.publish(DocumentAccessed)
    ↓
Return DocumentResponse
```

---

## 4. Database Schema Design

### 4.1 Schema: `document_repository`

#### Table: `documents`
```
documents
├── document_id (UUID, PK)
├── title (VARCHAR(500), NOT NULL)
├── url (VARCHAR(1000), UNIQUE, NOT NULL)
├── source (ENUM: s3, confluence, NOT NULL)
├── platform_id (VARCHAR(255), NOT NULL) - bucket name or space key
├── document_type (ENUM: sop, prd, guide, other)
├── format (ENUM: webpage, pdf, markdown)
├── access_level (ENUM: public, basic, advanced, NOT NULL)
├── snippet (TEXT)
├── last_modified (TIMESTAMP)
├── last_accessed (TIMESTAMP)
├── access_count (INTEGER, DEFAULT 0)
├── is_stale (BOOLEAN, DEFAULT false)
├── created_at (TIMESTAMP, NOT NULL)
└── INDEX on source, INDEX on url, INDEX on last_accessed
└── FULLTEXT INDEX on title, snippet (for search)
```

#### Table: `document_versions`
```
document_versions
├── version_id (UUID, PK)
├── document_id (UUID, FK to documents)
├── version_number (INTEGER, NOT NULL)
├── modified_at (TIMESTAMP, NOT NULL)
├── modified_by (VARCHAR(255))
├── change_description (TEXT)
└── INDEX on document_id, version_number
```

#### Table: `document_metadata`
```
document_metadata
├── metadata_id (UUID, PK)
├── document_id (UUID, FK to documents, UNIQUE)
├── author (VARCHAR(255))
├── created_at (TIMESTAMP)
├── file_size (BIGINT) - bytes
├── tags (JSONB) - array of strings
├── category (VARCHAR(100))
└── INDEX on document_id
```

#### Table: `search_queries`
```
search_queries
├── query_id (UUID, PK)
├── query_text (TEXT, NOT NULL)
├── filters (JSONB) - SearchFilters as JSON
├── user_id (UUID, NOT NULL)
├── result_count (INTEGER)
├── execution_time (INTEGER) - milliseconds
├── executed_at (TIMESTAMP, NOT NULL)
└── INDEX on query_text, executed_at (for cache lookup)
```

#### Table: `search_results`
```
search_results
├── result_id (UUID, PK)
├── query_id (UUID, FK to search_queries)
├── document_id (UUID, FK to documents)
├── relevance_score (DECIMAL(3,2))
├── matched_terms (JSONB) - array of strings
├── position (INTEGER)
└── INDEX on query_id, position
```

---

## 5. API-to-Component Mapping

### 5.1 Endpoint Mappings

| HTTP Method | Endpoint | Controller | Application Service | Domain Service | Adapters |
|-------------|----------|------------|---------------------|----------------|----------|
| GET | /api/v1/documents/search | DocumentSearchController | SearchDocumentsApplicationService | DocumentSearchService | S3SearchAdapter, ConfluenceSearchAdapter |
| GET | /api/v1/documents/{id} | DocumentSearchController | GetDocumentApplicationService | - | S3SearchAdapter or ConfluenceSearchAdapter |
| GET | /api/v1/documents/{id}/metadata | DocumentSearchController | GetDocumentMetadataApplicationService | DocumentMetadataRefreshService | S3SearchAdapter or ConfluenceSearchAdapter |

---

## 6. Integration Points

### 6.1 Outbound Integrations

**Access Control Context (Synchronous REST)**
- Endpoint: `POST /api/v1/auth/validate`
- Purpose: Validate user token
- Adapter: AccessControlHTTPClient

- Endpoint: `POST /api/v1/auth/filter-documents`
- Purpose: Filter documents by access level
- Adapter: AccessControlHTTPClient

**AWS S3 (External System)**
- API: AWS S3 REST API
- Purpose: Search and retrieve documents
- Adapter: S3SearchAdapter
- Authentication: AWS credentials (IAM role or access keys)

**Confluence (External System)**
- API: Confluence REST API
- Purpose: Search and retrieve documents
- Adapter: ConfluenceSearchAdapter
- Authentication: API token

### 6.2 Inbound Integrations

**AI Orchestration Context**
- Calls: `GET /api/v1/documents/search`
- Purpose: Retrieve documents for AI responses

**Chat Interface Context (indirect)**
- Via AI Orchestration Context

---

## 7. Error Handling Strategy

### 7.1 Error Categories

**Validation Errors (400 Bad Request)**
- Empty query text
- Invalid document ID format
- Invalid filters

**Authentication Errors (401 Unauthorized)**
- Invalid token
- Expired token

**Authorization Errors (403 Forbidden)**
- User doesn't have access to document

**Not Found Errors (404 Not Found)**
- Document not found
- Document no longer exists in source

**External Service Errors (500/503)**
- S3 unavailable
- Confluence API failure
- Access Control service unavailable

### 7.2 Adapter Error Handling

**Circuit Breaker Pattern:**
- If S3 fails 5 times in 1 minute, open circuit for 30 seconds
- If Confluence fails 5 times in 1 minute, open circuit for 30 seconds
- Return partial results if one source fails

**Retry Strategy:**
- Transient failures: Retry 3 times with exponential backoff
- Permanent failures: Return error immediately

**Fallback Strategy:**
- If S3 fails, return Confluence results only
- If Confluence fails, return S3 results only
- If both fail, return cached results if available

---

## 8. Security Considerations

### 8.1 Authentication
- All endpoints require valid JWT token
- Token validated via Access Control Context

### 8.2 Authorization
- Document access filtered by user access level
- Access level checked before returning documents

### 8.3 External API Security
- S3: Use IAM roles with least privilege
- Confluence: API token stored securely (environment variable)
- Never expose external API credentials in responses

### 8.4 Input Validation
- Query text: Max 500 characters
- Document ID: Valid UUID format
- URL validation before storing

---

## 9. Performance Considerations

### 9.1 Caching Strategy
- Search results: 5-minute TTL (Redis)
- Document metadata: 24-hour TTL (Redis)
- Frequently accessed documents: In-memory cache

### 9.2 Parallel Processing
- Search S3 and Confluence in parallel
- Use async/await or threading

### 9.3 Database Optimization
- Full-text search indexes on title and snippet
- Indexes on frequently queried fields
- Connection pooling

### 9.4 Response Time Targets
- Search documents: < 2 seconds (90th percentile)
- Get document: < 300ms
- Get metadata: < 200ms

---

## 10. Deployment Considerations

### 10.1 Service Deployment
- Containerized application (Docker)
- Stateless service (horizontal scaling)
- Environment-specific configuration

### 10.2 External Service Configuration
- S3: Bucket name, region, credentials
- Confluence: URL, API token, space keys
- Redis: Host, port, password

### 10.3 Monitoring
- Health check endpoint: `GET /health`
- Adapter health checks (S3, Confluence availability)
- Metrics: Search latency, cache hit rate, external API errors
- Alerts: High error rate, slow searches, external service failures

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Domain layer: Test aggregates, entities, value objects, domain services
- Relevance ranking algorithm
- Coverage target: 80%+

### 11.2 Integration Tests
- Test with mock adapters (no real S3/Confluence calls)
- Test repository operations with test database
- Test caching behavior

### 11.3 Adapter Tests
- Test S3SearchAdapter with localstack (S3 emulator)
- Test ConfluenceSearchAdapter with mock server
- Test error handling and retries

### 11.4 Contract Tests
- Verify API contracts with Access Control Context
- Verify external API contracts (S3, Confluence)

---

## 12. Benefits of Hexagonal Architecture

### 12.1 Testability
- Domain logic tested without external dependencies
- Mock adapters for unit tests
- Easy to test different scenarios (S3 failure, Confluence failure)

### 12.2 Flexibility
- Easy to add new document sources (ClickUp, SuiteAnswers)
- Easy to swap implementations (S3 → Azure Blob Storage)
- Easy to change caching strategy (Redis → Memcached)

### 12.3 Maintainability
- Domain logic isolated from infrastructure
- Clear boundaries between layers
- External API changes don't affect domain

---

## 13. Future Enhancements (Post-MVP)

- Add ClickUp adapter
- Add SuiteAnswers adapter
- Advanced search (filters, facets, date ranges)
- Document content indexing (full-text search)
- Document recommendations
- Search analytics (popular queries, zero-result queries)
- Document versioning and change tracking

---

## Notes

- Hexagonal architecture perfect for this service (multiple external systems)
- Adapters make it easy to add new document sources
- Domain logic isolated and highly testable
- Parallel search improves performance
- Caching reduces external API calls
- Circuit breaker prevents cascading failures
