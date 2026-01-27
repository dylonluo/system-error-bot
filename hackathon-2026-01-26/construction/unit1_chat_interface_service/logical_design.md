# Logical Design - Unit 1: Chat Interface Service

## Document Information
**Bounded Context:** Chat Interface Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Architecture Style:** Simplified Layered Architecture  
**Technology Stack:** Python/FastAPI or Node.js/Express (framework-agnostic design)

---

## 1. Architecture Overview

### 1.1 Architectural Style
**Simplified Layered Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  (REST Controllers, Request/Response DTOs)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Application Service Layer                 │
│  (Use Case Orchestration, Cross-Context Coordination)    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Domain Layer                           │
│  (Aggregates, Entities, Value Objects, Domain Services)  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                      │
│  (Repositories, External API Clients, File Storage)      │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles
- **Dependency Rule:** Dependencies flow downward (API → Application → Domain → Infrastructure)
- **Domain Isolation:** Business logic concentrated in domain layer
- **Single Responsibility:** Each layer has one clear purpose
- **Interface Segregation:** Repositories defined as interfaces in domain, implemented in infrastructure

---

## 2. Component Structure

### 2.1 API Layer Components

#### REST Controllers

**ConversationController**
- **Responsibility:** Handle HTTP requests for conversation operations
- **Endpoints:**
  - `POST /api/v1/chat/conversations` → createConversation()
  - `GET /api/v1/chat/conversations` → listConversations()
  - `GET /api/v1/chat/conversations/{id}` → getConversation()
  - `POST /api/v1/chat/conversations/{id}/escalate` → escalateConversation()

**MessageController**
- **Responsibility:** Handle HTTP requests for message operations
- **Endpoints:**
  - `POST /api/v1/chat/conversations/{id}/messages` → submitMessage()
  - `POST /api/v1/chat/conversations/{id}/feedback` → submitFeedback()

#### DTOs (Data Transfer Objects)

**Request DTOs:**
- CreateConversationRequest
- SubmitMessageRequest (includes query text, optional screenshot)
- SubmitFeedbackRequest
- EscalateConversationRequest

**Response DTOs:**
- ConversationResponse
- MessageResponse
- ConversationListResponse
- FeedbackResponse
- EscalationResponse

---

### 2.2 Application Service Layer Components

#### Application Services

**SubmitQueryApplicationService**
- **Responsibility:** Orchestrate query submission workflow
- **Key Operations:**
  - validateAuthentication() - Call Access Control Context
  - validateScreenshot() - Call ScreenshotValidationService
  - getOrCreateConversation() - Retrieve or create conversation
  - addUserMessage() - Add message to conversation
  - processQuery() - Call AI Orchestration Context
  - addAssistantResponse() - Add AI response to conversation
  - publishEvents() - Publish MessageAdded events
  - recordAnalytics() - Call Communication & Analytics Context

**SubmitFeedbackApplicationService**
- **Responsibility:** Orchestrate feedback submission
- **Key Operations:**
  - validateAuthentication()
  - retrieveConversation()
  - verifyOwnership()
  - submitFeedback()
  - publishFeedbackEvent()
  - recordAnalytics()

**EscalateConversationApplicationService**
- **Responsibility:** Orchestrate conversation escalation
- **Key Operations:**
  - validateAuthentication()
  - retrieveConversation()
  - verifyOwnership()
  - markAsEscalated()
  - sendEscalationEmail() - Call Communication & Analytics Context
  - publishEscalationEvent()
  - recordAnalytics()

**GetConversationApplicationService**
- **Responsibility:** Retrieve conversation with authorization
- **Key Operations:**
  - validateAuthentication()
  - retrieveConversation()
  - verifyOwnership()
  - returnConversation()

**ListConversationsApplicationService**
- **Responsibility:** List user's conversations
- **Key Operations:**
  - validateAuthentication()
  - retrieveUserConversations()
  - applyPagination()
  - returnConversationList()

#### External Service Clients

**AccessControlClient**
- **Responsibility:** Communicate with Access Control Context
- **Operations:**
  - validateToken(token) → User
  - getUserProfile(userId) → User

**AIOrchestrationClient**
- **Responsibility:** Communicate with AI Orchestration Context
- **Operations:**
  - processQuery(query, context, userId) → AIResponse

**CommunicationAnalyticsClient**
- **Responsibility:** Communicate with Communication & Analytics Context
- **Operations:**
  - sendEscalationEmail(conversationId, userId, history) → EmailConfirmation
  - recordEvent(eventType, metadata) → EventConfirmation

---

### 2.3 Domain Layer Components

#### Aggregates

