# Logical Design - Unit 5: Communication & Analytics Service

## Document Information
**Bounded Context:** Communication & Analytics Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Architecture Style:** Simplified Layered Architecture  
**Technology Stack:** Python/FastAPI or Node.js/Express (framework-agnostic design)

---

## 1. Architecture Overview

### 1.1 Architectural Style
**Simplified Layered Architecture** with event-driven analytics:

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  (REST Controllers, Request/Response DTOs)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Application Service Layer                 │
│  (Email Sending, Event Recording, Metrics Calculation)   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Domain Layer                           │
│  (EscalationEmail, AnalyticsEvent, Metric Aggregates)    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                      │
│  (Repositories, Email Provider, Event Queue, Scheduler)  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles
- **Event-Driven:** Analytics collected via events
- **Asynchronous Processing:** Email and analytics processed asynchronously
- **Batch Aggregation:** Metrics calculated daily
- **Fail-Safe:** Email failures don't block user operations

---

## 2. Component Structure

### 2.1 API Layer Components

#### REST Controllers

**EscalationController**
- **Responsibility:** Handle escalation email requests
- **Endpoints:**
  - `POST /api/v1/communication/send-escalation-email` → sendEscalationEmail()

**AnalyticsController**
- **Responsibility:** Handle analytics operations
- **Endpoints:**
  - `POST /api/v1/communication/analytics/record-event` → recordEvent()
  - `GET /api/v1/communication/analytics/dashboard` → getDashboard() (admin only)

#### DTOs (Data Transfer Objects)

**Request DTOs:**
- SendEscalationEmailRequest (conversationId, userId, conversationHistory, screenshots, reason)
- RecordEventRequest (eventType, userId, conversationId, metadata)

**Response DTOs:**
- EscalationEmailResponse (emailId, status, sentTo, sentAt)
- EventRecordedResponse (eventId, recorded)
- DashboardDataResponse (period, metrics)

---

### 2.2 Application Service Layer Components

#### Application Services

**SendEscalationEmailApplicationService**
- **Responsibility:** Orchestrate escalation email sending
- **Key Operations:**
  - validateAuthentication() - Call Access Control Context
  - retrieveConversationHistory() - Call Chat Interface Context
  - composeEmail() - Call EmailCompositionService
  - createEscalationEmail() - Create aggregate
  - sendEmail() - Call email provider (async)
  - publishEvent() - Publish EscalationEmailSent event
  - recordAnalytics() - Record escalation event
  - returnConfirmation()

**RecordAnalyticsEventApplicationService**
- **Responsibility:** Record analytics events
- **Key Operations:**
  - validateEventData()
  - createAnalyticsEvent()
  - saveEvent()
  - publishEvent() - Publish AnalyticsEventRecorded event
  - returnConfirmation()

**GetDashboardDataApplicationService**
- **Responsibility:** Retrieve dashboard data for admins
- **Key Operations:**
  - validateAdminPermission() - Call Access Control Context
  - getDashboardData() - Call DashboardDataService
  - returnFormattedData()

**ProcessEmailQueueApplicationService**
- **Responsibility:** Process queued emails (background job)
- **Key Operations:**
  - retrieveQueuedEmails()
  - sendEmail() - For each queued email
  - markAsSent() or markAsFailed()
  - retryFailed() - Retry failed emails with backoff

**CalculateMetricsApplicationService**
- **Responsibility:** Calculate metrics (scheduled job)
- **Key Operations:**
  - retrieveEvents() - Get events from last 30 days
  - calculateMetrics() - Call MetricsCalculationService
  - saveMetrics()
  - publishMetricCalculated() events

#### External Service Clients

**AccessControlClient**
- **Responsibility:** Communicate with Access Control Context
- **Operations:**
  - validateToken(token) → User
  - getUserProfile(userId) → User

**ChatInterfaceClient**
- **Responsibility:** Communicate with Chat Interface Context
- **Operations:**
  - getConversationHistory(conversationId) → ConversationHistory

---

### 2.3 Domain Layer Components

#### Aggregates

