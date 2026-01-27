# Domain Model - Unit 5: Communication & Analytics Service

## Document Information
**Bounded Context:** Communication & Analytics Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Technology:** Python/JavaScript  
**Database Schema:** `communication_analytics`

---

## Bounded Context Definition

**Purpose:** Handle email escalations to human support and track system usage analytics.

**Responsibilities:**
- Send escalation emails to support team
- Collect and store analytics events
- Calculate usage metrics
- Generate dashboard data for administrators
- Track resolution rates and query patterns

**What This Context Does NOT Do:**
- Own conversation data (reads from Chat Interface Context)
- Authenticate users (delegates to Access Control Context)
- Process queries (belongs to AI Orchestration Context)

---

## Aggregates

### 1. EscalationEmail (Aggregate Root)

**Description:** Represents an email sent to human support when a user escalates their issue.

**Aggregate Root:** EscalationEmail

**Entities:**
- EscalationEmail (root)

**Value Objects:**
- EmailId
- EmailAddress
- EmailContent
- EmailStatus
- ConversationSnapshot

**Invariants:**
- Must have valid recipient email address
- Must include conversation history
- Must include user information
- Email can only be sent once
- Delivery status must be tracked

**Lifecycle:**
- Created when user escalates conversation
- Queued for sending
- Sent via email service
- Delivery confirmed or failed
- Retained for audit (90 days)

---

### 2. AnalyticsEvent (Aggregate Root)

**Description:** Represents a recorded event in the system for analytics purposes.

**Aggregate Root:** AnalyticsEvent

**Entities:**
- AnalyticsEvent (root)

**Value Objects:**
- EventId
- EventType
- EventMetadata

**Invariants:**
- Event type must be valid
- Event must have timestamp
- Metadata must be valid JSON
- Events are immutable after creation

**Lifecycle:**
- Created when system event occurs
- Stored in event log
- Aggregated for metrics calculation
- Retained for 30 days
- Deleted after retention period

---

### 3. Metric (Aggregate Root)

**Description:** Represents a calculated metric for the analytics dashboard.

**Aggregate Root:** Metric

**Entities:**
- Metric (root)
- MetricDataPoint

**Value Objects:**
- MetricId
- MetricType
- MetricValue
- TimePeriod

**Invariants:**
- Metric must have a type and value
- Time period must be valid (30 days for MVP)
- Metrics recalculated daily
- Historical data points retained

**Lifecycle:**
- Calculated from analytics events
- Updated daily via scheduled job
- Stored for historical tracking
- Displayed on dashboard

---

## Entities

### EscalationEmail (Aggregate Root)

**Identity:** EmailId (UUID)

**Attributes:**
- emailId: EmailId
- conversationId: ConversationId (from Chat Interface)
- userId: UserId (from Access Control)
- recipientEmail: EmailAddress
- subject: String
- content: EmailContent
- conversationSnapshot: ConversationSnapshot
- screenshots: List<Screenshot>
- status: EmailStatus (queued, sent, failed)
- sentAt: Timestamp
- deliveryConfirmedAt: Timestamp
- failureReason: String (optional)
- retryCount: Integer

**Behaviors:**
- send(): void
- markAsSent(): void
- markAsFailed(reason): void
- retry(): void
- canRetry(): Boolean
- getConversationHistory(): String

**Business Rules:**
- Maximum 3 retry attempts
- Retry delay: exponential backoff (1min, 5min, 15min)
- Email content must include conversation history
- Screenshots attached if present
- Rate limit: 10 emails per hour per user
- Subject format: "Support Escalation - [ConversationId]"

---

### AnalyticsEvent (Aggregate Root)

**Identity:** EventId (UUID)

**Attributes:**
- eventId: EventId
- eventType: EventType
- userId: UserId
- conversationId: ConversationId (optional)
- metadata: EventMetadata
- occurredAt: Timestamp

