# Integration Patterns - Cross-Unit Domain Model Integration

## Document Information
**Purpose:** Define how domain models integrate across bounded contexts  
**Version:** 1.0  
**Date:** January 27, 2026

---

## Overview

This document describes how the five bounded contexts integrate, focusing on domain events, shared concepts, and consistency patterns.

---

## Domain Events Flow

### Event-Driven Integration

Domain events are the primary mechanism for asynchronous communication between contexts.

```
┌─────────────────────────────────────────────────────────────┐
│                    Event Flow Diagram                        │
└─────────────────────────────────────────────────────────────┘

Chat Interface Context
├── ConversationCreated ──────────┐
├── MessageAdded ─────────────────┤
├── FeedbackSubmitted ────────────┤
├── ConversationResolved ─────────┤
└── ConversationEscalated ────────┤
                                  │
                                  ▼
                    Communication & Analytics Context
                    (Records events for metrics)

AI Orchestration Context
├── QueryProcessed ───────────────┐
├── LowConfidenceDetected ────────┤
└── IntentDetected ───────────────┤
                                  │
                                  ▼
                    Communication & Analytics Context
                    (Records events for metrics)

Document Repository Context
├── DocumentAccessed ─────────────┐
└── SearchExecuted ───────────────┤
                                  │
                                  ▼
                    Communication & Analytics Context
                    (Records events for metrics)

Access Control Context
├── UserAuthenticated ────────────┐
├── UserAuthenticationFailed ─────┤
└── SessionRevoked ───────────────┤
                                  │
                                  ▼
                    Communication & Analytics Context
                    (Records events for audit)
```

---

## Shared Concepts Across Contexts

### Identity References

Contexts reference entities from other contexts using IDs only (no direct object references).

**UserId** (from Access Control Context)
- Referenced by: All contexts
- Used for: Authentication, authorization, ownership

**ConversationId** (from Chat Interface Context)
- Referenced by: AI Orchestration, Communication & Analytics
- Used for: Query context, escalation, analytics

**DocumentId** (from Document Repository Context)
- Referenced by: AI Orchestration (for documentation links)
- Used for: Document references in responses

---

## Integration Patterns by Context Pair

### 1. Chat Interface ↔ Access Control

**Pattern:** Synchronous API calls for authentication and authorization

**Flow:**
```
Chat Interface → Access Control
├── POST /auth/validate (validate user token)
├── GET /auth/users/{userId} (get user profile)
└── POST /auth/filter-documents (filter by access level)
```

**Domain Model Integration:**
- Chat Interface stores UserId (reference)
- Chat Interface does NOT store user credentials or roles
- All permission checks delegated to Access Control

**Consistency:** Strong consistency (synchronous calls)

---

### 2. Chat Interface ↔ AI Orchestration

**Pattern:** Synchronous API calls for query processing

**Flow:**
```
Chat Interface → AI Orchestration
└── POST /ai/process-query
    ├── Input: query text, conversation context, user ID
    └── Output: AI response with documentation links
```

**Domain Model Integration:**
- Chat Interface sends ConversationId for context
- AI Orchestration returns Response with DocumentationLinks
- Chat Interface stores response as Message entity

**Consistency:** Strong consistency (synchronous calls)

---

### 3. Chat Interface ↔ Communication & Analytics

**Pattern:** Asynchronous events for escalation and analytics

**Flow:**
```
Chat Interface → Communication & Analytics
├── POST /communication/send-escalation-email (synchronous)
└── Domain Events (asynchronous):
    ├── ConversationCreated
    ├── MessageAdded
    ├── FeedbackSubmitted
    ├── ConversationResolved
    └── ConversationEscalated
```

**Domain Model Integration:**
- Chat Interface triggers escalation (synchronous)
- Chat Interface publishes events (asynchronous)
- Communication & Analytics reads conversation history via API

**Consistency:** Eventual consistency for analytics, strong consistency for escalation

---

### 4. AI Orchestration ↔ Access Control

**Pattern:** Synchronous API calls for permission verification

**Flow:**
```
AI Orchestration → Access Control
├── POST /auth/validate (validate user token)
├── GET /auth/users/{userId} (get user access level)
└── POST /auth/filter-documents (filter documents by access)
```

**Domain Model Integration:**
- AI Orchestration stores UserId (reference)
- AI Orchestration delegates all access filtering to Access Control
- Access level determines which documents are returned

**Consistency:** Strong consistency (synchronous calls)