**EscalationEmail (Aggregate Root)**
- **Identity:** EmailId
- **Value Objects:** EmailAddress, EmailContent, EmailStatus, ConversationSnapshot
- **Key Methods:**
  - send() → void
  - markAsSent() → void
  - markAsFailed(reason) → void
  - retry() → void
  - canRetry() → Boolean
  - getConversationHistory() → String

**AnalyticsEvent (Aggregate Root)**
- **Identity:** EventId
- **Value Objects:** EventType, EventMetadata
- **Key Methods:**
  - getMetadata(key) → String
  - hasMetadata(key) → Boolean
  - toJSON() → String

**Metric (Aggregate Root)**
- **Identity:** MetricId
- **Entities:** MetricDataPoint (collection)
- **Value Objects:** MetricType, MetricValue, TimePeriod
- **Key Methods:**
  - calculate() → void
  - addDataPoint(value, timestamp) → void
  - getValue() → MetricValue
  - getTrend() → String (increasing, decreasing, stable)

#### Entities

**MetricDataPoint**
- **Identity:** DataPointId
- **Attributes:** value, timestamp
- **Key Methods:**
  - getValue() → Float
  - getTimestamp() → Timestamp

#### Value Objects

**EmailId** - UUID wrapper
**EmailAddress** - String with email validation
**EmailContent** - body, format (plain_text, html)
**EmailStatus** - Enum (QUEUED, SENT, FAILED)
**ConversationSnapshot** - conversationId, messages, userInfo, createdAt
**EventId** - UUID wrapper
**EventType** - Enum (QUERY_SUBMITTED, FEEDBACK_SUBMITTED, ESCALATION_TRIGGERED, USER_AUTHENTICATED, DOCUMENT_ACCESSED)
**EventMetadata** - Map<String, Any> as JSON
**MetricId** - UUID wrapper
**MetricType** - Enum (TOTAL_QUERIES, RESOLUTION_RATE, ESCALATION_COUNT, ACTIVE_USERS, TOP_QUERIES)
**MetricValue** - Any (Integer, Float, List, Map) with unit
**TimePeriod** - startDate, endDate, days

#### Domain Services

**EmailCompositionService**
- **Responsibility:** Compose escalation email content
- **Operations:**
  - composeEmail(conversationId, userId) → EmailContent
  - formatConversationHistory(messages) → String
  - formatUserInfo(user) → String
  - generateSubject(conversationId) → String
- **Business Rules:**
  - Subject: "Support Escalation - [ConversationId]"
  - Include full conversation history
  - Include user name, email, role
  - Plain text format for MVP

**MetricsCalculationService**
- **Responsibility:** Calculate analytics metrics
- **Operations:**
  - calculateTotalQueries(timePeriod) → Integer
  - calculateResolutionRate(timePeriod) → Float
  - calculateEscalationCount(timePeriod) → Integer
  - calculateActiveUsers(timePeriod) → Integer
  - calculateTopQueries(timePeriod, limit) → List<QueryCount>
  - recalculateAllMetrics() → void
- **Business Rules:**
  - Total queries: Count of QUERY_SUBMITTED events
  - Resolution rate: (Solved feedback / Total feedback) * 100
  - Escalation count: Count of ESCALATION_TRIGGERED events
  - Active users: Distinct users with QUERY_SUBMITTED events
  - Top queries: Most frequent query texts (top 10)

**DashboardDataService**
- **Responsibility:** Prepare dashboard data
- **Operations:**
  - getDashboardData(timePeriod) → DashboardData
  - getMetricsByType(metricTypes) → Map<MetricType, Metric>
  - formatForDisplay(metrics) → DashboardData
- **Business Rules:**
  - Dashboard shows last 30 days (fixed for MVP)
  - Only accessible to Administrators

#### Domain Events

- EscalationEmailSent
- EscalationEmailFailed
- AnalyticsEventRecorded
- MetricCalculated

---

### 2.4 Infrastructure Layer Components

#### Repositories

**EscalationEmailRepository (implements IEscalationEmailRepository)**
- **Responsibility:** Persist escalation emails
- **Operations:**
  - save(email) → void
  - findById(emailId) → EscalationEmail
  - findByConversationId(conversationId) → EscalationEmail
  - findByUserId(userId, limit) → List<EscalationEmail>
  - findQueued() → List<EscalationEmail>
  - findFailed() → List<EscalationEmail>
  - deleteOlderThan(days) → Integer