**Behaviors:**
- getMetadata(key): String
- hasMetadata(key): Boolean
- toJSON(): String

**Business Rules:**
- Events are immutable
- Metadata stored as JSON
- Events retained for 30 days
- Events processed asynchronously

---

### Metric (Aggregate Root)

**Identity:** MetricId (UUID)

**Attributes:**
- metricId: MetricId
- metricType: MetricType
- value: MetricValue
- timePeriod: TimePeriod
- calculatedAt: Timestamp
- dataPoints: List<MetricDataPoint>

**Behaviors:**
- calculate(): void
- addDataPoint(value, timestamp): void
- getValue(): MetricValue
- getTrend(): String (increasing, decreasing, stable)

**Business Rules:**
- Metrics calculated daily at midnight
- Time period: last 30 days for MVP
- Historical data points retained for trending

---

### MetricDataPoint (Entity within Metric)

**Identity:** DataPointId (UUID)

**Attributes:**
- dataPointId: DataPointId
- metricId: MetricId
- value: Float
- timestamp: Timestamp

**Behaviors:**
- getValue(): Float
- getTimestamp(): Timestamp

**Business Rules:**
- One data point per day
- Used for trend analysis

---

## Value Objects

### EmailId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): Boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### EmailAddress

**Attributes:**
- value: String

**Behaviors:**
- equals(other): Boolean
- toString(): String
- isValid(): Boolean

**Invariants:**
- Must be valid email format
- Cannot be empty

---

### EmailContent

**Attributes:**
- body: String
- format: String (plain_text, html)

**Behaviors:**
- getBody(): String
- isPlainText(): Boolean
- isHTML(): Boolean

**Invariants:**
- Body must not be empty
- Format must be plain_text or html (MVP uses plain_text only)

---

### EmailStatus

**Attributes:**
- value: Enum (QUEUED, SENT, FAILED)

**Behaviors:**
- isQueued(): Boolean
- isSent(): Boolean
- isFailed(): Boolean
- canTransitionTo(newStatus): Boolean

**Invariants:**
- Valid transitions:
  - QUEUED → SENT
  - QUEUED → FAILED
  - FAILED → QUEUED (retry)

---

### ConversationSnapshot

**Attributes:**
- conversationId: ConversationId
- messages: List<Message>
- userInfo: UserInfo
- createdAt: Timestamp

**Behaviors:**
- formatForEmail(): String
- getMessageCount(): Integer

**Invariants:**
- Must include at least one message
- Messages ordered by timestamp

---

### EventId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): Boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### EventType

**Attributes:**
- value: Enum (QUERY_SUBMITTED, FEEDBACK_SUBMITTED, ESCALATION_TRIGGERED, USER_AUTHENTICATED, DOCUMENT_ACCESSED)

**Behaviors:**
- isQuerySubmitted(): Boolean
- isFeedbackSubmitted(): Boolean
- isEscalationTriggered(): Boolean
- toString(): String

**Invariants:**
- Must be one of the defined types

---

### EventMetadata

**Attributes:**
- data: Map<String, Any>

**Behaviors:**
- get(key): Any
- has(key): Boolean
- toJSON(): String
- fromJSON(json): EventMetadata

**Invariants:**
- Must be valid JSON
- Keys must be strings

---

### MetricType

**Attributes:**
- value: Enum (TOTAL_QUERIES, RESOLUTION_RATE, ESCALATION_COUNT, ACTIVE_USERS, TOP_QUERIES)

**Behaviors:**
- isTotalQueries(): Boolean
- isResolutionRate(): Boolean
- isEscalationCount(): Boolean
- isActiveUsers(): Boolean
- isTopQueries(): Boolean
- toString(): String

**Invariants:**
- Must be one of the defined types

---

### MetricValue

**Attributes:**
- value: Any (Integer, Float, List, Map)
- unit: String (count, percentage, list)

