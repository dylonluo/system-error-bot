# Bounded Contexts - System Support Web Application

## Document Information
**Purpose:** Define the boundaries and relationships between domain contexts  
**Version:** 1.0  
**Date:** January 27, 2026

---

## Overview

The System Support Web Application is organized into **5 bounded contexts**, each corresponding to a unit. Each context has clear boundaries, its own domain model, and well-defined integration points.

---

## Context Map

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface Context                    │
│                         (Unit 1)                             │
│  - Manages conversations and user interactions               │
└───────┬─────────────────────────────────┬──────────────────┘
        │                                 │
        │ Authenticates                   │ Escalates
        │ Submits Queries                 │ Records Events
        ▼                                 ▼
┌──────────────────────┐         ┌──────────────────────┐
│  Access Control      │         │  Communication &     │
│     Context          │         │  Analytics Context   │
│     (Unit 2)         │         │     (Unit 5)         │
│                      │         │                      │
│ - Authentication     │         │ - Email escalation   │
│ - Authorization      │         │ - Analytics          │
│ - Permission checks  │         │ - Metrics            │
└──────┬───────────────┘         └──────────────────────┘
       │
       │ Validates Permissions
       │ Filters Documents
       │
       ▼
┌──────────────────────┐
│  AI Orchestration    │
│     Context          │
│     (Unit 4)         │
│                      │
│ - Query processing   │
│ - Intent detection   │
│ - Response generation│
└──────┬───────────────┘
       │
       │ Searches Documents
       │
       ▼