- **Implementation:** PostgreSQL with `communication_analytics` schema

**AnalyticsEventRepository (implements IAnalyticsEventRepository)**
- **Responsibility:** Persist analytics events
- **Operations:**
  - save(event) → void
  - findById(eventId) → AnalyticsEvent
  - findByType(eventType, startDate, endDate) → List<AnalyticsEvent>
  - findByUserId(userId, startDate, endDate) → List<AnalyticsEvent>
  - countByType(eventType, startDate, endDate) → Integer
  - deleteOlderThan(days) → Integer
- **Implementation:** PostgreSQL with time-series indexing

**MetricRepository (implements IMetricRepository)**
- **Responsibility:** Persist metrics
- **Operations:**
  - save(metric) → void
  - findById(metricId) → Metric
  - findByType(metricType) → Metric
  - findByTypeAndPeriod(metricType, timePeriod) → Metric
  - findAll() → List<Metric>
- **Implementation:** PostgreSQL with caching

#### Email Provider

**EmailProvider (interface)**
- **Operations:**
  - send(to, subject, body) → EmailResult
  - isAvailable() → Boolean

**SMTPEmailProvider (implements EmailProvider)**
- **Responsibility:** Send emails via SMTP
- **Configuration:** SMTP host, port, username, password
- **Error Handling:** Retry on transient failures

**SendGridEmailProvider (implements EmailProvider)**
- **Responsibility:** Send emails via SendGrid
- **Configuration:** API key
- **Error Handling:** Retry on rate limits

**AWSEmailProvider (implements EmailProvider)**
- **Responsibility:** Send emails via AWS SES
- **Configuration:** AWS region, credentials
- **Error Handling:** Retry on throttling

#### Background Jobs

**EmailQueueProcessor**
- **Responsibility:** Process email queue
- **Schedule:** Every 1 minute
- **Operations:**
  - Retrieve queued emails
  - Send via EmailProvider
  - Update status

**MetricsCalculator**
- **Responsibility:** Calculate metrics
- **Schedule:** Daily at midnight (00:00 UTC)
- **Operations:**
  - Retrieve events from last 30 days
  - Calculate all metrics
  - Save to database

**EventCleanup**
- **Responsibility:** Delete old events
- **Schedule:** Daily at 01:00 UTC
- **Operations:**
  - Delete events older than 30 days

**EmailCleanup**
- **Responsibility:** Delete old emails
- **Schedule:** Daily at 02:00 UTC
- **Operations:**
  - Delete emails older than 90 days

#### Event Publisher

**EventPublisher**
- **Responsibility:** Publish domain events
- **Operations:**
  - publish(event) → void
- **Implementation:** Message queue or HTTP webhooks

---

## 3. Data Flow Diagrams

### 3.1 Send Escalation Email Flow

```
User Request (conversationId, userId, reason)
    ↓
EscalationController.sendEscalationEmail()
    ↓
SendEscalationEmailApplicationService.execute()
    ├─→ AccessControlClient.validateToken()
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return User
    ├─→ ChatInterfaceClient.getConversationHistory(conversationId)
    │       ↓
    │   [Chat Interface Context]
    │       ↓
    │   Return ConversationHistory (messages, screenshots)
    ├─→ EmailCompositionService.composeEmail()
    │   ├─→ generateSubject() → "Support Escalation - [ConversationId]"
    │   ├─→ formatConversationHistory(messages)
    │   ├─→ formatUserInfo(user)
    │   └─→ Return EmailContent
    ├─→ Create EscalationEmail aggregate
    │   ├─→ Set status = QUEUED
    │   ├─→ Set recipientEmail = "support@example.com"
    │   └─→ Set retryCount = 0
    ├─→ EscalationEmailRepository.save(email)
    ├─→ EmailProvider.send(email) [Asynchronous]
    │   ├─→ If success:
    │   │   ├─→ EscalationEmail.markAsSent()
    │   │   ├─→ EscalationEmailRepository.save(email)
    │   │   └─→ EventPublisher.publish(EscalationEmailSent)
    │   └─→ If failure:
    │       ├─→ EscalationEmail.markAsFailed(reason)
    │       ├─→ EscalationEmailRepository.save(email)
    │       ├─→ EventPublisher.publish(EscalationEmailFailed)
    │       └─→ Queue for retry (if retryCount < 3)
    ├─→ RecordAnalyticsEventApplicationService.execute()
    │   └─→ Record ESCALATION_TRIGGERED event
    ↓
Return EscalationEmailResponse (emailId, status, sentTo)
```