**Conversation (Aggregate Root)**
- **Identity:** ConversationId
- **Entities:** Message (collection)
- **Value Objects:** ConversationStatus, Screenshot, Feedback
- **Key Methods:**
  - addMessage(content, role, screenshot) → Message
  - markAsResolved() → void
  - escalateToSupport(reason) → void
  - canAddMessage() → boolean
  - isOwnedBy(userId) → boolean
  - getRecentMessages(limit) → List<Message>

#### Entities

**Message**
- **Identity:** MessageId
- **Attributes:** role, content, screenshot, documentationLinks, feedback, timestamp
- **Key Methods:**
  - submitFeedback(answeredQuestion, problemSolved) → void
  - hasFeedback() → boolean
  - hasScreenshot() → boolean

#### Value Objects

**ConversationId** - UUID wrapper
**MessageId** - UUID wrapper
**ConversationStatus** - Enum (ACTIVE, RESOLVED, ESCALATED)
**Screenshot** - filename, content, mimeType, size, uploadedAt
**Feedback** - answeredQuestion, problemSolved, submittedAt
**DocumentationLink** - title, url, description, source, format, relevance
**MessageRole** - Enum (USER, ASSISTANT)

#### Domain Services

**ConversationHistoryService**
- **Responsibility:** Manage conversation history and retention
- **Operations:**
  - getConversationHistory(userId, limit) → List<Conversation>
  - cleanupOldConversations() → Integer
  - canContinueConversation(conversationId, userId) → Boolean

**ScreenshotValidationService**
- **Responsibility:** Validate screenshot uploads
- **Operations:**
  - validateScreenshot(screenshot) → ValidationResult
  - sanitizeFilename(filename) → String

#### Domain Events

- ConversationCreated
- MessageAdded
- FeedbackSubmitted
- ConversationResolved
- ConversationEscalated

---

### 2.4 Infrastructure Layer Components

#### Repositories

**ConversationRepository (implements IConversationRepository)**
- **Responsibility:** Persist and retrieve Conversation aggregates
- **Operations:**
  - save(conversation) → void
  - findById(conversationId) → Conversation
  - findByUserId(userId, limit, offset) → List<Conversation>
  - findRecentByUserId(userId, days) → List<Conversation>
  - delete(conversationId) → void
  - deleteOlderThan(days) → Integer
- **Implementation:** PostgreSQL with `chat_interface` schema

#### File Storage

**ScreenshotStorageService**
- **Responsibility:** Store and retrieve screenshot files
- **Operations:**
  - store(screenshot) → String (URL)
  - retrieve(url) → Screenshot
  - delete(url) → void
- **Implementation:** Local file system or S3

#### Event Publisher

**EventPublisher**
- **Responsibility:** Publish domain events
- **Operations:**
  - publish(event) → void
- **Implementation:** Message queue (RabbitMQ/Redis) or HTTP webhooks

---

## 3. Data Flow Diagrams

### 3.1 Submit Query Flow

```
User Request
    ↓
ConversationController.submitMessage()
    ↓
SubmitQueryApplicationService.execute()
    ├─→ AccessControlClient.validateToken()
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return User
    ├─→ ScreenshotValidationService.validate() (if screenshot present)
    ├─→ ConversationRepository.findById() or create new
    ├─→ Conversation.addMessage(userContent, USER, screenshot)
    ├─→ ConversationRepository.save()
    ├─→ AIOrchestrationClient.processQuery()
    │       ↓
    │   [AI Orchestration Context]
    │       ↓
    │   Return AIResponse with DocumentationLinks
    ├─→ Conversation.addMessage(aiContent, ASSISTANT, links)
    ├─→ ConversationRepository.save()
    ├─→ EventPublisher.publish(MessageAdded)
    ├─→ CommunicationAnalyticsClient.recordEvent()
    ↓
Return MessageResponse to User
```

### 3.2 Escalate Conversation Flow

```
User Request
    ↓
ConversationController.escalateConversation()
    ↓
EscalateConversationApplicationService.execute()
    ├─→ AccessControlClient.validateToken()
    ├─→ ConversationRepository.findById()
    ├─→ Conversation.isOwnedBy(userId) - verify ownership
    ├─→ Conversation.escalateToSupport(reason)
    ├─→ ConversationRepository.save()
    ├─→ CommunicationAnalyticsClient.sendEscalationEmail()
    │       ↓
    │   [Communication & Analytics Context]
    │       ↓
    │   Return EmailConfirmation
    ├─→ EventPublisher.publish(ConversationEscalated)
    ├─→ CommunicationAnalyticsClient.recordEvent()
    ↓
Return EscalationResponse to User
```

