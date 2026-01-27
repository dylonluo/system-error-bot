# Domain Model & Logical Design Refinement Summary

## Document Information
**Purpose:** Summary of clarifications and refinements made to domain models and logical designs  
**Date:** January 27, 2026  
**Scope:** All 5 units - clarification only, no new features or bounded context changes

---

## Unit 1 — Chat Interface Service

### Refinements Made

**1. Conversation Creation Strategy (CLARIFIED)**
- **Decision**: Implicit creation on first message submission
- **No explicit "create conversation" endpoint** - conversation created automatically when user submits first message with conversationId=null
- ConversationId generated server-side and returned in response
- Subsequent messages reference the returned ConversationId
- **API Impact**: Removed POST /api/v1/chat/conversations endpoint
- **DTO Impact**: SubmitMessageRequest now includes optional conversationId field

**2. Screenshot Value Object (CLARIFIED)**
- **Purpose**: Metadata + storage reference only, NOT binary content
- **Attributes**: filename, storageUrl (not content/base64), mimeType, size, uploadedAt
- **Separation**: Binary content stored in infrastructure layer (file system/S3)
- Screenshot value object contains reference (URL) to stored file

**3. ConversationDeleted Event (CLARIFIED)**
- **Status**: Formal domain event (not just infrastructure deletion)
- **Purpose**: Published for audit trail and cleanup coordination
- **Attributes**: conversationId, userId, deletedAt, reason (retention_policy, user_request)
- **Consumers**: Communication & Analytics Context for cleanup

**4. Message Ordering Rules (DOCUMENTED)**
- **Rule**: Messages ordered by timestamp (ascending) within conversation
- **Deterministic**: Timestamp assigned server-side on message creation
- **First message behavior**: Explicitly documented in API flows and application service

**5. First-Message Behavior (DOCUMENTED)**
- **API behavior**: If conversationId is null → create new conversation
- **API behavior**: If conversationId provided → retrieve existing, validate ownership
- **Event**: ConversationCreated published only on first message
- **Response**: Always includes conversationId for client to use in subsequent messages

---

## Unit 2 — Access Control Service

### Refinements Made

**1. MVP Authorization Scope (CLARIFIED)**
- **MVP scope**: Two roles (END_USER, ADMINISTRATOR), two access levels (BASIC, ALL)
- **Document filtering**: Based on access level (public, basic, advanced)
- **Feature access**: Conversation ownership, dashboard access (admin only)
- **Future-ready**: User, Role, Permission entities designed to support fine-grained RBAC post-MVP
- **No expansion in MVP**: Simple role-based model sufficient

**2. Session Activity Updates (CLARIFIED)**
- **Single responsibility**: Session.updateActivity() called on each validated API call
- **Ownership**: Access Control Service owns session activity tracking
- **Not delegated**: Other services do not update session activity directly
- **Implementation**: ValidateTokenApplicationService updates lastActivityAt timestamp

**3. Token Validation Strategy (CLARIFIED)**
- **MVP approach**: Local verification using JWT signature and secret key
- **Process**: Decode token → verify signature → check expiration → check session revocation in DB → verify user active
- **No remote calls**: Self-contained validation (no external service dependency)
- **Future consideration**: Remote validation service for distributed token revocation

**4. Shared Kernel Contract Stability (DOCUMENTED)**
- **Stable contracts**: User, Role, AccessLevel value objects are stable interfaces
- **Change coordination**: Any changes to these contracts require coordination with all consuming contexts
- **Versioning**: Consider versioning strategy if contracts must evolve
- **Documentation**: Explicitly noted in domain model notes section

---

## Unit 3 — Document Repository Service

### Refinements Made

**1. Orchestration-Only Clarification (DOCUMENTED)**
- **Role**: Gateway to external document systems (S3, Confluence)
- **No business rules**: Beyond search relevance and caching logic
- **Orchestration**: Coordinates document search, metadata caching, relevance ranking
- **Delegation**: Access control delegated to Unit 2, no domain rules enforced here

---

## Unit 4 — AI Orchestration Service

### Refinements Made

**1. Prompt Construction vs Model Invocation (SEPARATED)**
- **Prompt construction**: Domain logic in PromptEngineeringService
  - Builds system prompts, user prompts, adds context
  - Contains business rules for prompt formatting
  - Versioned prompt templates
- **Model invocation**: Infrastructure concern in IAIProvider adapters
  - Handles actual API calls to Bedrock, OpenAI
  - Manages retries, timeouts, circuit breakers
  - No domain logic in adapters

**2. Model Configuration Versioning (INTRODUCED)**
- **Prompt versioning**: Each prompt template has version identifier (v1.0, v1.1, etc.)
- **Model config tracking**: Model name, temperature, max tokens tracked with each query
- **Audit trail**: Version stored with AIQuery for debugging and rollback
- **A/B testing ready**: Can compare performance across prompt versions

**3. Retry, Timeout, and Fallback Behavior (DOCUMENTED)**
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s) on transient failures
- **Timeout**: AI calls timeout after 10 seconds
- **Fallback**: Primary (Bedrock) → Secondary (OpenAI) if primary fails
- **Circuit breaker**: If provider fails 10 times in 5 minutes, circuit opens for 1 minute
- **Implementation**: All in infrastructure layer (IAIProvider adapters), not domain