### 3.2 Record Analytics Event Flow

```
External Service Request (eventType, userId, metadata)
    ↓
AnalyticsController.recordEvent()
    ↓
RecordAnalyticsEventApplicationService.execute()
    ├─→ Validate event data
    ├─→ Create AnalyticsEvent aggregate
    │   ├─→ Set eventType
    │   ├─→ Set userId
    │   ├─→ Set metadata (as JSON)
    │   └─→ Set occurredAt = now()
    ├─→ AnalyticsEventRepository.save(event)
    ├─→ EventPublisher.publish(AnalyticsEventRecorded)
    ↓
Return EventRecordedResponse (eventId, recorded=true)
```

### 3.3 Calculate Metrics Flow (Scheduled Job)

```
Scheduled Job (Daily at 00:00 UTC)
    ↓
MetricsCalculator.run()
    ↓
CalculateMetricsApplicationService.execute()
    ├─→ Define timePeriod = last 30 days
    ├─→ MetricsCalculationService.calculateTotalQueries(timePeriod)
    │   ├─→ AnalyticsEventRepository.countByType(QUERY_SUBMITTED, timePeriod)
    │   └─→ Return count
    ├─→ MetricsCalculationService.calculateResolutionRate(timePeriod)
    │   ├─→ AnalyticsEventRepository.findByType(FEEDBACK_SUBMITTED, timePeriod)
    │   ├─→ Count events where metadata.problemSolved = true
    │   ├─→ Calculate: (solved / total) * 100
    │   └─→ Return percentage
    ├─→ MetricsCalculationService.calculateEscalationCount(timePeriod)
    │   ├─→ AnalyticsEventRepository.countByType(ESCALATION_TRIGGERED, timePeriod)
    │   └─→ Return count
    ├─→ MetricsCalculationService.calculateActiveUsers(timePeriod)
    │   ├─→ AnalyticsEventRepository.findByType(QUERY_SUBMITTED, timePeriod)
    │   ├─→ Extract distinct userIds
    │   └─→ Return count
    ├─→ MetricsCalculationService.calculateTopQueries(timePeriod, 10)
    │   ├─→ AnalyticsEventRepository.findByType(QUERY_SUBMITTED, timePeriod)
    │   ├─→ Group by metadata.query
    │   ├─→ Count occurrences
    │   ├─→ Sort by count descending
    │   └─→ Return top 10
    ├─→ For each metric:
    │   ├─→ Create or update Metric aggregate
    │   ├─→ Metric.addDataPoint(value, timestamp)
    │   ├─→ MetricRepository.save(metric)
    │   └─→ EventPublisher.publish(MetricCalculated)
    ↓
Log completion
```

### 3.4 Get Dashboard Data Flow

```
Admin Request
    ↓
AnalyticsController.getDashboard()
    ↓
GetDashboardDataApplicationService.execute()
    ├─→ AccessControlClient.validateToken()
    │       ↓
    │   Return User
    ├─→ Verify user.role = ADMINISTRATOR
    │       ↓
    │   If not admin → Return 403 Forbidden
    ├─→ DashboardDataService.getDashboardData(last 30 days)
    │   ├─→ MetricRepository.findByType(TOTAL_QUERIES)
    │   ├─→ MetricRepository.findByType(RESOLUTION_RATE)
    │   ├─→ MetricRepository.findByType(ESCALATION_COUNT)
    │   ├─→ MetricRepository.findByType(ACTIVE_USERS)
    │   ├─→ MetricRepository.findByType(TOP_QUERIES)
    │   └─→ Format as DashboardData
    ↓
Return DashboardDataResponse
```