### 3.3 Submit Feedback Flow

```
User Request
    ↓
MessageController.submitFeedback()
    ↓
SubmitFeedbackApplicationService.execute()
    ├─→ AccessControlClient.validateToken()
    ├─→ ConversationRepository.findById()
    ├─→ Conversation.isOwnedBy(userId)
    ├─→ Message.submitFeedback(answeredQuestion, problemSolved)
    ├─→ ConversationRepository.save()
    ├─→ EventPublisher.publish(FeedbackSubmitted)
    ├─→ CommunicationAnalyticsClient.recordEvent()
    ↓
Return FeedbackResponse to User
```

---

## 4. Database Schema Design

### 4.1 Schema: `chat_interface`

#### Table: `conversations`
```
conversations
├── conversation_id (UUID, PK)
├── user_id (UUID, FK to access_control.users)
├── title (VARCHAR(500), nullable)
├── status (ENUM: active, resolved, escalated)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
├── last_message_at (TIMESTAMP)
└── INDEX on user_id, INDEX on status, INDEX on last_message_at
```

#### Table: `messages`
```
messages
├── message_id (UUID, PK)
├── conversation_id (UUID, FK to conversations)
├── role (ENUM: user, assistant)
├── content (TEXT)
├── screenshot_filename (VARCHAR(255), nullable)
├── screenshot_url (VARCHAR(500), nullable)
├── screenshot_mime_type (VARCHAR(50), nullable)
├── screenshot_size (INTEGER, nullable)
├── timestamp (TIMESTAMP)
└── INDEX on conversation_id, INDEX on timestamp
```

#### Table: `documentation_links`
```
documentation_links
├── link_id (UUID, PK)
├── message_id (UUID, FK to messages)
├── title (VARCHAR(500))
├── url (VARCHAR(1000))
├── description (TEXT)
├── source (ENUM: s3, confluence)
├── format (ENUM: webpage, pdf)
├── relevance (DECIMAL(3,2))
└── INDEX on message_id
```

#### Table: `feedback`
```
feedback
├── feedback_id (UUID, PK)
├── message_id (UUID, FK to messages, UNIQUE)
├── answered_question (BOOLEAN)
├── problem_solved (BOOLEAN)
├── submitted_at (TIMESTAMP)
└── INDEX on message_id
```

### 4.2 Relationships
- One Conversation has many Messages (1:N)
- One Message (assistant) has many DocumentationLinks (1:N)
- One Message (assistant) has one Feedback (1:1, optional)

---

## 5. API-to-Component Mapping

### 5.1 Endpoint Mappings

| HTTP Method | Endpoint | Controller | Application Service | Domain Aggregate |
|-------------|----------|------------|---------------------|------------------|
| POST | /api/v1/chat/conversations | ConversationController | SubmitQueryApplicationService | Conversation |
| GET | /api/v1/chat/conversations | ConversationController | ListConversationsApplicationService | Conversation |
| GET | /api/v1/chat/conversations/{id} | ConversationController | GetConversationApplicationService | Conversation |
| POST | /api/v1/chat/conversations/{id}/messages | MessageController | SubmitQueryApplicationService | Conversation, Message |
| POST | /api/v1/chat/conversations/{id}/feedback | MessageController | SubmitFeedbackApplicationService | Message |
| POST | /api/v1/chat/conversations/{id}/escalate | ConversationController | EscalateConversationApplicationService | Conversation |

---

## 6. Integration Points

### 6.1 Outbound Integrations

**Access Control Context (Synchronous REST)**
- Endpoint: `POST /api/v1/auth/validate`
- Purpose: Validate JWT token and get user info
- Trigger: Every authenticated request
- Error Handling: Return 401 if token invalid

**AI Orchestration Context (Synchronous REST)**
- Endpoint: `POST /api/v1/ai/process-query`
- Purpose: Process user query and get AI response
- Trigger: When user submits message
- Error Handling: Return 500 if AI service unavailable, suggest retry

**Communication & Analytics Context (Asynchronous + Synchronous)**
- Endpoint: `POST /api/v1/communication/send-escalation-email` (Synchronous)
- Purpose: Send escalation email
- Trigger: When user escalates conversation
- Error Handling: Return error if email fails, allow retry

- Endpoint: `POST /api/v1/communication/analytics/record-event` (Asynchronous)
- Purpose: Record analytics events
- Trigger: After domain events published
- Error Handling: Fire-and-forget, log failures

### 6.2 Inbound Integrations

**None** - This is the entry point for users (no upstream dependencies)

---

## 7. Error Handling Strategy

### 7.1 Error Categories

