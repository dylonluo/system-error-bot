# Domain Model - Unit 1: Chat Interface Service

## Document Information
**Bounded Context:** Chat Interface Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Technology:** Python/JavaScript  
**Database Schema:** `chat_interface`

---

## Bounded Context Definition

**Purpose:** Manage user conversations, message flow, and feedback collection for the chat-style interface.

**Responsibilities:**
- Create and manage conversations
- Store and retrieve messages
- Handle screenshot attachments
- Collect user feedback
- Trigger escalation to human support
- Maintain conversation history (30 days)

**What This Context Does NOT Do:**
- Process AI queries (delegates to AI Orchestration Context)
- Authenticate users (delegates to Access Control Context)
- Send emails (delegates to Communication & Analytics Context)

---

## Aggregates

### 1. Conversation (Aggregate Root)

**Description:** Represents a thread of messages between a user and the AI assistant.

**Aggregate Root:** Conversation

**Entities:**
- Conversation (root)
- Message

**Value Objects:**
- ConversationId
- ConversationStatus
- Screenshot
- Feedback

**Invariants:**
- A conversation must belong to exactly one user
- A conversation must have at least one message
- Messages within a conversation are ordered by timestamp
- A conversation can only be escalated once
- Feedback can only be submitted for assistant messages
- Screenshots must not exceed 5MB

**Lifecycle:**
- Created when user submits first query
- Active while user interacts
- Resolved when user marks problem as solved
- Escalated when user requests human support
- Deleted after 30 days of inactivity

---

## Entities

### Conversation (Aggregate Root)

**Identity:** ConversationId (UUID)

**Attributes:**
- conversationId: ConversationId
- userId: UserId (from Access Control Context)
- title: String (optional, derived from first message)
- status: ConversationStatus (active, resolved, escalated)
- createdAt: Timestamp
- updatedAt: Timestamp
- lastMessageAt: Timestamp

**Behaviors:**
- addMessage(content, role, screenshot): Message
- markAsResolved(): void
- escalateToSupport(reason): void
- canAddMessage(): boolean
- isOwnedBy(userId): boolean
- getRecentMessages(limit): List<Message>

**Business Rules:**
- Cannot add messages to escalated conversations
- Cannot escalate already escalated conversations
- Cannot resolve conversations with no messages
- Title is auto-generated from first 50 characters of first message

---

### Message (Entity within Conversation)

**Identity:** MessageId (UUID)

**Attributes:**
- messageId: MessageId
- conversationId: ConversationId
- role: MessageRole (user, assistant)
- content: String
- screenshot: Screenshot (optional, only for user messages)
- documentationLinks: List<DocumentationLink> (only for assistant messages)
- feedback: Feedback (optional, only for assistant messages)
- timestamp: Timestamp

**Behaviors:**
- submitFeedback(answeredQuestion, problemSolved): void
- hasFeedback(): boolean
- hasScreenshot(): boolean
- getDocumentationLinks(): List<DocumentationLink>

**Business Rules:**
- User messages can have screenshots, assistant messages cannot
- Assistant messages can have documentation links, user messages cannot
- Feedback can only be submitted once per message
- Content cannot be empty
- Messages are immutable after creation (except feedback)

---

## Value Objects

### ConversationId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### ConversationStatus

**Attributes:**
- value: Enum (ACTIVE, RESOLVED, ESCALATED)

**Behaviors:**
- isActive(): boolean
- isResolved(): boolean
- isEscalated(): boolean
- canTransitionTo(newStatus): boolean

**Invariants:**
- Valid transitions:
  - ACTIVE → RESOLVED
  - ACTIVE → ESCALATED
  - No transitions from RESOLVED or ESCALATED

---

### Screenshot

**Attributes:**
- filename: String
- content: Base64String (or file path)
- mimeType: String (image/jpeg, image/png)
- size: Integer (bytes)
- uploadedAt: Timestamp

**Behaviors:**
- isValidFormat(): boolean
- isWithinSizeLimit(): boolean
- getUrl(): String

**Invariants:**
- Size must not exceed 5MB (5,242,880 bytes)
- MIME type must be image/jpeg or image/png
- Filename must not be empty

---

### Feedback

**Attributes:**
- answeredQuestion: Boolean (Yes/No)
- problemSolved: Boolean (Solved/Not Solved)
- submittedAt: Timestamp

**Behaviors:**
- isPositive(): boolean
- wasHelpful(): boolean