---

## 4. Database Schema Design

### 4.1 Schema: `communication_analytics`

#### Table: `escalation_emails`
```
escalation_emails
├── email_id (UUID, PK)
├── conversation_id (UUID, NOT NULL)
├── user_id (UUID, NOT NULL)
├── recipient_email (VARCHAR(255), NOT NULL)
├── subject (VARCHAR(500), NOT NULL)
├── body (TEXT, NOT NULL)
├── status (ENUM: queued, sent, failed, NOT NULL)
├── sent_at (TIMESTAMP, nullable)
├── delivery_confirmed_at (TIMESTAMP, nullable)
├── failure_reason (TEXT, nullable)
├── retry_count (INTEGER, DEFAULT 0)
├── created_at (TIMESTAMP, NOT NULL)
└── INDEX on conversation_id, INDEX on user_id, INDEX on status
```

#### Table: `email_attachments`
```
email_attachments
├── attachment_id (UUID, PK)
├── email_id (UUID, FK to escalation_emails)
├── filename (VARCHAR(255), NOT NULL)
├── url (VARCHAR(1000), NOT NULL)
├── mime_type (VARCHAR(100))
└── INDEX on email_id
```

#### Table: `analytics_events`
```
analytics_events
├── event_id (UUID, PK)
├── event_type (ENUM: query_submitted, feedback_submitted, escalation_triggered, user_authenticated, document_accessed, NOT NULL)
├── user_id (UUID, NOT NULL)
├── conversation_id (UUID, nullable)
├── metadata (JSONB, NOT NULL) - event-specific data
├── occurred_at (TIMESTAMP, NOT NULL)
└── INDEX on event_type, occurred_at
└── INDEX on user_id, occurred_at
└── INDEX on conversation_id (if not null)
```

#### Table: `metrics`
```
metrics
├── metric_id (UUID, PK)
├── metric_type (ENUM: total_queries, resolution_rate, escalation_count, active_users, top_queries, NOT NULL)
├── value (JSONB, NOT NULL) - flexible value storage
├── unit (VARCHAR(50)) - count, percentage, list
├── time_period_start (TIMESTAMP, NOT NULL)
├── time_period_end (TIMESTAMP, NOT NULL)
├── time_period_days (INTEGER, NOT NULL)
├── calculated_at (TIMESTAMP, NOT NULL)
└── UNIQUE INDEX on metric_type, time_period_start, time_period_end
```

#### Table: `metric_data_points`
```
metric_data_points
├── data_point_id (UUID, PK)
├── metric_id (UUID, FK to metrics)
├── value (DECIMAL(10,2), NOT NULL)
├── timestamp (TIMESTAMP, NOT NULL)
└── INDEX on metric_id, timestamp
```

---

## 5. API-to-Component Mapping

### 5.1 Endpoint Mappings

| HTTP Method | Endpoint | Controller | Application Service | Domain Service |
|-------------|----------|------------|---------------------|----------------|
| POST | /api/v1/communication/send-escalation-email | EscalationController | SendEscalationEmailApplicationService | EmailCompositionService |
| POST | /api/v1/communication/analytics/record-event | AnalyticsController | RecordAnalyticsEventApplicationService | - |
| GET | /api/v1/communication/analytics/dashboard | AnalyticsController | GetDashboardDataApplicationService | DashboardDataService, MetricsCalculationService |

---

## 6. Integration Points

### 6.1 Outbound Integrations

**Access Control Context (Synchronous REST)**
- Endpoint: `POST /api/v1/auth/validate`
- Purpose: Validate user token
- Trigger: Every authenticated request

**Chat Interface Context (Synchronous REST)**
- Endpoint: `GET /api/v1/chat/conversations/{id}`
- Purpose: Retrieve conversation history for escalation email
- Trigger: When escalation email is sent

**Email Service Provider (External System)**
- SMTP, SendGrid, or AWS SES
- Purpose: Send escalation emails
- Trigger: When email is queued

### 6.2 Inbound Integrations

**All Other Contexts (Asynchronous Events)**
- Chat Interface Context: Publishes conversation events
- AI Orchestration Context: Publishes query events
- Access Control Context: Publishes authentication events
- Document Repository Context: Publishes document access events