**Behaviors:**
- asInteger(): Integer
- asFloat(): Float
- asList(): List
- asMap(): Map
- toString(): String

**Invariants:**
- Value must match unit type

---

### TimePeriod

**Attributes:**
- startDate: Timestamp
- endDate: Timestamp
- days: Integer

**Behaviors:**
- getDays(): Integer
- includes(timestamp): Boolean
- isLast30Days(): Boolean

**Invariants:**
- End date must be after start date
- MVP uses fixed 30-day period

---

## Domain Events

### EscalationEmailSent

**Attributes:**
- emailId: EmailId
- conversationId: ConversationId
- userId: UserId
- sentAt: Timestamp

**Triggered When:** Escalation email successfully sent

**Consumers:** Internal (for tracking)

---

### EscalationEmailFailed

**Attributes:**
- emailId: EmailId
- conversationId: ConversationId
- failureReason: String
- retryCount: Integer
- failedAt: Timestamp

**Triggered When:** Email sending fails

**Consumers:** Internal (for retry logic and alerting)

---

### AnalyticsEventRecorded

**Attributes:**
- eventId: EventId
- eventType: EventType
- occurredAt: Timestamp

**Triggered When:** Analytics event is stored

**Consumers:** Internal (for metrics calculation)

---

### MetricCalculated

**Attributes:**
- metricId: MetricId
- metricType: MetricType
- value: MetricValue
- calculatedAt: Timestamp

**Triggered When:** Metric is calculated or updated

**Consumers:** Internal (for dashboard refresh)

---

## Repositories

### IEscalationEmailRepository

**Purpose:** Persist and retrieve EscalationEmail aggregates

**Methods:**
- save(email: EscalationEmail): void
- findById(emailId: EmailId): EscalationEmail
- findByConversationId(conversationId: ConversationId): EscalationEmail
- findByUserId(userId: UserId, limit: Integer): List<EscalationEmail>
- findQueued(): List<EscalationEmail>
- findFailed(): List<EscalationEmail>
- deleteOlderThan(days: Integer): Integer

**Implementation Notes:**
- Uses `communication_analytics.escalation_emails` table
- Implements retry queue for failed emails
- Retains emails for 90 days

---

### IAnalyticsEventRepository

**Purpose:** Persist and retrieve AnalyticsEvent aggregates

**Methods:**
- save(event: AnalyticsEvent): void
- findById(eventId: EventId): AnalyticsEvent
- findByType(eventType: EventType, startDate: Timestamp, endDate: Timestamp): List<AnalyticsEvent>
- findByUserId(userId: UserId, startDate: Timestamp, endDate: Timestamp): List<AnalyticsEvent>
- countByType(eventType: EventType, startDate: Timestamp, endDate: Timestamp): Integer
- deleteOlderThan(days: Integer): Integer

**Implementation Notes:**
- Uses `communication_analytics.analytics_events` table
- Implements time-series indexing for fast queries
- Retains events for 30 days

---

### IMetricRepository

**Purpose:** Persist and retrieve Metric aggregates

**Methods:**
- save(metric: Metric): void
- findById(metricId: MetricId): Metric
- findByType(metricType: MetricType): Metric
- findByTypeAndPeriod(metricType: MetricType, timePeriod: TimePeriod): Metric
- findAll(): List<Metric>

**Implementation Notes:**
- Uses `communication_analytics.metrics` and `communication_analytics.metric_data_points` tables
- Implements caching for dashboard queries
- Historical data points retained indefinitely

---

## Domain Services

### EmailCompositionService

**Purpose:** Compose escalation email content

**Methods:**
- composeEmail(conversationId: ConversationId, userId: UserId): EmailContent
- formatConversationHistory(messages: List<Message>): String
- formatUserInfo(user: User): String
- generateSubject(conversationId: ConversationId): String

**Business Rules:**
- Subject: "Support Escalation - [ConversationId]"
- Include full conversation history
- Include user name, email, role
- Include timestamp of escalation
- Plain text format for MVP
- Expected response time: 24-48 hours