**Invariants:**
- Both fields must be set
- Cannot be modified after submission

---

### DocumentationLink

**Attributes:**
- title: String
- url: String
- description: String
- source: String (s3, confluence)
- format: String (webpage, pdf)
- relevance: Float (0.0-1.0)

**Behaviors:**
- isAccessible(): boolean
- getDisplayText(): String

**Invariants:**
- URL must be valid
- Title must not be empty
- Relevance must be between 0.0 and 1.0

---

### MessageRole

**Attributes:**
- value: Enum (USER, ASSISTANT)

**Behaviors:**
- isUser(): boolean
- isAssistant(): boolean

---

## Domain Events

### ConversationCreated

**Attributes:**
- conversationId: ConversationId
- userId: UserId
- createdAt: Timestamp

**Triggered When:** User starts a new conversation

**Consumers:** Communication & Analytics Context (for analytics)

---

### MessageAdded

**Attributes:**
- conversationId: ConversationId
- messageId: MessageId
- role: MessageRole
- hasScreenshot: Boolean
- timestamp: Timestamp

**Triggered When:** User or assistant adds a message

**Consumers:** Communication & Analytics Context (for analytics)

---

### FeedbackSubmitted

**Attributes:**
- conversationId: ConversationId
- messageId: MessageId
- answeredQuestion: Boolean
- problemSolved: Boolean
- submittedAt: Timestamp

**Triggered When:** User submits feedback on a response

**Consumers:** Communication & Analytics Context (for metrics calculation)

---

### ConversationResolved

**Attributes:**
- conversationId: ConversationId
- userId: UserId
- resolvedAt: Timestamp

**Triggered When:** User marks conversation as resolved

**Consumers:** Communication & Analytics Context (for resolution rate)

---

### ConversationEscalated

**Attributes:**
- conversationId: ConversationId
- userId: UserId
- reason: String (optional)
- escalatedAt: Timestamp

**Triggered When:** User escalates to human support

**Consumers:** Communication & Analytics Context (for email sending and analytics)

---

## Repositories

### IConversationRepository

**Purpose:** Persist and retrieve Conversation aggregates

**Methods:**
- save(conversation: Conversation): void
- findById(conversationId: ConversationId): Conversation
- findByUserId(userId: UserId, limit: Integer, offset: Integer): List<Conversation>
- findRecentByUserId(userId: UserId, days: Integer): List<Conversation>
- delete(conversationId: ConversationId): void
- deleteOlderThan(days: Integer): Integer

**Implementation Notes:**
- Uses `chat_interface.conversations` and `chat_interface.messages` tables
- Implements optimistic locking for concurrent updates
- Lazy loads messages for performance

---

## Domain Services

### ConversationHistoryService

**Purpose:** Manage conversation history and retention policies

**Methods:**
- getConversationHistory(userId: UserId, limit: Integer): List<Conversation>
- cleanupOldConversations(): Integer
- canContinueConversation(conversationId: ConversationId, userId: UserId): Boolean

**Business Rules:**
- Conversations older than 30 days are automatically deleted
- Users can only access their own conversations
- Administrators can access all conversations

**Rationale:** This is a domain service because it operates on multiple Conversation aggregates and enforces retention policies.

---

### ScreenshotValidationService

**Purpose:** Validate screenshot uploads

**Methods:**
- validateScreenshot(screenshot: Screenshot): ValidationResult
- sanitizeFilename(filename: String): String

**Business Rules:**
- Maximum size: 5MB
- Allowed formats: JPEG, PNG
- Filename must be sanitized to prevent security issues

**Rationale:** This is a domain service because it contains business rules about screenshot validation that don't naturally belong to a single aggregate.

---

## Application Services

### SubmitQueryApplicationService

**Purpose:** Orchestrate the workflow of submitting a user query

**Responsibilities:**
1. Validate user authentication (call Access Control Context)
2. Validate screenshot if provided (call ScreenshotValidationService)
3. Create or retrieve conversation
4. Add user message to conversation
5. Call AI Orchestration Context to process query
6. Add assistant response to conversation
7. Publish MessageAdded events
8. Return response to user

**Not a Domain Service because:** It orchestrates across multiple contexts and handles infrastructure concerns.

---

### SubmitFeedbackApplicationService

**Purpose:** Orchestrate feedback submission

**Responsibilities:**
1. Validate user authentication
2. Retrieve conversation and message
3. Verify user owns the conversation
4. Submit feedback on message
5. Publish FeedbackSubmitted event
6. Return confirmation