---

## 7. Error Handling Strategy

### 7.1 Error Categories

**Validation Errors (400 Bad Request)**
- Invalid event type
- Missing required fields
- Invalid conversation ID

**Authentication Errors (401 Unauthorized)**
- Invalid token
- Expired token

**Authorization Errors (403 Forbidden)**
- Non-admin trying to access dashboard

**Rate Limit Errors (429 Too Many Requests)**
- More than 10 escalation emails per hour per user

**External Service Errors (500/503)**
- Email service unavailable
- Access Control service unavailable
- Chat Interface service unavailable

### 7.2 Email Sending Error Handling

**Retry Strategy:**
- Retry 3 times with exponential backoff (1min, 5min, 15min)
- After 3 failures, mark as permanently failed
- Manual intervention required for permanently failed emails

**Failure Notifications:**
- Log all email failures
- Alert on high failure rate (> 10% in 1 hour)

---

## 8. Security Considerations

### 8.1 Authentication
- All endpoints require valid JWT token
- Token validated via Access Control Context

### 8.2 Authorization
- Dashboard endpoint: Admin only
- Record event endpoint: All authenticated users
- Escalation email endpoint: All authenticated users

### 8.3 Rate Limiting
- Escalation emails: Max 10 per hour per user
- Prevents spam and abuse

### 8.4 Data Privacy
- PII redacted in analytics events
- Email content encrypted at rest
- Conversation history sanitized before emailing

---

## 9. Performance Considerations

### 9.1 Asynchronous Processing
- Email sending: Asynchronous (non-blocking)
- Analytics event recording: Fire-and-forget
- Metrics calculation: Scheduled batch job

### 9.2 Database Optimization
- Indexes on event_type, occurred_at for fast queries
- Time-series partitioning for analytics_events table
- Connection pooling

### 9.3 Caching Strategy
- Dashboard data: 1-hour TTL (Redis)
- Metrics: Cached after calculation

### 9.4 Response Time Targets
- Send escalation email: < 1 second (queuing only)
- Record event: < 100ms
- Get dashboard: < 500ms (with caching)

---

## 10. Deployment Considerations

### 10.1 Service Deployment
- Containerized application (Docker)
- Stateless service (horizontal scaling)
- Background jobs: Separate containers or same container with scheduler

### 10.2 Email Provider Configuration
- SMTP: Host, port, username, password
- SendGrid: API key
- AWS SES: Region, credentials

### 10.3 Scheduled Jobs
- Email queue processor: Every 1 minute
- Metrics calculator: Daily at 00:00 UTC
- Event cleanup: Daily at 01:00 UTC
- Email cleanup: Daily at 02:00 UTC

### 10.4 Monitoring
- Health check endpoint: `GET /health`
- Metrics: Email send rate, email failure rate, event recording rate
- Alerts: High email failure rate, metrics calculation failures

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Domain layer: Test aggregates, entities, value objects, domain services
- Email composition logic
- Metrics calculation logic
- Coverage target: 80%+

### 11.2 Integration Tests
- Test with mock email provider
- Test with test database
- Test scheduled jobs

### 11.3 Email Provider Tests
- Test with real SMTP server (integration tests)
- Test retry logic
- Test failure handling

### 11.4 Contract Tests
- Verify API contracts with Chat Interface Context
- Verify API contracts with Access Control Context

---

## 12. Future Enhancements (Post-MVP)

- Real-time analytics dashboard (WebSocket)
- Advanced metrics (average resolution time, user satisfaction)
- Email templates with HTML formatting
- Email delivery tracking (open rate, click rate)
- Custom dashboard filters (date range, user segments)
- Export dashboard data (CSV, PDF)
- Alerting system (email, Slack, PagerDuty)
- A/B testing for email content

---

## Notes

- This service handles both communication and analytics for MVP simplicity
- Could be split into two services in post-MVP
- Email sending is asynchronous to avoid blocking user operations
- Analytics are batch-processed for efficiency
- Dashboard is read-only with daily refresh
- Metrics calculated daily (not real-time)
