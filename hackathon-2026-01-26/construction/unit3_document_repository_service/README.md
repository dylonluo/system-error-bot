# Document Repository Service (Unit 3)

A Domain-Driven Design implementation of the Document Repository Service using Hexagonal Architecture. This service searches and retrieves documentation from external sources (S3, Confluence) with access control and relevance ranking.

## Architecture

**Hexagonal Architecture (Ports & Adapters)**
- **Domain Core**: Aggregates, Entities, Value Objects, Domain Services
- **Inbound Ports**: Application Service Interfaces
- **Outbound Ports**: Repository and External Service Interfaces
- **Adapters**: Infrastructure implementations (in-memory for MVP)

## Features

- ✅ Document search across multiple sources (S3 focus for MVP)
- ✅ Relevance ranking with configurable weights
- ✅ Access level filtering (PUBLIC, BASIC, ADVANCED)
- ✅ Document metadata management
- ✅ Search result caching (5-minute TTL)
- ✅ Domain event publishing
- ✅ RESTful API with FastAPI

## Project Structure

```
unit3_document_repository_service/
├── src/
│   ├── domain/              # Domain layer (business logic)
│   │   ├── value_objects/   # Immutable value objects
│   │   ├── entities/        # Domain entities
│   │   ├── aggregates/      # Aggregate roots
│   │   ├── events/          # Domain events
│   │   ├── repositories/    # Repository interfaces
│   │   ├── services/        # Domain services
│   │   └── ports/           # External service interfaces
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── repositories/    # In-memory repositories
│   │   ├── adapters/        # Mock adapters (S3, Access Control)
│   │   └── events/          # Event publisher
│   ├── application/         # Application layer
│   │   ├── dtos/            # Request/Response DTOs
│   │   └── services/        # Application services
│   └── api/                 # API layer
│       ├── controllers/     # REST controllers
│       ├── middleware/      # Error handling
│       └── main.py          # FastAPI application
├── demo.py                  # Demo script
├── pyproject.toml           # Dependencies
└── README.md                # This file
```

## Installation

### Prerequisites
- Python 3.11+
- uv (Python package manager)

### Setup

1. Install dependencies:
```bash
cd hackathon-2026-01-26/construction/unit3_document_repository_service
uv pip install -e .
```

Or with pip:
```bash
pip install -e .
```

## Running the Demo

The demo script demonstrates all key features without starting the API server:

```bash
python demo.py
```

### Demo Scenarios

1. **Search Documents**: Search for "NetSuite" and "TMS" with different user access levels
2. **Get Document by ID**: Retrieve a specific document with metadata
3. **Access Level Filtering**: Demonstrate access control (End User vs Administrator)

## Running the API Server

Start the FastAPI server:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```
GET /health
```

### Search Documents
```
GET /api/v1/documents/search?query=NetSuite&limit=10
Headers:
  Authorization: user-123  (or admin-456)
```

Query Parameters:
- `query` (required): Search query text
- `sources`: Filter by sources (s3, confluence)
- `document_types`: Filter by types (sop, prd, guide, other)
- `formats`: Filter by formats (webpage, pdf, markdown)
- `access_levels`: Filter by access (public, basic, advanced)
- `limit`: Maximum results (default: 50, max: 100)

### Get Document
```
GET /api/v1/documents/{document_id}
Headers:
  Authorization: user-123
```

### Get Document Metadata
```
GET /api/v1/documents/{document_id}/metadata
Headers:
  Authorization: user-123
```

## Sample Data

The mock S3 adapter includes 5 pre-populated documents:

1. **NetSuite Error Troubleshooting Guide** (BASIC access)
2. **TMS Integration SOP** (ADVANCED access)
3. **NetSuite API Integration Guide** (BASIC access)
4. **TMS User Manual** (PUBLIC access)
5. **System Architecture PRD** (ADVANCED access)

## Mock Users

Two mock users are available for testing:

- **End User**: `user-123` (access_level: "basic")
  - Can access PUBLIC and BASIC documents
  
- **Administrator**: `admin-456` (access_level: "all")
  - Can access all documents (PUBLIC, BASIC, ADVANCED)

## Domain Model

### Aggregates
- **Document**: Represents a document with metadata and access control
- **SearchQuery**: Represents a search request with results

### Value Objects
- DocumentId, DocumentTitle, DocumentUrl
- DocumentAccessLevel, DocumentType, DocumentFormat
- DocumentSource, RelevanceScore, SearchFilters
- DocumentMetadata, QueryId, QueryText

### Domain Events
- DocumentDiscovered
- DocumentAccessed
- DocumentMetadataUpdated
- SearchExecuted
- DocumentMarkedStale

## Relevance Ranking Algorithm

Documents are ranked using a weighted scoring system:

- **Keyword Match**: 60% weight
  - Title matches worth 2x snippet matches
- **Recency**: 20% weight
  - Recent documents (< 30 days) score higher
- **Popularity**: 20% weight
  - Based on access count
- **Bonus**: Exact title match adds 0.2 to score

## Access Control Rules

- **PUBLIC**: Accessible to all users
- **BASIC**: Accessible to End Users and Administrators
- **ADVANCED**: Accessible to Administrators only

## Testing

Run the demo script to verify all functionality:

```bash
python demo.py
```

Expected output:
- ✓ Search results with relevance scores
- ✓ Document retrieval with metadata
- ✓ Access level filtering working correctly
- ✓ Events published for all operations

## Development

### Adding New Document Sources

1. Create adapter implementing `IDocumentSearchProvider`
2. Register in `main.py`
3. Update `DocumentSearchService` to include new source

### Extending Domain Model

1. Add new value objects in `domain/value_objects/`
2. Update aggregates if needed
3. Add domain events for new behaviors
4. Update application services

## Notes

- All repositories use in-memory storage (no persistence)
- Mock adapters return pre-defined sample documents
- Event publisher logs events to console
- Cache has 5-minute TTL for search results
- Metadata refresh triggered when > 24 hours old

## Future Enhancements

- PostgreSQL repository implementation
- Real S3 and Confluence adapters
- Redis cache provider
- Document content indexing
- Advanced search filters
- Document recommendations
- Search analytics dashboard
