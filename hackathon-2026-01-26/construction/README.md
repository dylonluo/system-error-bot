# Construction Phase - Domain Model Design

## Overview

This directory contains the complete Domain-Driven Design (DDD) domain models for all five units of the System Support Web Application MVP.

---

## Deliverables

### Foundation Documents

1. **[ubiquitous_language.md](ubiquitous_language.md)**
   - Common vocabulary used across all bounded contexts
   - Core domain terms and definitions
   - Business rules and state transitions

2. **[bounded_contexts.md](bounded_contexts.md)**
   - Definition of all five bounded contexts
   - Context boundaries and responsibilities
   - Context map and relationships
   - Database schema strategy

3. **[integration_patterns.md](integration_patterns.md)**
   - Cross-context integration patterns
   - Domain event flows
   - Consistency boundaries
   - API contracts and error handling

### Unit Domain Models

4. **[unit1_chat_interface_service/domain_model.md](unit1_chat_interface_service/domain_model.md)**
   - Aggregates: Conversation (root), Message
   - Key value objects: ConversationStatus, Screenshot, Feedback
   - Domain events: ConversationCreated, MessageAdded, FeedbackSubmitted, ConversationEscalated
   - Domain services: ConversationHistoryService, ScreenshotValidationService

5. **[unit2_access_control_service/domain_model.md](unit2_access_control_service/domain_model.md)**
   - Aggregates: User (root), Session
   - Key value objects: Role, AccessLevel, Password, JWTToken
   - Domain events: UserAuthenticated, SessionCreated, SessionRevoked
   - Domain services: AuthenticationService, AuthorizationService, PasswordPolicyService

6. **[unit3_document_repository_service/domain_model.md](unit3_document_repository_service/domain_model.md)**
   - Aggregates: Document (root), SearchQuery (root)
   - Key value objects: DocumentAccessLevel, RelevanceScore, DocumentSource
   - Domain events: DocumentDiscovered, DocumentAccessed, SearchExecuted
   - Domain services: DocumentSearchService, RelevanceRankingService, DocumentMetadataRefreshService

7. **[unit4_ai_orchestration_service/domain_model.md](unit4_ai_orchestration_service/domain_model.md)**
   - Aggregates: AIQuery (root), ContextMessage
   - Key value objects: Intent, ConfidenceScore, AIResponse, Prompt
   - Domain events: QueryProcessed, LowConfidenceDetected, IntentDetected
   - Domain services: IntentDetectionService, PromptEngineeringService, ResponseGenerationService, ConfidenceCalculationService

8. **[unit5_communication_analytics_service/domain_model.md](unit5_communication_analytics_service/domain_model.md)**
   - Aggregates: EscalationEmail (root), AnalyticsEvent (root), Metric (root)
   - Key value objects: EmailStatus, EventType, MetricType, TimePeriod
   - Domain events: EscalationEmailSent, AnalyticsEventRecorded, MetricCalculated
   - Domain services: EmailCompositionService, MetricsCalculationService, DashboardDataService

---

## Architecture Diagrams

Additional PlantUML diagrams are available in the `/architecture` folder:

- **[layered-architecture-example.puml](../architecture/layered-architecture-example.puml)** - Shows domain, application, and infrastructure layers
- **[ai-query-processing-sequence.puml](../architecture/ai-query-processing-sequence.puml)** - Sequence diagram for AI query processing
- **[hexagonal-architecture.puml](../architecture/hexagonal-architecture.puml)** - Ports and adapters pattern

---

## Key Design Decisions

### 1. Persistence Strategy
- **Traditional state-based persistence** (not event sourcing)
- Single database with separate schemas per unit
- Domain events used for cross-context communication only

### 2. Service Types
- **Domain Services**: Contain core business logic (e.g., AuthenticationService, RelevanceRankingService)
- **Application Services**: Orchestrate workflows across contexts (e.g., ProcessAIQueryApplicationService)

### 3. External Systems
- **Infrastructure adapters** (not anti-corruption layers)
- External systems: S3, Confluence, AWS Bedrock
- Simple adapters sufficient for MVP

### 4. Technology Stack
- Python and JavaScript
- PostgreSQL with schema-per-unit
- JWT-based authentication

### 5. Integration Patterns
- **Synchronous**: REST APIs for request-response
- **Asynchronous**: Domain events for analytics and notifications
- **Shared Kernel**: Access Control Context consumed by all

---

## Bounded Context Summary

| Context | Aggregate Roots | Key Responsibilities |
|---------|----------------|---------------------|
| **Chat Interface** | Conversation | Manage conversations, messages, feedback |
| **Access Control** | User | Authentication, authorization, sessions |
| **Document Repository** | Document, SearchQuery | Search documents, manage metadata |
| **AI Orchestration** | AIQuery | Process queries, orchestrate AI responses |
| **Communication & Analytics** | EscalationEmail, AnalyticsEvent, Metric | Send emails, track analytics |

---

## Domain Events Flow

```
Chat Interface → Communication & Analytics
├── ConversationCreated
├── MessageAdded
├── FeedbackSubmitted
└── ConversationEscalated

AI Orchestration → Communication & Analytics
├── QueryProcessed
├── LowConfidenceDetected
└── IntentDetected

Document Repository → Communication & Analytics
├── DocumentAccessed
└── SearchExecuted

Access Control → Communication & Analytics
├── UserAuthenticated
└── SessionRevoked
```

---

## Business Rules Highlights

### Conversation Rules
- Conversations retained for 30 days
- Context limited to last 5 messages
- Maximum 5 documentation links per response
- One screenshot per message (5MB limit)

### Access Control Rules
- Two roles: End User, Administrator
- End Users: BASIC access level (public, basic documents)
- Administrators: ALL access level (all documents)
- Sessions expire: 1 hour (access token), 7 days (refresh token)

### Document Rules
- Search across S3 and Confluence
- Results ranked by relevance (keyword 60%, recency 20%, popularity 20%)
- Maximum 50 results per query
- Results cached for 5 minutes

### AI Processing Rules
- Confidence threshold: 0.5 (suggest escalation if below)
- Processing time target: < 5 seconds for 90% of queries
- Temperature: 0.3 (focused responses)
- Maximum 500 tokens per response

### Analytics Rules
- Events retained for 30 days
- Metrics calculated daily
- Dashboard shows last 30 days (fixed)
- Escalation emails: max 10 per hour per user

---

## Next Steps

With domain models complete, the next phase is:

1. **Technical Design**: Define database schemas, API specifications, infrastructure components
2. **Implementation**: Build each unit following the domain models
3. **Testing**: Unit tests for domain logic, integration tests for cross-context flows
4. **Deployment**: Set up CI/CD pipelines and deploy to environments

---

## Notes

- All domain models are technology-agnostic where possible
- No code snippets included (as per requirements)
- Focus on business logic and domain rules
- Infrastructure concerns noted but not detailed
- MVP scope maintained throughout

---

**Version:** 1.0  
**Date:** January 27, 2026  
**Status:** Complete