---

### 5. AI Orchestration ↔ Document Repository

**Pattern:** Synchronous API calls for document search

**Flow:**
```
AI Orchestration → Document Repository
└── GET /documents/search
    ├── Input: query text, filters
    └── Output: list of documents with relevance scores
```

**Domain Model Integration:**
- AI Orchestration receives Document entities
- AI Orchestration filters documents via Access Control
- AI Orchestration converts to DocumentationLink value objects

**Consistency:** Strong consistency (synchronous calls)

---

### 6. Document Repository ↔ Access Control

**Pattern:** Synchronous API calls for permission verification

**Flow:**
```
Document Repository → Access Control
├── POST /auth/validate (validate user token)
└── POST /auth/filter-documents (filter by access level)
```

**Domain Model Integration:**
- Document Repository stores DocumentAccessLevel
- Access Control enforces filtering based on UserAccessLevel
- Documents filtered before returning to caller

**Consistency:** Strong consistency (synchronous calls)

---

### 7. All Contexts ↔ Communication & Analytics

**Pattern:** Asynchronous events for analytics

**Flow:**
```
All Contexts → Communication & Analytics
└── POST /communication/analytics/record-event
    ├── Event types: query_submitted, feedback_submitted, etc.
    └── Asynchronous processing
```

**Domain Model Integration:**
- All contexts publish domain events
- Communication & Analytics subscribes to events
- Events stored as AnalyticsEvent aggregates
- Metrics calculated from events

**Consistency:** Eventual consistency (asynchronous events)

---

## Aggregate Boundaries and Consistency

### Strong Consistency (Within Aggregate)

Each context maintains strong consistency within its own aggregates:

**Chat Interface:**
- Conversation + Messages (atomic updates)

**Access Control:**
- User + Sessions (atomic updates)

**Document Repository:**
- Document + DocumentVersions (atomic updates)
- SearchQuery + SearchResults (atomic updates)

**AI Orchestration:**
- AIQuery + ContextMessages (atomic updates)

**Communication & Analytics:**
- EscalationEmail (atomic updates)
- AnalyticsEvent (atomic updates)
- Metric + MetricDataPoints (atomic updates)

---

### Eventual Consistency (Across Aggregates)

Cross-context operations use eventual consistency:

**Analytics Events:**
- Events published asynchronously
- Metrics calculated daily (not real-time)
- Dashboard data may be up to 24 hours old

**Document Metadata:**
- Metadata refreshed asynchronously
- Search results may be slightly stale (5-minute cache)

**Email Delivery:**
- Escalation emails sent asynchronously
- Delivery confirmation may be delayed

---

## Data Ownership

### Clear Ownership Boundaries

Each context owns its data exclusively:

| Context | Owned Data |
|---------|-----------|
| **Chat Interface** | Conversations, Messages, Feedback |
| **Access Control** | Users, Sessions, Roles, Permissions |
| **Document Repository** | Document metadata, Search queries |
| **AI Orchestration** | AI queries, Processing metrics |
| **Communication & Analytics** | Escalation emails, Analytics events, Metrics |

**Rule:** No direct database access between contexts. All data access via APIs.

---

## Shared Kernel: Access Control

Access Control Context acts as a **Shared Kernel** - all contexts depend on it.

**Shared Concepts:**
- UserId
- Role
- AccessLevel
- Permission
- JWT Token

**Integration Pattern:**
- All contexts call Access Control for authentication
- All contexts use JWT tokens for authorization
- All contexts respect access level filtering

---

## Event Sourcing vs State-Based Persistence

**Decision:** Traditional state-based persistence for MVP

**Rationale:**
- Simpler implementation
- Faster development
- Good enough for MVP requirements

**Domain Events Still Used For:**
- Cross-context communication (asynchronous)
- Analytics event collection
- Audit logging

**Not Used For:**
- Primary data storage (events not replayed)
- State reconstruction

---

## Anti-Corruption Layers

**Decision:** Not used in MVP

**Rationale:**
- External systems (S3, Confluence, AWS Bedrock) handled as simple infrastructure adapters
- Complexity not justified for MVP
- Can be added in post-MVP if needed

**Future Consideration:**
- Add ACL if external APIs become complex or unstable
- Add ACL if external data models diverge significantly from domain models

---

## Transaction Boundaries

### Single Context Transactions

Transactions are scoped to single contexts:

**Chat Interface:**
- Create conversation + add first message (single transaction)
- Add message + update conversation (single transaction)