**4. Orchestration-Only Assertion (CLARIFIED)**
- **No business rules**: This service orchestrates AI processing but does NOT implement business rules
- **Domain logic**: Limited to prompt engineering, intent detection, confidence calculation
- **Business rules**: Belong in Chat Interface (conversation management) or other units
- **Role**: Pure orchestration of AI and document search

**5. Observability Metrics (SPECIFIED)**
- **Latency**: Total processing time, AI call time, document search time
- **Tokens**: Input tokens, output tokens, total tokens per query
- **Failures**: AI service errors, timeout count, fallback usage count
- **Cost**: Per-query cost in USD, daily/monthly aggregates
- **Storage**: Metrics stored with each AIQuery for analysis

---

## Unit 5 — Communication & Analytics Service

### Refinements Made

**1. Read-Only Nature (EXPLICITLY MARKED)**
- **No write-back**: This unit consumes events from other units but never writes back to them
- **Event-driven**: Purely event-driven data collection
- **Append-only**: Analytics events are immutable, append-only log
- **Dashboard**: Read-only views of aggregated data

**2. Domain Events Consumed (LISTED)**
- ConversationCreated (Chat Interface)
- MessageAdded (Chat Interface)
- FeedbackSubmitted (Chat Interface)
- ConversationEscalated (Chat Interface)
- QueryProcessed (AI Orchestration)
- UserAuthenticated (Access Control)
- DocumentAccessed (Document Repository)

**3. Data Freshness & Consistency Guarantees (DEFINED)**
- **Event processing**: Near real-time (within seconds)
- **Metrics calculation**: Daily batch at midnight UTC
- **Dashboard data**: Up to 24 hours stale (acceptable for MVP)
- **Eventual consistency**: Analytics may lag source systems by seconds to minutes
- **No strong consistency**: Analytics are informational, not transactional

**4. KPI and Metric Definitions (STANDARDIZED)**
- **Total Queries**: Count of QUERY_SUBMITTED events
- **Resolution Rate**: (problemSolved=true feedback / total feedback) * 100
- **Escalation Count**: Count of ESCALATION_TRIGGERED events
- **Active Users**: Distinct userIds with QUERY_SUBMITTED events
- **Top Queries**: Most frequent query texts (grouped, top 10)
- **Average Response Time**: Mean time between query and first feedback

**5. Event Replay and Historical Backfill (DOCUMENTED)**
- **Replay capability**: Metrics can be recalculated from event log for any period
- **Backfill process**: If metrics missing, replay events from that period
- **Idempotent**: Recalculating same period produces same results
- **Event sourcing**: All metrics derived from immutable event log

**6. Ownership & Immutability (CLARIFIED)**
- **EscalationEmail ownership**: Aggregate owns email lifecycle and delivery status
- **Email immutability**: Once sent successfully, content is immutable
- **Audit trail**: All state changes recorded with timestamps
- **AnalyticsEvent immutability**: Events never modified after creation (append-only)
- **Retention-based deletion**: Events deleted in batch after 30 days, not individually

---

## Cross-Cutting Refinements

### Integration Patterns
- **Synchronous REST**: For request-response operations (authentication, document search, AI processing)
- **Asynchronous events**: For analytics, escalation notifications
- **No direct DB access**: All cross-context data access via APIs only

### Consistency Boundaries
- **Strong consistency**: Within aggregates (immediate)
- **Eventual consistency**: Across aggregates and contexts (acceptable lag)
- **Analytics**: Explicitly eventual (up to 24 hours stale acceptable)

### Error Handling
- **Retry strategies**: Documented for each external integration
- **Fallback behavior**: Documented for AI providers
- **Circuit breakers**: Documented for high-failure scenarios

---

## What Was NOT Changed

### Bounded Contexts
- ✅ No changes to bounded context boundaries
- ✅ No new units introduced
- ✅ No units merged or split

### User-Facing Features
- ✅ No new features added
- ✅ No features removed
- ✅ All existing responsibilities preserved

### Responsibilities
- ✅ All existing responsibilities maintained
- ✅ No responsibility transfers between units
- ✅ Clear boundaries preserved

---

## Implementation Readiness

### Clarifications Achieved
- ✅ Conversation creation strategy: Implicit on first message
- ✅ Screenshot handling: Metadata + storage reference
- ✅ Token validation: Local verification
- ✅ Session activity: Owned by Access Control
- ✅ Prompt vs invocation: Separated concerns
- ✅ Retry/timeout/fallback: Fully documented
- ✅ Analytics read-only: Explicitly marked
- ✅ Event replay: Documented capability
- ✅ KPI definitions: Standardized

### Ambiguities Removed
- ✅ First message behavior: Fully specified
- ✅ Message ordering: Deterministic rules
- ✅ ConversationDeleted: Formal event, not just infra
- ✅ MVP authorization scope: Clearly bounded
- ✅ Shared kernel stability: Documented
- ✅ Orchestration-only: Clarified for Units 3 & 4
- ✅ Data freshness: Guarantees specified
- ✅ Immutability: Clarified for emails and events

### Ready for Implementation
- ✅ All domain models have clear invariants
- ✅ All aggregates have defined lifecycles
- ✅ All integration points documented
- ✅ All error handling strategies specified
- ✅ All observability metrics defined
- ✅ All consistency guarantees stated

---

## Notes

- This refinement focused on **clarification and alignment**, not redesign
- All changes are **backward compatible** with existing design
- No new features or bounded contexts introduced
- Implementation can proceed with confidence
- All ambiguities resolved for MVP scope
