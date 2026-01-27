# Ubiquitous Language - System Support Web Application

## Document Information
**Purpose:** Define the common vocabulary used across all bounded contexts  
**Version:** 1.0  
**Date:** January 27, 2026

---

## Core Domain Terms

### Query & Conversation Domain

**Query**
- A user's question or problem description submitted to the AI assistant
- Can include text and optionally a screenshot attachment
- Represents a single request for help

**Conversation**
- A thread of messages between a user and the AI assistant
- Contains multiple queries and responses
- Has a lifecycle: active → resolved/escalated
- Persisted for 30 days

**Message**
- A single communication unit within a conversation
- Can be from user (query) or assistant (response)
- Immutable once created

**Response**
- The AI assistant's answer to a user's query
- Contains documentation links and explanatory text
- Includes confidence score

**Screenshot**
- An image attachment (JPG/PNG) provided with a query
- Limited to 5MB
- Helps AI understand visual context

**Feedback**
- User's evaluation of a response
- Two types: "Answered Question" (Yes/No) and "Problem Solved" (Solved/Not Solved)

**Escalation**
- Process of forwarding an unresolved conversation to human support
- Triggers automated email with conversation history
- Marks conversation as "escalated"

---

### Access Control Domain

**User**
- A person who uses the system
- Has credentials (username/password)
- Assigned a role and access level

**Role**
- Defines a user's function in the system
- MVP roles: End User, Administrator
- Determines available features and permissions

**Access Level**
- Defines what documentation a user can view
- Levels: basic, all
- End Users have "basic", Administrators have "all"

**Permission**
- A specific right to perform an action or view content
- Enforced at document and feature level

**Session**
- A user's authenticated period of system use
- Managed via JWT tokens
- Expires after 1 hour (access token) or 7 days (refresh token)

**Authentication**
- Process of verifying user identity
- MVP uses username/password

**Authorization**
- Process of determining what an authenticated user can access
- Based on role and access level

---

### Document Domain

**Document**
- A piece of documentation stored in external systems (S3, Confluence)
- Types: SOP (Standard Operating Procedure), PRD (Product Requirements Document), Guide
- Has access level: public, basic, advanced

**Documentation Link**
- A URL pointing to a document
- Includes metadata: title, description, relevance score, format
- Filtered based on user permissions

**Document Source**
- The platform where a document is stored
- MVP sources: S3, Confluence

**Document Format**
- The type of document content
- Formats: webpage, PDF

**Relevance Score**
- A numerical value (0.0-1.0) indicating how well a document matches a query
- Used for ranking search results

**Access Restriction**
- Rules determining which users can view which documents
- Based on document access level and user access level

---

### AI Orchestration Domain

**Intent**
- The detected purpose of a user's query
- Types: Error Troubleshooting, Task Guidance, General Question, Off-Topic
- Determined by AI analysis

**Context**
- Historical information used to understand a query
- Includes last 5 messages from conversation
- Helps AI provide relevant responses

**Confidence Score**
- A numerical value (0.0-1.0) indicating AI's certainty in its response
- Low confidence may trigger escalation suggestion

**Prompt**
- The formatted input sent to the AI service
- Includes query, context, and system instructions

**AI Response**
- Raw output from the AI service
- Contains generated text and metadata

**Token**
- Unit of text processed by AI (not authentication token)
- Used for cost tracking and limits

**Off-Topic Query**
- A user query not related to NetSuite or TMS
- Rejected with polite message
- No document search performed
- User can escalate if incorrectly classified

---

### Communication & Analytics Domain

**Escalation Email**
- Automated email sent to support team
- Contains conversation history, user info, and screenshots
- Triggered by user action

**Analytics Event**
- A recorded occurrence in the system
- Types: query_submitted, feedback_submitted, escalation_triggered
- Used for metrics calculation

**Metric**
- A calculated measurement of system usage
- Examples: total queries, resolution rate, active users

**Dashboard**
- Visual display of analytics metrics
- Available only to Administrators
- Shows data for last 30 days

**Resolution Rate**
- Percentage of queries marked as "Solved"
- Key performance indicator

---

## Bounded Contexts

### Chat Interface Context
**Focus:** User interaction and conversation management  
**Key Concepts:** Conversation, Message, Query, Response, Feedback, Screenshot

### Access Control Context
**Focus:** Authentication, authorization, and permission management  
**Key Concepts:** User, Role, Permission, Session, Access Level, Authentication, Authorization

### Document Repository Context
**Focus:** Document search and retrieval  
**Key Concepts:** Document, Documentation Link, Document Source, Relevance Score, Access Restriction

### AI Orchestration Context
**Focus:** AI query processing and response generation  
**Key Concepts:** Intent, Context, Confidence Score, Prompt, AI Response, Token

### Communication & Analytics Context
**Focus:** Email notifications and usage analytics  
**Key Concepts:** Escalation Email, Analytics Event, Metric, Dashboard, Resolution Rate

---

## Cross-Context Terms

**User ID**
- Unique identifier for a user
- Used across all contexts for correlation

**Conversation ID**
- Unique identifier for a conversation
- Used to link messages, feedback, and escalations

**Timestamp**
- ISO 8601 formatted date/time
- Used for ordering and filtering

**JWT Token**
- JSON Web Token for authentication
- Passed between units for authorization

---

## Business Rules & Invariants

### Conversation Rules
- A conversation must have at least one message
- A conversation belongs to exactly one user
- Messages in a conversation are ordered by timestamp
- Conversations are retained for 30 days only

### Access Control Rules
- Every user must have exactly one role
- End Users have "basic" access level
- Administrators have "all" access level
- A session must be valid to access any protected resource

### Document Rules
- A document link must point to an accessible resource
- Documents are filtered before being shown to users
- Maximum 5 documentation links per response
- Public documents are accessible to all users

### AI Processing Rules
- Context is limited to last 5 messages
- Confidence score below threshold suggests escalation
- Screenshot size must not exceed 5MB
- Query must not be empty

### Analytics Rules
- Events are recorded asynchronously
- Metrics are calculated for 30-day periods
- Dashboard is accessible only to Administrators

---

## State Transitions

### Conversation States
- **Active:** Conversation is ongoing
- **Resolved:** User marked problem as solved
- **Escalated:** Conversation forwarded to human support

### Session States
- **Valid:** Token is active and not expired
- **Expired:** Token has passed expiration time
- **Revoked:** User logged out, token invalidated

---

## Notes

- This language is used consistently across all domain models
- Terms are technology-agnostic where possible
- External system terms (S3, Confluence, Bedrock) are kept in infrastructure layer
- All team members should use these terms in discussions and documentation