**Access Control:**
- Create user + assign role (single transaction)
- Login + create session (single transaction)

**Document Repository:**
- Save document + create version (single transaction)

**AI Orchestration:**
- Create query + add context + save response (single transaction)

**Communication & Analytics:**
- Create email + queue for sending (single transaction)
- Record event (single transaction)

### Cross-Context Transactions

**No distributed transactions in MVP**

**Pattern:** Eventual consistency via events

**Example - Escalation Flow:**
1. Chat Interface: Mark conversation as escalated (transaction 1)
2. Publish ConversationEscalated event
3. Communication & Analytics: Create escalation email (transaction 2)
4. Send email (asynchronous)

**Failure Handling:**
- Each transaction can succeed or fail independently
- Compensating actions for failures
- Idempotent event handlers

---

## API Contract Enforcement

### Integration Contract

All API contracts defined in `/inception/units/integration_contract.md`

**Enforcement:**
- Request/response schemas validated
- API versioning (v1)
- Backward compatibility maintained
- Breaking changes require new version

### Domain Model Alignment

API contracts align with domain models:

**Example - Process Query:**
```
API Request:
{
  "query": "string",
  "context": {...}
}

Domain Model:
AIQuery aggregate with:
- queryText: QueryText (value object)
- context: List<ContextMessage> (entities)
```

---

## Error Handling Across Contexts

### Error Propagation

Errors propagate up the call chain:

```
Chat Interface
    ↓ (calls)
AI Orchestration
    ↓ (calls)
Document Repository
    ↓ (error occurs)
    ↑ (error returned)
    ↑ (error handled/transformed)
    ↑ (error returned to user)
```

### Error Types

**Domain Errors:**
- Validation failures (e.g., empty query)
- Business rule violations (e.g., conversation already escalated)
- Returned as 400 Bad Request

**Authorization Errors:**
- Invalid token
- Insufficient permissions
- Returned as 401 Unauthorized or 403 Forbidden

**Infrastructure Errors:**
- External service failures (AI, S3, Confluence)
- Database errors
- Returned as 500 Internal Server Error

---

## Performance Considerations

### Caching Strategy

**Access Control:**
- Cache user permissions (5-minute TTL)
- Cache JWT token validation (1-minute TTL)

**Document Repository:**
- Cache search results (5-minute TTL)
- Cache document metadata (24-hour TTL)

**AI Orchestration:**
- Cache common query responses (1-hour TTL)
- Cache intent detection results (5-minute TTL)

### Parallel Processing

**AI Query Processing:**
- Search S3 and Confluence in parallel
- Filter documents while AI processes query

**Analytics:**
- Process events asynchronously
- Calculate metrics in background jobs

---

## Monitoring and Observability

### Cross-Context Tracing

**Correlation IDs:**
- Each request assigned a correlation ID
- Correlation ID passed across context boundaries
- Used for distributed tracing

**Example Flow:**
```
Request ID: req-123
├── Chat Interface (req-123)
│   ├── AI Orchestration (req-123)
│   │   ├── Access Control (req-123)
│   │   └── Document Repository (req-123)
│   └── Communication & Analytics (req-123)
```

### Domain Event Monitoring

**Event Metrics:**
- Event publish rate
- Event processing latency
- Failed event deliveries

---

## Summary

### Key Integration Patterns

1. **Synchronous APIs** for request-response operations
2. **Asynchronous Events** for analytics and notifications
3. **Shared Kernel** (Access Control) for authentication/authorization
4. **Strong Consistency** within aggregates
5. **Eventual Consistency** across contexts
6. **No Distributed Transactions** in MVP
7. **Clear Data Ownership** boundaries
8. **API Contract Enforcement** via integration contract

### Benefits

- **Loose Coupling:** Contexts can evolve independently
- **High Cohesion:** Related functionality grouped together
- **Scalability:** Contexts can be scaled independently
- **Testability:** Each context can be tested in isolation
- **Maintainability:** Clear boundaries and responsibilities

### Trade-offs

- **Eventual Consistency:** Analytics data may be slightly stale
- **No Distributed Transactions:** Requires compensating actions
- **API Overhead:** Cross-context calls have network latency
- **Complexity:** More moving parts than monolithic design

---

## Notes

- Integration patterns designed for MVP simplicity
- Can be enhanced in post-MVP (e.g., add message queue, event sourcing)
- Focus on clear boundaries and contracts
- Emphasis on maintainability and testability