---

### EscalateConversationApplicationService

**Purpose:** Orchestrate conversation escalation

**Responsibilities:**
1. Validate user authentication
2. Retrieve conversation
3. Verify user owns the conversation
4. Mark conversation as escalated
5. Call Communication & Analytics Context to send email
6. Publish ConversationEscalated event
7. Return confirmation

---

## Policies

### ConversationRetentionPolicy

**Rule:** Conversations older than 30 days must be deleted

**Implementation:** 
- Scheduled job runs daily
- Calls ConversationHistoryService.cleanupOldConversations()
- Publishes ConversationDeleted events

---

### FeedbackPolicy

**Rule:** Feedback can only be submitted once per message

**Implementation:**
- Message.submitFeedback() checks if feedback already exists
- Throws FeedbackAlreadySubmittedException if feedback exists

---

### EscalationPolicy

**Rule:** A conversation can only be escalated once

**Implementation:**
- Conversation.escalateToSupport() checks current status
- Throws ConversationAlreadyEscalatedException if already escalated

---

## Business Rules Summary

### Conversation Rules
1. A conversation must belong to exactly one user
2. A conversation must have at least one message
3. Messages are ordered by timestamp
4. Conversations are retained for 30 days only
5. Users can only access their own conversations (except administrators)
6. A conversation can only be escalated once
7. Cannot add messages to escalated conversations

### Message Rules
1. User messages can have screenshots, assistant messages cannot
2. Assistant messages can have documentation links, user messages cannot
3. Messages are immutable after creation (except feedback)
4. Content cannot be empty
5. Maximum 5 documentation links per assistant message

### Screenshot Rules
1. Maximum size: 5MB
2. Allowed formats: JPEG, PNG only
3. One screenshot per user message

### Feedback Rules
1. Feedback can only be submitted for assistant messages
2. Feedback can only be submitted once per message
3. Both answeredQuestion and problemSolved must be provided

---

## Aggregate Relationships

```
Conversation (Aggregate Root)
├── conversationId: ConversationId (identity)
├── userId: UserId (reference to Access Control Context)
├── status: ConversationStatus (value object)
├── Messages (entities, 1-to-many)
│   ├── Message 1
│   │   ├── messageId: MessageId
│   │   ├── role: MessageRole
│   │   ├── content: String
│   │   ├── screenshot: Screenshot (value object, optional)
│   │   ├── documentationLinks: List<DocumentationLink> (value objects)
│   │   └── feedback: Feedback (value object, optional)
│   ├── Message 2
│   └── Message N
└── Timestamps (createdAt, updatedAt, lastMessageAt)
```

---

## Consistency Boundaries

**Strong Consistency (within aggregate):**
- All changes to messages within a conversation are immediately consistent
- Feedback submission is atomic with message update

**Eventual Consistency (across aggregates):**
- Analytics events are published asynchronously
- Email escalation is asynchronous
- Conversation history queries may have slight delay

---

## Integration Points

### Inbound (APIs this context provides)

**REST Endpoints:**
- POST /api/v1/chat/conversations - Create conversation
- POST /api/v1/chat/conversations/{id}/messages - Submit query
- GET /api/v1/chat/conversations/{id} - Get conversation
- GET /api/v1/chat/conversations - List user's conversations
- POST /api/v1/chat/conversations/{id}/feedback - Submit feedback
- POST /api/v1/chat/conversations/{id}/escalate - Escalate conversation

### Outbound (APIs this context consumes)

**Access Control Context:**
- POST /api/v1/auth/validate - Validate user token
- GET /api/v1/auth/users/{userId} - Get user profile

**AI Orchestration Context:**
- POST /api/v1/ai/process-query - Process user query

**Communication & Analytics Context:**
- POST /api/v1/communication/send-escalation-email - Send escalation email
- POST /api/v1/communication/analytics/record-event - Record analytics event

---

## Infrastructure Concerns

**Not part of domain model, but noted for completeness:**

- Screenshot storage (file system or S3)
- Database persistence (PostgreSQL with `chat_interface` schema)
- Event publishing (message queue or event bus)
- API authentication (JWT token validation)
- Rate limiting
- Logging and monitoring

---

## Notes

- This domain model focuses on business logic and rules
- Infrastructure details are intentionally omitted
- External system integration is handled via application services
- Domain events enable loose coupling with other contexts
- Aggregate boundaries ensure consistency and encapsulation