**Rationale:** This is a domain service because it contains business logic for email composition.

---

### MetricsCalculationService

**Purpose:** Calculate analytics metrics from events

**Methods:**
- calculateTotalQueries(timePeriod: TimePeriod): Integer
- calculateResolutionRate(timePeriod: TimePeriod): Float
- calculateEscalationCount(timePeriod: TimePeriod): Integer
- calculateActiveUsers(timePeriod: TimePeriod): Integer
- calculateTopQueries(timePeriod: TimePeriod, limit: Integer): List<QueryCount>
- recalculateAllMetrics(): void

**Business Rules:**
- Total queries: Count of QUERY_SUBMITTED events
- Resolution rate: (Solved feedback / Total feedback) * 100
- Escalation count: Count of ESCALATION_TRIGGERED events
- Active users: Distinct users with QUERY_SUBMITTED events
- Top queries: Most frequent query texts (top 10)
- Metrics calculated daily at midnight

**Rationale:** This is a domain service because it contains complex calculation logic across multiple events.

---

### DashboardDataService

**Purpose:** Prepare data for analytics dashboard

**Methods:**
- getDashboardData(timePeriod: TimePeriod): DashboardData
- getMetricsByType(metricTypes: List<MetricType>): Map<MetricType, Metric>
- formatForDisplay(metrics: List<Metric>): DashboardData

**Business Rules:**
- Dashboard shows last 30 days (fixed for MVP)
- Includes: total queries, resolution rate, escalation count, active users, top 10 queries
- Data refreshed daily
- Only accessible to Administrators

**Rationale:** This is a domain service because it orchestrates dashboard data preparation.

---

## Application Services

### SendEscalationEmailApplicationService

**Purpose:** Orchestrate escalation email sending

**Responsibilities:**
1. Validate user authentication (call Access Control Context)
2. Retrieve conversation history (call Chat Interface Context)
3. Compose email (call EmailCompositionService)
4. Create EscalationEmail aggregate
5. Send email via email service provider (infrastructure)
6. Publish EscalationEmailSent event
7. Return confirmation

**Not a Domain Service because:** It orchestrates across contexts and handles infrastructure concerns.

---

### RecordAnalyticsEventApplicationService

**Purpose:** Record analytics events from other contexts

**Responsibilities:**
1. Validate event data
2. Create AnalyticsEvent aggregate
3. Save event
4. Publish AnalyticsEventRecorded event
5. Return confirmation

---

### GetDashboardDataApplicationService

**Purpose:** Retrieve dashboard data for administrators

**Responsibilities:**
1. Validate user is administrator (call Access Control Context)
2. Get dashboard data (call DashboardDataService)
3. Return formatted data

---

## Policies

### EmailRetryPolicy

**Rule:** Failed emails retried up to 3 times with exponential backoff

**Implementation:**
- Retry delays: 1 minute, 5 minutes, 15 minutes
- Maximum 3 attempts
- After 3 failures, manual intervention required

---

### EventRetentionPolicy

**Rule:** Analytics events retained for 30 days

**Implementation:**
- Scheduled job runs daily
- Deletes events older than 30 days
- Metrics calculated before deletion

---

### EmailRateLimitPolicy

**Rule:** Maximum 10 escalation emails per hour per user

**Implementation:**
- Tracked in EscalationEmailRepository
- Prevents spam and abuse
- Returns error if limit exceeded

---

### MetricRefreshPolicy

**Rule:** Metrics recalculated daily at midnight

**Implementation:**
- Scheduled job runs at 00:00 UTC
- Calls MetricsCalculationService.recalculateAllMetrics()
- Updates all metric types

---

## Business Rules Summary

