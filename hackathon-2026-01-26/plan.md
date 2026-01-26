# Plan: System Support Web Application - User Stories

## Overview
Creating user stories for a system support web application where users interact with AI to get help with system errors and task guidance, with links to SOPs/documents.

## Steps

### Phase 1: Requirements Clarification
- [x] **Step 1:** Clarify user roles and personas
  - [Question] Who are the primary users of this system? (e.g., end users, IT support staff, administrators, developers)
  - [Answer] all mentioned
  
  - [Question] Are there different user roles with different permissions or capabilities?
  - [Answer] yes and the response will need to base on user access restriction

- [x] **Step 2:** Clarify AI interaction scope
  - [Question] What types of systems/applications will this support (e.g., specific software, general IT systems, custom enterprise applications)?
  - [Answer] netsuite and all the system integrations with Transport Management System

  - [Question] Should the AI provide real-time troubleshooting or just link to existing documentation?
  - [Answer] just provide link to documentation
  
  - [Question] Can users provide screenshots, error codes, or log files to the AI?
  - [Answer] yes

- [x] **Step 3:** Clarify document/SOP management
  - [Question] Where are the SOPs/documents stored (e.g., internal knowledge base, external URLs, document management system)?
  - [Answer] SOP & PRD are stored in S3 & confluence and clickup. netsuite related general system non customised questions can be search from internet or access from Suiteanswer which need netsuite access. Some logic may not have documentation so will need to check from customised scripts/workflows in netsuite
  
  - [Question] Should the system support multiple document formats (PDF, web pages, videos)?
  - [Answer] usually web pages and some PDFs but some may need system access. 
  
  - [Question] Do documents need to be searchable or tagged for better AI matching?
  - [Answer] yes both searable and/or tagged 

- [x] **Step 4:** Clarify user workflow and features
  - [Question] Should users be able to save their conversation history or bookmark solutions?
  - [Answer] yes for both
  
  - [Question] Do you need user feedback mechanisms (e.g., "Was this helpful?" ratings)?
  - [Answer] yes
  
  - [Question] Should there be escalation to human support if AI cannot help?
  - [Answer] yes. human support will be via email 
  
  - [Question] Do you need analytics/reporting on common issues or user queries?
  - [Answer] yes

- [x] **Step 5:** Clarify confirmation workflow
  - [Question] What does "user confirms" mean in your workflow? (e.g., confirms the diagnosis is correct, confirms they want to see the document, confirms they tried the solution)
  - [Answer] confirm that the response answered their question and confirm they want to see the document links provided and confirm the proposed solution solve their problem. 

### Phase 2: User Story Development
- [x] **Step 6:** Create inception directory structure

- [x] **Step 7:** Write core user stories for AI interaction (query submission, AI response)

- [x] **Step 8:** Write user stories for error troubleshooting workflow

- [x] **Step 9:** Write user stories for task guidance workflow

- [x] **Step 10:** Write user stories for document/SOP access

- [x] **Step 11:** Write user stories for user confirmation and feedback

- [x] **Step 12:** Review and refine all user stories for completeness

### Phase 3: Review and Approval
- [x] **Step 13:** Present user stories for your review and approval

---

## Notes
- User stories will follow standard format: "As a [role], I want [feature] so that [benefit]"
- Each story will include acceptance criteria
- Stories will be prioritized (Must Have, Should Have, Could Have)
- Focus only on user stories, no technical design or architecture

---

**Status:** User stories completed and approved.