**Validation Errors (400 Bad Request)**
- Empty query text
- Screenshot exceeds 5MB
- Invalid conversation ID format
- Missing required fields

**Authentication Errors (401 Unauthorized)**
- Invalid JWT token
- Expired token
- Missing Authorization header

**Authorization Errors (403 Forbidden)**
- User doesn't own conversation
- User trying to access another user's data

**Not Found Errors (404 Not Found)**
- Conversation not found
- Message not found

**Business Rule Violations (409 Conflict)**
- Feedback already submitted
- Conversation already escalated
- Cannot add message to escalated conversation

**External Service Errors (500/503)**
- AI Orchestration service unavailable
- Database connection failure
- Email service failure

### 7.2 Error Response Format

```
{
  "error": {
    "code": "CONVERSATION_NOT_FOUND",
    "message": "Conversation with ID xyz not found",
    "timestamp": "2026-01-27T10:30:00Z",
    "requestId": "req-uuid-123"
  }
}
```

### 7.3 Retry Strategy

**Transient Failures:**
- AI Orchestration timeout: Retry once after 2 seconds
- Database connection: Retry 3 times with exponential backoff
- Analytics event recording: Fire-and-forget, log failure

**Permanent Failures:**
- Validation errors: No retry, return error immediately
- Authorization errors: No retry, return error immediately

---

## 8. Security Considerations

### 8.1 Authentication
- All endpoints require valid JWT token (except health check)
- Token validated on every request via Access Control Context
- Token passed in `Authorization: Bearer {token}` header

### 8.2 Authorization
- Users can only access their own conversations
- Ownership verified before any operation
- Administrators can access all conversations (enforced by Access Control Context)

### 8.3 Input Validation
- Query text: 2-2000 characters
- Screenshot: Max 5MB, JPEG/PNG only
- Filename sanitization to prevent path traversal
- SQL injection prevention via parameterized queries

### 8.4 Data Protection
- Screenshots stored with unique UUIDs (no user-provided filenames)
- Conversation data encrypted at rest (database-level encryption)
- PII redacted in logs
- HTTPS/TLS for all API communication

### 8.5 Rate Limiting
- 60 requests per minute per user
- Enforced at API Gateway level
- Return 429 Too Many Requests if exceeded

---

## 9. Performance Considerations

### 9.1 Database Optimization
- Indexes on frequently queried fields (user_id, conversation_id, timestamp)
- Pagination for conversation list (limit/offset)
- Lazy loading of messages (not loaded with conversation list)
- Connection pooling for database connections

### 9.2 Caching Strategy
- No caching in MVP (conversations change frequently)
- Future: Cache user's recent conversations (5-minute TTL)

### 9.3 Asynchronous Processing
- Analytics event recording: Fire-and-forget
- Domain event publishing: Asynchronous
- Screenshot upload: Synchronous (blocking) in MVP

### 9.4 Response Time Targets
- List conversations: < 200ms
- Get conversation: < 300ms
- Submit query: < 5 seconds (includes AI processing)
- Submit feedback: < 100ms
- Escalate conversation: < 1 second

---

## 10. Deployment Considerations

### 10.1 Service Deployment
- Containerized application (Docker)
- Stateless service (horizontal scaling possible)
- Environment-specific configuration (dev, staging, prod)

### 10.2 Database Deployment
- PostgreSQL with `chat_interface` schema
- Automated migrations on deployment
- Backup strategy: Daily full backup, point-in-time recovery

### 10.3 File Storage Deployment
- MVP: Local file system with volume mount
- Future: S3 for scalability

### 10.4 Monitoring
- Health check endpoint: `GET /health`
- Metrics: Request count, response time, error rate
- Logging: Structured JSON logs with correlation IDs
- Alerts: High error rate, slow response times

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Domain layer: Test aggregates, entities, value objects, domain services
- Application layer: Test application services with mocked dependencies
- Coverage target: 80%+

### 11.2 Integration Tests
- API layer: Test REST endpoints with test database
- Repository layer: Test database operations
- External clients: Test with mocked external services

### 11.3 Contract Tests
- Verify API contracts match integration contract document
- Test request/response schemas
- Validate error responses

---

## 12. Future Enhancements (Post-MVP)

- WebSocket support for real-time updates
- Conversation search functionality
- Message editing/deletion
- Conversation export (PDF, JSON)
- Advanced analytics (conversation duration, message count)
- Conversation tagging and categorization
- Multi-language support

---

## Notes

- Design prioritizes simplicity and speed for MVP
- Clear separation of concerns enables easy testing
- External service clients abstracted for flexibility
- Domain logic isolated from infrastructure concerns
- Ready for horizontal scaling when needed
