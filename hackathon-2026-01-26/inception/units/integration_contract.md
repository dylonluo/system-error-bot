# Integration Contract - System Support Web Application (MVP)

## Document Information
**Project:** System Support Web Application - MVP  
**Version:** 1.0 MVP  
**Date:** January 26, 2026  
**Purpose:** Define API contracts between all units for integration

**MVP Scope:**
- Basic AI query submission and response
- Document link retrieval from S3 and Confluence only
- Simple authentication (username/password, 2 roles)
- Essential conversation management (last 30 days)
- Basic feedback mechanism
- Automated email escalation
- Basic analytics dashboard

---

## Architecture Overview

### Unit Structure
1. **Unit 1:** Chat Interface Service
2. **Unit 2:** Access Control Service
3. **Unit 3:** Document Repository Service
4. **Unit 4:** AI Orchestration Service
5. **Unit 5:** Communication & Analytics Service

### Communication Pattern
- **Synchronous:** REST APIs for request-response operations
- **Asynchronous:** Event-driven for analytics and email notifications
- **Authentication:** JWT tokens in Authorization header
- **Data Format:** JSON for all API requests and responses
- **Access Control:** All responses filtered by Access Control Service

---

## Unit 2: Access Control Service

### Base URL
`/api/v1/auth`

### Endpoints

#### POST /auth/login
**Description:** Authenticate user and generate access token

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "string (JWT)",
  "refreshToken": "string",
  "expiresIn": 3600,
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "end_user|administrator",
    "accessLevel": "basic|all"
  }
}
```

**Error Responses:**
- 401 Unauthorized: Invalid credentials
- 429 Too Many Requests: Rate limit exceeded

---

#### POST /auth/logout
**Description:** Invalidate user session and tokens

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

#### POST /auth/validate
**Description:** Validate access token and return user info

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "end_user|administrator",
    "accessLevel": "basic|all"
  }
}
```

**Error Responses:**
- 401 Unauthorized: Invalid or expired token

---

#### POST /auth/filter-documents
**Description:** Filter document list based on user access restrictions

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "documents": [
    {
      "id": "string",
      "title": "string",
      "url": "string",
      "accessLevel": "public|basic|advanced"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "filteredDocuments": [
    {
      "id": "string",
      "title": "string",
      "url": "string",
      "accessLevel": "string"
    }
  ],
  "removedCount": 2
}
```

---

#### GET /auth/users/{userId}
**Description:** Get user profile information

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "end_user|administrator",
  "accessLevel": "basic|all",
  "createdAt": "ISO 8601 timestamp",
  "lastLogin": "ISO 8601 timestamp"
}
```

---

## Unit 3: Document Repository Service

### Base URL
`/api/v1/documents`

### Endpoints

#### GET /documents/search
**Description:** Search documents across S3 and Confluence

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
- `query` (required): Search query string
- `platforms`: Comma-separated list (s3,confluence)
- `documentType`: sop|prd|guide
- `limit`: Number of results (default: 20, max: 50)

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "string",
      "title": "string",
      "snippet": "string",
      "url": "string",
      "platform": "s3|confluence",
      "documentType": "sop|prd|guide",
      "format": "webpage|pdf",
      "relevanceScore": 0.92,
      "accessLevel": "public|basic|advanced",
      "lastModified": "ISO 8601 timestamp"
    }
  ],
  "totalResults": 45,
  "query": "string"
}
```

**Error Responses:**
- 400 Bad Request: Missing or invalid query parameter
- 401 Unauthorized: Invalid token
- 500 Internal Server Error: Search service unavailable

---

#### GET /documents/{documentId}
**Description:** Get document details

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "title": "string",
  "url": "string",
  "platform": "s3|confluence",
  "format": "webpage|pdf",
  "accessLevel": "public|basic|advanced",
  "metadata": {
    "author": "string",
    "created": "ISO 8601 timestamp",
    "lastModified": "ISO 8601 timestamp"
  }
}
```

**Error Responses:**
- 404 Not Found: Document not found
- 403 Forbidden: User doesn't have access to document

---

## Unit 4: AI Orchestration Service

### Base URL
`/api/v1/ai`

### Endpoints