┌──────────────────────┐
│  Document Repository │
│     Context          │
│     (Unit 3)         │
│                      │
│ - Document search    │
│ - Link generation    │
└──────────────────────┘
```

---

## Bounded Context Definitions

### 1. Chat Interface Context (Unit 1)

**Responsibility:** Manage user conversations and message flow

**Core Concepts:**
- Conversation (Aggregate Root)
- Message (Entity)
- Query (Value Object)
- Response (Value Object)
- Feedback (Value Object)
- Screenshot (Value Object)

**Boundaries:**
- Owns conversation lifecycle
- Manages message history
- Collects user feedback
- Does NOT process AI queries (delegates to Unit 4)
- Does NOT authenticate users (delegates to Unit 2)
- Does NOT send emails (delegates to Unit 5)

**Integration Points:**
- **Upstream:** None (entry point for users)
- **Downstream:** 
  - Access Control Context (authentication, authorization)
  - AI Orchestration Context (query processing)
  - Communication & Analytics Context (escalation, events)

**Database Schema:** `chat_interface`

---

### 2. Access Control Context (Unit 2)

**Responsibility:** Manage authentication, authorization, and permissions

**Core Concepts:**
- User (Aggregate Root)
- Session (Entity)
- Role (Value Object)
- Permission (Value Object)
- AccessLevel (Value Object)

**Boundaries:**
- Owns user identity and credentials
- Manages sessions and tokens
- Enforces access restrictions
- Provides centralized permission checking
- Does NOT store conversations
- Does NOT process queries

**Integration Points:**
- **Upstream:** All other contexts (consumed by all)
- **Downstream:** None (foundational service)

**Database Schema:** `access_control`

**Special Role:** This is a **Shared Kernel** - all contexts depend on it for authentication and authorization.

---

### 3. Document Repository Context (Unit 3)

**Responsibility:** Search and retrieve documents from external sources

**Core Concepts:**
- Document (Aggregate Root)
- DocumentMetadata (Entity)
- DocumentLink (Value Object)
- SearchQuery (Value Object)
- RelevanceScore (Value Object)

**Boundaries:**
- Owns document search logic
- Manages document metadata
- Generates document links
- Does NOT enforce user permissions (delegates to Unit 2)
- Does NOT process AI queries (consumed by Unit 4)

**Integration Points:**
- **Upstream:** AI Orchestration Context
- **Downstream:** 
  - Access Control Context (permission verification)
  - External Systems (S3, Confluence) via infrastructure

**Database Schema:** `document_repository`

---

### 4. AI Orchestration Context (Unit 4)

**Responsibility:** Process queries using AI and orchestrate document retrieval

**Core Concepts:**
- AIQuery (Aggregate Root)
- Intent (Value Object)
- Context (Value Object)
- ConfidenceScore (Value Object)
- AIResponse (Value Object)

**Boundaries:**
- Owns AI query processing logic
- Manages conversation context
- Orchestrates document search
- Determines when to suggest escalation
- Does NOT store conversations (delegates to Unit 1)
- Does NOT authenticate users (delegates to Unit 2)

**Integration Points:**
- **Upstream:** Chat Interface Context
- **Downstream:** 
  - Access Control Context (permission verification)
  - Document Repository Context (document search)
  - External Systems (AWS Bedrock) via infrastructure

**Database Schema:** `ai_orchestration`

---

### 5. Communication & Analytics Context (Unit 5)

**Responsibility:** Handle email notifications and track system analytics

**Core Concepts:**
- EscalationEmail (Aggregate Root)
- AnalyticsEvent (Aggregate Root)
- Metric (Entity)
- Dashboard (Value Object)

**Boundaries:**
- Owns email escalation logic
- Manages analytics event collection
- Calculates metrics
- Generates dashboard data
- Does NOT own conversation data (reads from Unit 1)
- Does NOT authenticate users (delegates to Unit 2)

**Integration Points:**
- **Upstream:** Chat Interface Context
- **Downstream:** 
  - Access Control Context (admin verification)
  - External Systems (Email service) via infrastructure

**Database Schema:** `communication_analytics`

---

## Context Relationships

### Relationship Types

**Customer-Supplier**
- Chat Interface → AI Orchestration (Chat is customer, AI is supplier)
- AI Orchestration → Document Repository (AI is customer, Doc is supplier)
- Chat Interface → Communication & Analytics (Chat is customer, Comm is supplier)

**Shared Kernel**
- Access Control Context is shared by all contexts
- All contexts depend on User, Role, Permission concepts

**Conformist**
- All contexts conform to Access Control's authentication model
- All contexts use JWT tokens as defined by Access Control

---

## Integration Patterns

### Synchronous Communication (REST APIs)
- Chat Interface → AI Orchestration (query processing)
- AI Orchestration → Document Repository (document search)
- All contexts → Access Control (authentication, permission checks)

### Asynchronous Communication (Events)
- Chat Interface → Communication & Analytics (analytics events)
- Escalation triggers (email sending)

### Data Ownership
- Each context owns its own data
- No direct database access between contexts
- Data shared via APIs only

---

## Anti-Corruption Layers

**Not used in MVP** - External systems (S3, Confluence, AWS Bedrock) are handled as simple infrastructure adapters.

**Future consideration:** If external APIs become complex or unstable, introduce ACL.

---

## Context Boundaries - What Each Context Does NOT Do

### Chat Interface Context
- ❌ Does NOT process AI queries
- ❌ Does NOT authenticate users
- ❌ Does NOT send emails
- ❌ Does NOT search documents
- ✅ ONLY manages conversations and UI

### Access Control Context
- ❌ Does NOT store conversations
- ❌ Does NOT process queries
- ❌ Does NOT search documents
- ✅ ONLY manages authentication and authorization

### Document Repository Context
- ❌ Does NOT enforce user permissions (delegates to Unit 2)
- ❌ Does NOT process AI queries
- ❌ Does NOT store conversations
- ✅ ONLY searches and retrieves documents

### AI Orchestration Context
- ❌ Does NOT store conversations
- ❌ Does NOT authenticate users
- ❌ Does NOT send emails
- ✅ ONLY processes queries and orchestrates responses

### Communication & Analytics Context
- ❌ Does NOT own conversation data
- ❌ Does NOT authenticate users
- ❌ Does NOT process queries
- ✅ ONLY sends emails and tracks analytics

---

## Database Strategy

**Single Database with Separate Schemas**

```
Database: system_support_db
├── Schema: chat_interface
│   ├── conversations
│   ├── messages
│   └── feedback
├── Schema: access_control
│   ├── users
│   ├── sessions
│   └── roles
├── Schema: document_repository
│   ├── documents
│   └── document_metadata
├── Schema: ai_orchestration
│   ├── ai_queries
│   └── query_context
└── Schema: communication_analytics
    ├── escalation_emails
    ├── analytics_events
    └── metrics
```

**Benefits:**
- Easier to manage in MVP
- Simpler deployment
- Can still enforce boundaries via schema permissions
- Can migrate to separate databases later if needed

**Rules:**
- Each context only accesses its own schema
- Cross-context data access via APIs only
- No foreign keys across schemas

---

## Notes

- Each bounded context maps to one unit
- Contexts communicate via well-defined APIs (integration contract)
- Access Control is the foundational context (shared kernel)
- Clear boundaries prevent coupling and enable independent development
- MVP uses simple integration patterns (REST + events)

