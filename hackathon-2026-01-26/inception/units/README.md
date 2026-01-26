# System Support Web Application - Unit Documentation (MVP)

## Overview
This directory contains the unit grouping and integration contracts for the **MVP version** of the System Support Web Application, focusing on NetSuite and Transport Management System (TMS) integrations with AI-powered documentation link provision.

**MVP Scope:**
- Basic AI query submission and response
- Document link retrieval from S3 and Confluence only
- Simple authentication (username/password, 2 roles)
- Essential conversation management (last 30 days)
- Basic feedback mechanism (Yes/No, Solved/Not Solved)
- Automated email escalation
- Basic analytics dashboard

---

## Unit Structure

The MVP system is organized into **5 independent units** that can be built by a single development team:

### Unit 1: Chat Interface Service
**File:** `unit1_chat_interface_service.md`  
**User Stories:** 9 stories (US-001, US-002, US-003, US-011, US-013, US-015, US-017, US-018)

**Responsibilities:**
- Chat-style user interface
- Message submission and display
- Screenshot attachment handling
- Conversation history (last 30 days)
- User feedback collection (Yes/No, Solved/Not Solved)
- Email escalation trigger

**MVP Simplifications:**
- Single screenshot per query
- Basic list view for history
- No bookmarks
- No advanced search

---

### Unit 2: Access Control Service
**File:** `unit2_access_control_service.md`  
**User Stories:** 2 stories (US-020, US-021)

**Responsibilities:**
- Basic username/password authentication
- Session management
- Role-based access control (2 roles: End User, Administrator)
- Document access filtering
- Permission verification

**MVP Simplifications:**
- No SSO integration
- Two roles only
- Basic permission model
- No password reset

---

### Unit 3: Document Repository Service
**File:** `unit3_document_repository_service.md`  
**User Stories:** 7 stories (US-004, US-006, US-007, US-008, US-010, US-026, US-027)

**Responsibilities:**
- Document search from S3 and Confluence
- Document link generation
- Basic keyword search
- Permission-based access control
- Multi-format support (web pages, PDFs)

**MVP Simplifications:**
- S3 and Confluence only (no ClickUp)
- Basic keyword search (no tagging)
- Simple relevance ranking
- No advanced filtering

---

### Unit 4: AI Orchestration Service
**File:** `unit4_ai_orchestration_service.md`  
**User Stories:** 2 stories (US-028, US-030)

**Responsibilities:**
- AI query processing
- Documentation link generation
- Basic intent detection
- Context management (last 5 messages)
- Access restriction enforcement

**MVP Simplifications:**
- Basic query understanding
- Simple document matching
- Limited context window
- No advanced NLP

---

### Unit 5: Communication & Analytics Service
**File:** `unit5_communication_analytics_service.md`  
**User Stories:** 1 story (US-022)

**Responsibilities:**
- Automated email escalation
- Basic analytics dashboard (Admin only)
- Feedback data collection
- Usage metrics

**MVP Simplifications:**
- Single support email address
- Basic text email format
- Fixed 30-day analytics period
- Simple charts only
- No export functionality

---

## Integration Contract

**File:** `integration_contract.md`

The integration contract defines all API endpoints, request/response schemas, authentication patterns, and data models for communication between units.

### Key Integration Points:

1. **Unit 1 → Unit 4:** Query processing and response generation
2. **Unit 1 → Unit 2:** Authentication and session management
3. **Unit 1 → Unit 5:** Escalation triggers and feedback collection
4. **Unit 4 → Unit 2:** Access restriction filtering
5. **Unit 4 → Unit 3:** Document search and retrieval
6. **Unit 5 → Unit 1:** Analytics data collection
7. **All Units → Unit 2:** Permission verification

### Communication Patterns:
- **Synchronous:** REST APIs for request-response
- **Asynchronous:** Event-driven for analytics and email
- **Authentication:** JWT tokens
- **Data Format:** JSON
- **Access Control:** Centralized filtering via Unit 2

---

## Architecture Principles

### Loose Coupling
- Units communicate only through well-defined APIs
- No direct database access between units
- Each unit can be deployed independently
- Changes to one unit don't require changes to others

### High Cohesion
- Each unit has a single, well-defined responsibility
- Related functionality is grouped together
- User stories within each unit are highly related

### MVP Focus
- Simple, functional implementation
- Core features only
- Technical debt acceptable for faster delivery
- Focus on learning and validation

---

## Development Approach

### Recommended Build Order:
1. **Unit 2 (Access Control)** - Foundation for all other units (2-3 weeks)
2. **Unit 3 (Document Repository)** - Core knowledge source (3-4 weeks)
3. **Unit 4 (AI Orchestration)** - AI capabilities (3-4 weeks)
4. **Unit 5 (Communication & Analytics)** - Email and analytics (1-2 weeks)
5. **Unit 1 (Chat Interface)** - User-facing functionality (2-3 weeks)

**Total MVP Timeline: 10-13 weeks**

### Testing Strategy:
- Unit testing within each unit
- Integration testing using contract tests
- End-to-end testing through Unit 1 APIs
- Mock external dependencies (S3, Confluence, AI service)

---

## MVP Deferred Features

The following features are **NOT included in MVP** and will be built in post-MVP phases:

### Deferred to Phase 2:
- SSO authentication
- Additional roles (IT Support Staff, Developer)
- ClickUp integration
- SuiteAnswers integration
- Direct NetSuite system access
- Advanced tagging and search
- Bookmark functionality
- Advanced analytics and reporting
- Export functionality
- Password reset
- Cross-device sync
- Advanced NLP features

---

## Security Considerations

- All inter-unit communication requires authentication
- JWT tokens with 1-hour expiration
- Centralized access restriction filtering (Unit 2)
- Audit logging for sensitive operations
- HTTPS/TLS for all communications
- PII encryption at rest
- Document-level access control

---

## Next Steps

1. ✅ Review unit documentation and integration contracts
2. ⏳ Approve unit structure and API designs
3. ⏳ Begin technical system design for each unit
4. ⏳ Set up development environment and CI/CD pipelines
5. ⏳ Start implementation with Unit 2 (Access Control)

---

## Files in This Directory

- `unit1_chat_interface_service.md` - Unit 1 documentation with 9 user stories
- `unit2_access_control_service.md` - Unit 2 documentation with 2 user stories
- `unit3_document_repository_service.md` - Unit 3 documentation with 7 user stories
- `unit4_ai_orchestration_service.md` - Unit 4 documentation with 2 user stories
- `unit5_communication_analytics_service.md` - Unit 5 documentation with 1 user story
- `integration_contract.md` - Complete API specifications for all units
- `README.md` - This file

---

**Total User Stories in MVP:** 20  
**Total Units:** 5  
**Total API Endpoints:** 25+ endpoints across all units

**Version:** 1.0 MVP  
**Last Updated:** January 26, 2026