#### POST /ai/process-query
**Description:** Process user query and return documentation links

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "query": "string",
  "context": {
    "conversationId": "string",
    "previousMessages": [
      {
        "role": "user|assistant",
        "content": "string",
        "timestamp": "ISO 8601 timestamp"
      }
    ],
    "screenshot": {
      "filename": "string",
      "content": "string (base64)",
      "mimeType": "image/jpeg|image/png"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "response": "string",
  "documentationLinks": [
    {
      "id": "string",
      "title": "string",
      "url": "string",
      "source": "s3|confluence",
      "type": "sop|prd|guide",
      "relevance": 0.95,
      "description": "string",
      "format": "webpage|pdf"
    }
  ],
  "confidence": 0.85,
  "suggestEscalation": false,
  "processingTime": 2.3
}
```

**Error Responses:**
- 400 Bad Request: Invalid query or context
- 401 Unauthorized: Invalid token
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: AI service unavailable

**Notes:**
- Maximum 5 documentation links returned
- Links are pre-filtered based on user access level
- Context limited to last 5 messages

---

#### POST /ai/detect-intent
**Description:** Detect user query intent

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "query": "string"
}
```

**Response (200 OK):**
```json
{
  "intent": "error_troubleshooting|task_guidance|general_question",
  "entities": {
    "netsuiteModule": "string",
    "errorCode": "string",
    "taskType": "string"
  },
  "confidence": 0.92
}
```

---

## Unit 1: Chat Interface Service

### Base URL
`/api/v1/chat`

### Endpoints

#### POST /chat/conversations
**Description:** Create new conversation

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "title": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "conversationId": "string",
  "userId": "string",
  "title": "string",
  "createdAt": "ISO 8601 timestamp"
}
```

---

#### POST /chat/conversations/{conversationId}/messages
**Description:** Send message in conversation

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "message": "string",
  "screenshot": {
    "filename": "string",
    "content": "string (base64)",
    "mimeType": "image/jpeg|image/png",
    "size": 1234567
  }
}
```

**Response (200 OK):**
```json
{
  "messageId": "string",
  "userMessage": {
    "id": "string",
    "content": "string",
    "timestamp": "ISO 8601 timestamp",
    "screenshot": {
      "filename": "string",
      "url": "string"
    }
  },
  "aiResponse": {
    "id": "string",
    "content": "string",
    "documentationLinks": [
      {
        "title": "string",
        "url": "string",
        "description": "string",
        "format": "webpage|pdf"
      }
    ],
    "timestamp": "ISO 8601 timestamp"
  }
}
```

**Error Responses:**
- 400 Bad Request: Empty message or invalid screenshot
- 413 Payload Too Large: Screenshot exceeds 5MB
- 401 Unauthorized: Invalid token

---

#### GET /chat/conversations/{conversationId}
**Description:** Get conversation history

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "conversationId": "string",
  "title": "string",
  "messages": [
    {
      "id": "string",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO 8601 timestamp",
      "documentationLinks": [],
      "screenshot": {
        "filename": "string",
        "url": "string"
      }
    }
  ],
  "status": "active|resolved|escalated",
  "createdAt": "ISO 8601 timestamp"
}
```

**Error Responses:**
- 404 Not Found: Conversation not found
- 403 Forbidden: User doesn't own this conversation

---

#### GET /chat/conversations
**Description:** Get user's conversation list (last 30 days)

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "conversationId": "string",
      "title": "string",
      "lastMessage": "string",
      "status": "active|resolved|escalated",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp"
    }
  ],
  "total": 45
}
```

---

#### POST /chat/conversations/{conversationId}/feedback
**Description:** Submit feedback for a message

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "messageId": "string",
  "answeredQuestion": true,
  "problemSolved": true
}
```

**Response (200 OK):**
```json
{
  "feedbackId": "string",
  "recorded": true
}
```

---

#### POST /chat/conversations/{conversationId}/escalate
**Description:** Escalate conversation to human support

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "reason": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "escalationId": "string",
  "emailSent": true,
  "sentAt": "ISO 8601 timestamp",
  "estimatedResponseTime": "24-48 hours"
}
```

---

## Unit 5: Communication & Analytics Service

### Base URL
`/api/v1/communication`

### Endpoints

