# Plan: System Support Web Application - Unit Grouping & Integration Contracts (V2)

## Overview
Grouping user stories from /inception/user_stories.md into independent, loosely coupled units with high cohesion. Each unit can be built by a single team and will have clear integration contracts.

**Updated Scope:** 
- NetSuite and Transport Management System (TMS) integrations only
- AI provides documentation links only (no real-time troubleshooting)
- Document storage: S3, Confluence, ClickUp
- All responses filtered by user access restrictions
- Escalation via automated email

---

## Steps

### Phase 1: Analysis and Unit Definition

- [x] **Step 1:** Analyze all 33 user stories from updated user_stories.md and identify natural groupings
  - Review user stories for functional cohesion
  - Identify dependencies between stories
  - Consider team boundaries and independent deployment
  - Account for access restriction requirements
  - Consider standalone web application architecture

- [x] **Step 2:** Define unit boundaries and responsibilities
  - [Question] Should we keep the same 5-unit structure from previous version, or would you like to reconsider based on the updated requirements (TMS only, documentation links only, S3 instead of SharePoint)?
  - [Answer] pls create new version base on updated requirements. 
  
  - [Question] Should the email escalation service be part of Unit 1 (Orchestration) or a separate unit?
  - [Answer] pls keep email escalation as separate unit
  
  - [Question] Should access restriction filtering be centralized in one unit or distributed across units?
  - [Answer] centralized in one unit
  
  - [Question] Do you want to maintain the same unit names or rename them to better reflect the updated scope?
  - [Answer] rename pls

- [x] **Step 3:** Validate unit independence and coupling
  - Ensure units can be built independently
  - Identify and minimize inter-unit dependencies
  - Verify each unit has clear boundaries
  - Validate access restriction enforcement points

### Phase 2: Unit Documentation

- [x] **Step 4:** Delete existing unit files and create fresh /inception/units/ directory structure

- [ ] **Step 5:** Write Unit 1 documentation with user stories and acceptance criteria

- [ ] **Step 6:** Write Unit 2 documentation with user stories and acceptance criteria

- [ ] **Step 7:** Write Unit 3 documentation with user stories and acceptance criteria

- [ ] **Step 8:** Write Unit 4 documentation with user stories and acceptance criteria

- [ ] **Step 9:** Write Unit 5 documentation with user stories and acceptance criteria (if applicable)

- [ ] **Step 10:** Write Unit 6 documentation with user stories and acceptance criteria (if applicable)

### Phase 3: Integration Contract Definition

- [ ] **Step 11:** Identify all integration points between units
  - Map data flows between units
  - Identify synchronous vs asynchronous communication needs
  - Define shared data models
  - Specify access restriction enforcement patterns
  - Define email service integration requirements

- [ ] **Step 12:** Define API endpoints for each unit
  - Specify HTTP methods (GET, POST, PUT, DELETE)
  - Define request/response schemas
  - Specify authentication requirements
  - Define error responses
  - Document access restriction filtering
  - Document email escalation endpoints

- [ ] **Step 13:** Create integration_contract.md with all API specifications
  - Document all endpoints by unit
  - Include request/response examples
  - Specify data formats and protocols
  - Define versioning strategy
  - Document external system integration patterns
  - Include email service specifications

### Phase 4: Review and Validation

- [ ] **Step 14:** Review unit groupings for cohesion and coupling

- [ ] **Step 15:** Validate integration contracts are complete and clear

- [ ] **Step 16:** Present units and integration contracts for your review and approval

---

## Key Changes from Previous Version

### Requirements Changes:
1. **System Scope:** NetSuite + TMS only (removed eCommerce, POS, Warehouse Management)
2. **AI Behavior:** Documentation links only (no real-time troubleshooting)
3. **Document Storage:** S3 instead of SharePoint
4. **Access Control:** Responses filtered by user access restrictions (emphasized throughout)
5. **Document Tagging:** Both searchable and tagged
6. **Escalation:** Automated email (not manual)

### Architectural Considerations:
- Standalone web application with chat-style interface
- Access restriction filtering at multiple layers
- Email service integration for escalation
- S3 integration instead of SharePoint
- TMS-specific integration patterns

---

## Proposed Unit Structure (Preliminary)

Based on updated requirements, here are potential unit structures:

### Option A: Keep 5-Unit Structure (Adapted)
1. **AI Orchestration & User Experience Unit** - Chat interface, conversation management, feedback, analytics
2. **Authentication & Authorization Unit** - Auth, roles, access restriction enforcement
3. **NetSuite & TMS Access Unit** - NetSuite system access, TMS integration, SuiteAnswers
4. **Document Integration Unit** - S3, Confluence, ClickUp document search and retrieval
5. **External AI Service Unit** - AI model integration, prompt engineering

### Option B: 6-Unit Structure (Separate Email)
1. **AI Orchestration & User Experience Unit** - Chat interface, conversation management, feedback
2. **Authentication & Authorization Unit** - Auth, roles, access restriction enforcement
3. **NetSuite & TMS Access Unit** - NetSuite system access, TMS integration
4. **Document Integration Unit** - S3, Confluence, ClickUp
5. **External AI Service Unit** - AI model integration
6. **Communication Services Unit** - Email escalation, notifications, analytics

### Option C: 4-Unit Structure (Consolidated)
1. **Frontend & Orchestration Unit** - Chat UI, conversation management, feedback, escalation
2. **Authentication & Access Control Unit** - Auth, roles, access restrictions
3. **Knowledge Access Unit** - NetSuite, TMS, S3, Confluence, ClickUp, SuiteAnswers
4. **AI & Communication Services Unit** - AI integration, email service, analytics

---

## User Story Distribution Analysis

### By Functional Area (Updated):
- **AI Interaction:** US-001, US-002, US-003 (3 stories)
- **NetSuite & TMS Access:** US-005, US-007, US-007A, US-027A, US-028, US-029, US-030, US-031 (8 stories)
- **Error Troubleshooting:** US-004 (1 story)
- **Document Management:** US-006, US-010, US-026, US-027 (4 stories)
- **Task Guidance:** US-008, US-009 (2 stories)
- **User Feedback:** US-011, US-012, US-013, US-014 (4 stories)
- **Conversation Management:** US-015, US-016, US-017 (3 stories)
- **Escalation:** US-018, US-019 (2 stories) - **Now with automated email**
- **Access Control:** US-020, US-021 (2 stories) - **Critical for filtering**
- **Analytics:** US-022, US-023, US-024, US-025 (4 stories)

### Key Integration Points:
- **Access Restriction Filtering** - Must be enforced at multiple layers
- **Email Service** - Required for automated escalation
- **S3 Integration** - Replaces SharePoint
- **TMS Integration** - Specific to Transport Management System
- **Document Tagging** - Required for better search

---

## Notes
- Each unit will be documented in a separate .md file
- Units will be designed for independent development and deployment
- Integration contracts will specify all inter-unit communication
- No technical system design will be included (as per requirements)
- Access restriction filtering is critical and must be clearly defined
- Email service integration required for escalation
- S3 integration patterns need to be specified

---

**Status:** Awaiting answers to clarification questions before proceeding with unit grouping.