### Escalation Email Rules
1. Maximum 3 retry attempts
2. Retry delay: exponential backoff
3. Must include conversation history
4. Must include user information
5. Rate limit: 10 emails per hour per user
6. Subject format: "Support Escalation - [ConversationId]"
7. Plain text format (MVP)
8. Retained for 90 days

### Analytics Event Rules
1. Events are immutable
2. Metadata stored as JSON
3. Events retained for 30 days
4. Events processed asynchronously
5. Event types: query_submitted, feedback_submitted, escalation_triggered, user_authenticated, document_accessed

### Metrics Rules
1. Metrics calculated daily at midnight
2. Time period: last 30 days (fixed for MVP)
3. Historical data points retained
4. Dashboard accessible to Administrators only
5. Metrics: total queries, resolution rate, escalation count, active users, top 10 queries

### Dashboard Rules
1. Shows last 30 days only (MVP)
2. Accessible to Administrators only
3. Data refreshed daily
4. No filtering or export (MVP)
5. Simple charts: bar, pie, numbers

---

## Aggregate Relationships

```
EscalationEmail (Aggregate Root)
├── emailId: EmailId (identity)
├── conversationId: ConversationId (reference to Chat Interface)
├── userId: UserId (reference to Access Control)
├── recipientEmail: EmailAddress (value object)
├── content: EmailContent (value object)
├── conversationSnapshot: ConversationSnapshot (value object)
├── screenshots: List<Screenshot> (value objects)
├── status: EmailStatus (value object)
└── Timestamps (sentAt, deliveryConfirmedAt)

AnalyticsEvent (Aggregate Root)
├── eventId: EventId (identity)
├── eventType: EventType (value object)
├── userId: UserId (reference to Access Control)
├── conversationId: ConversationId (optional reference)
├── metadata: EventMetadata (value object)
└── occurredAt: Timestamp

Metric (Aggregate Root)
├── metricId: MetricId (identity)
├── metricType: MetricType (value object)
├── value: MetricValue (value object)
├── timePeriod: TimePeriod (value object)
├── MetricDataPoints (entities, 1-to-many)
│   ├── MetricDataPoint 1
│   │   ├── dataPointId: DataPointId
│   │   ├── value: Float
│   │   └── timestamp: Timestamp
│   ├── MetricDataPoint 2
│   └── MetricDataPoint N
└── calculatedAt: Timestamp
```

---

## Consistency Boundaries

**Strong Consistency (within aggregate):**
- Email sending and status updates are atomic
- Event recording is immediate
- Metric calculations are consistent

**Eventual Consistency (across aggregates):**
- Metrics updated daily (not real-time)
- Email delivery confirmation may be delayed
- Dashboard data may be up to 24 hours old

---

## Integration Points

### Inbound (APIs this context provides)

**REST Endpoints:**
- POST /api/v1/communication/send-escalation-email - Send escalation email
- POST /api/v1/communication/analytics/record-event - Record analytics event
- GET /api/v1/communication/analytics/dashboard - Get dashboard data (admin only)

### Outbound (APIs this context consumes)

**Access Control Context:**
- POST /api/v1/auth/validate - Validate user token
- GET /api/v1/auth/users/{userId} - Get user profile

**Chat Interface Context:**
- GET /api/v1/chat/conversations/{id} - Get conversation history

**External Systems (via Infrastructure):**
- Email service provider (SendGrid, AWS SES, SMTP)

---

## Infrastructure Concerns

**Not part of domain model, but noted for completeness:**

- Email service integration (SendGrid, AWS SES, SMTP)
- Email template management
- Retry queue for failed emails
- Time-series database for events (optional)
- Dashboard visualization library
- Scheduled jobs for metrics calculation
- Event retention cleanup job

---

## Notes

- This context handles both communication and analytics for MVP simplicity
- Could be split into two contexts in post-MVP
- Email escalation is automated (no manual routing)
- Analytics are basic (advanced reporting deferred)
- Dashboard is read-only (no export functionality in MVP)
- Metrics calculated daily (not real-time)