#### POST /communication/send-escalation-email
**Description:** Send escalation email to support team (called by Unit 1)

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "conversationId": "string",
  "userId": "string",
  "conversationHistory": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO 8601 timestamp"
    }
  ],
  "screenshots": [
    {
      "filename": "string",
      "url": "string"
    }
  ],
  "reason": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "emailId": "string",
  "status": "sent",
  "sentTo": "support@example.com",
  "sentAt": "ISO 8601 timestamp"
}
```

**Error Responses:**
- 500 Internal Server Error: Email service unavailable
- 429 Too Many Requests: Rate limit exceeded (max 10 emails/hour per user)

---

#### GET /communication/analytics/dashboard
**Description:** Get analytics dashboard data (Admin only)

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Response (200 OK):**
```json
{
  "period": {
    "start": "ISO 8601 timestamp",
    "end": "ISO 8601 timestamp",
    "days": 30
  },
  "metrics": {
    "totalQueries": 1523,
    "resolvedQueries": 1289,
    "escalatedQueries": 45,
    "activeUsers": 87,
    "resolutionRate": 0.846,
    "topQueries": [
      {
        "query": "string",
        "count": 123
      }
    ]
  }
}
```

**Error Responses:**
- 403 Forbidden: User is not an administrator

---

#### POST /communication/analytics/record-event
**Description:** Record analytics event (called by Unit 1)

**Headers:**
```
Authorization: Bearer {accessToken}
```

**Request:**
```json
{
  "eventType": "query_submitted|feedback_submitted|escalation_triggered",
  "conversationId": "string",
  "userId": "string",
  "metadata": {
    "answeredQuestion": true,
    "problemSolved": true,
    "query": "string"
  },
  "timestamp": "ISO 8601 timestamp"
}
```

**Response (200 OK):**
```json
{
  "eventId": "string",
  "recorded": true
}
```

---

## Common Data Models

### User Object
```json
{
  "id": "string (UUID)",
  "username": "string",
  "email": "string",
  "role": "end_user|administrator",
  "accessLevel": "basic|all"
}
```

### Documentation Link Object
```json
{
  "id": "string",
  "title": "string",
  "url": "string",
  "source": "s3|confluence",
  "type": "sop|prd|guide",
  "relevance": 0.95,
  "accessLevel": "public|basic|advanced",
  "description": "string",
  "format": "webpage|pdf"
}
```

### Message Object
```json
{
  "id": "string",
  "role": "user|assistant",
  "content": "string",
  "timestamp": "ISO 8601 timestamp",
  "documentationLinks": [],
  "screenshot": {
    "filename": "string",
    "url": "string"
  }
}
```

### Error Response Object
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "timestamp": "ISO 8601 timestamp",
    "requestId": "string (UUID)"
  }
}
```

---

## Integration Flow Examples

### Query Processing Flow
1. User submits query via **Unit 1** (Chat Interface)
2. **Unit 1** calls **Unit 2** (Access Control) to validate token
3. **Unit 1** calls **Unit 4** (AI Orchestration) to process query
4. **Unit 4** calls **Unit 2** to get user permissions
5. **Unit 4** calls **Unit 3** (Document Repository) for documents
6. **Unit 3** returns documents
7. **Unit 4** calls **Unit 2** to filter documents by access level
8. **Unit 4** generates response with up to 5 filtered links
9. **Unit 4** returns response to **Unit 1**
10. **Unit 1** displays response to user
11. **Unit 1** calls **Unit 5** to record analytics event

### Escalation Flow
1. User clicks escalate button in **Unit 1**
2. **Unit 1** retrieves conversation history
3. **Unit 1** calls **Unit 5** (Communication) to send email
4. **Unit 5** formats email with conversation context
5. **Unit 5** sends email via email service provider
6. **Unit 5** returns confirmation to **Unit 1**
7. **Unit 1** displays confirmation to user
8. **Unit 1** calls **Unit 5** to record escalation event

### Feedback Flow
1. User submits feedback in **Unit 1**
2. **Unit 1** stores feedback in database
3. **Unit 1** calls **Unit 5** to record analytics event
4. **Unit 5** updates metrics

---

## Security Standards

### Authentication
- JWT tokens with 1-hour expiration
- Refresh tokens with 7-day expiration
- All requests require valid authentication token

### Authorization
- Role-based access control (RBAC)
- Centralized access restriction filtering via Unit 2
- Permission checks on every request

### Data Protection
- HTTPS/TLS for all communications
- Passwords hashed with bcrypt
- PII encryption at rest
- Sensitive data redaction in logs

---

## Error Handling Standards

### HTTP Status Codes
- **200 OK:** Successful request
- **201 Created:** Resource created
- **400 Bad Request:** Invalid parameters
- **401 Unauthorized:** Missing/invalid authentication
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **413 Payload Too Large:** File size exceeds limit
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Server error

---

## Rate Limiting (MVP)

### Limits by Unit
- **Unit 1:** 60 requests/minute per user
- **Unit 2:** 100 requests/minute per user
- **Unit 3:** 30 requests/minute per user
- **Unit 4:** 20 requests/minute per user (AI processing)
- **Unit 5:** 10 emails/hour per user, unlimited analytics calls

---

## Performance Targets (MVP)

- **Query Response Time:** < 5 seconds for 90% of queries
- **API Response Time:** < 500ms for 95% of non-AI requests
- **Uptime:** 99% availability
- **Concurrent Users:** Support for 20 concurrent users

---

## Notes
- All timestamps use ISO 8601 format
- All IDs are UUIDs
- Pagination uses offset/limit pattern
- Screenshot uploads limited to 5MB
- Maximum 5 documentation links per response
- Conversation history limited to last 30 days
- Context window limited to last 5 messages
- **Access restriction filtering is mandatory for all document responses**
- **Email escalation is automated, not manual**
- **S3 and Confluence only (no ClickUp or SuiteAnswers in MVP)**
- **Two roles only: End User and Administrator**

