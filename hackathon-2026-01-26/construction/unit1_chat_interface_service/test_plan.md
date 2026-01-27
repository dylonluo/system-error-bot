# Test Plan - Unit 1: Chat Interface Service

## Document Information
**Version:** 1.0  
**Date:** January 27, 2026  
**Status:** Draft - Pending Review

---

## 1. Test Plan Overview

### 1.1 Scope
This test plan covers backend testing for the Chat Interface Service, including:
- Domain layer (aggregates, entities, value objects, domain services)
- Application layer (application services with mocked dependencies)
- API layer (REST endpoints with test database/mocks)
- Integration with external service clients (mocked)

### 1.2 Out of Scope
- Frontend/UI testing
- End-to-end testing with real external services
- Performance/load testing
- Security penetration testing

### 1.3 Test Framework
- **Framework:** pytest
- **Async Support:** pytest-asyncio
- **Coverage:** pytest-cov (target: 80%+)
- **Mocking:** unittest.mock / pytest-mock

---

## 2. Execution Plan

### Phase 1: Domain Layer Unit Tests
- [ ] 2.1 Value Objects Tests
  - [ ] 2.1.1 ConversationId tests
  - [ ] 2.1.2 MessageId tests
  - [ ] 2.1.3 ConversationStatus tests
  - [ ] 2.1.4 MessageRole tests
  - [ ] 2.1.5 Screenshot tests
  - [ ] 2.1.6 Feedback tests
  - [ ] 2.1.7 DocumentationLink tests

- [ ] 2.2 Entity Tests
  - [ ] 2.2.1 Message entity tests

- [ ] 2.3 Aggregate Tests
  - [ ] 2.3.1 Conversation aggregate tests

- [ ] 2.4 Domain Service Tests
  - [ ] 2.4.1 ScreenshotValidationService tests
  - [ ] 2.4.2 ConversationHistoryService tests

### Phase 2: Application Layer Unit Tests
- [ ] 2.5 Application Service Tests
  - [ ] 2.5.1 SubmitQueryApplicationService tests
  - [ ] 2.5.2 SubmitFeedbackApplicationService tests
  - [ ] 2.5.3 EscalateConversationApplicationService tests
  - [ ] 2.5.4 GetConversationApplicationService tests
  - [ ] 2.5.5 ListConversationsApplicationService tests

### Phase 3: API Layer Integration Tests
- [ ] 2.6 Controller Tests
  - [ ] 2.6.1 ConversationController tests
  - [ ] 2.6.2 MessageController tests

### Phase 4: Infrastructure Tests
- [ ] 2.7 Repository Tests
  - [ ] 2.7.1 InMemoryConversationRepository tests

- [ ] 2.8 Storage Tests
  - [ ] 2.8.1 InMemoryScreenshotStorage tests

- [ ] 2.9 Event Publisher Tests
  - [ ] 2.9.1 InMemoryEventPublisher tests

---

## 3. Detailed Test Cases

### 3.1 Value Objects Tests

#### 3.1.1 ConversationId Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-CID-001 | Generate new ConversationId | Valid UUID generated |
| VO-CID-002 | Create from valid UUID string | ConversationId created successfully |
| VO-CID-003 | Create from invalid string | ValueError raised |
| VO-CID-004 | Equality comparison (same UUID) | Returns True |
| VO-CID-005 | Equality comparison (different UUID) | Returns False |
| VO-CID-006 | String representation | Returns UUID string |

#### 3.1.2 MessageId Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-MID-001 | Generate new MessageId | Valid UUID generated |
| VO-MID-002 | Create from valid UUID string | MessageId created successfully |
| VO-MID-003 | Create from invalid string | ValueError raised |
| VO-MID-004 | Equality comparison | Correct boolean result |

#### 3.1.3 ConversationStatus Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-CS-001 | ACTIVE status is_active() | Returns True |
| VO-CS-002 | RESOLVED status is_active() | Returns False |
| VO-CS-003 | ESCALATED status is_active() | Returns False |
| VO-CS-004 | ACTIVE can transition to RESOLVED | Returns True |
| VO-CS-005 | ACTIVE can transition to ESCALATED | Returns True |
| VO-CS-006 | RESOLVED cannot transition | Returns False |
| VO-CS-007 | ESCALATED cannot transition | Returns False |

#### 3.1.4 MessageRole Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-MR-001 | USER role is_user() | Returns True |
| VO-MR-002 | USER role is_assistant() | Returns False |
| VO-MR-003 | ASSISTANT role is_assistant() | Returns True |
| VO-MR-004 | ASSISTANT role is_user() | Returns False |

#### 3.1.5 Screenshot Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-SS-001 | Create valid JPEG screenshot (< 5MB) | Screenshot created |
| VO-SS-002 | Create valid PNG screenshot (< 5MB) | Screenshot created |
| VO-SS-003 | Create screenshot with invalid MIME type | ValueError raised |
| VO-SS-004 | Create screenshot exceeding 5MB | ValueError raised |
| VO-SS-005 | Create screenshot with empty filename | ValueError raised |
| VO-SS-006 | is_valid_format() for JPEG | Returns True |
| VO-SS-007 | is_valid_format() for invalid type | Returns False |
| VO-SS-008 | is_within_size_limit() for valid size | Returns True |
| VO-SS-009 | is_within_size_limit() for oversized | Returns False |

#### 3.1.6 Feedback Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-FB-001 | Create feedback with both fields True | Feedback created |
| VO-FB-002 | Create feedback with both fields False | Feedback created |
| VO-FB-003 | Create feedback with mixed values | Feedback created |
| VO-FB-004 | Feedback is immutable | Cannot modify after creation |

#### 3.1.7 DocumentationLink Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| VO-DL-001 | Create valid documentation link | Link created |
| VO-DL-002 | Create link with empty title | ValueError raised |
| VO-DL-003 | Create link with invalid URL | ValueError raised |
| VO-DL-004 | Relevance within valid range (0.0-1.0) | Link created |
| VO-DL-005 | Relevance outside valid range | ValueError raised |

### 3.2 Entity Tests

#### 3.2.1 Message Entity Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| EN-MSG-001 | Create user message with content | Message created |
| EN-MSG-002 | Create message with empty content | ValueError raised |
| EN-MSG-003 | Create user message with screenshot | Message created with screenshot |
| EN-MSG-004 | Create assistant message with doc links | Message created with links |
| EN-MSG-005 | Submit feedback on assistant message | Feedback added |
| EN-MSG-006 | Submit feedback on user message | ValueError raised |
| EN-MSG-007 | Submit feedback twice | ValueError raised |
| EN-MSG-008 | has_feedback() before feedback | Returns False |
| EN-MSG-009 | has_feedback() after feedback | Returns True |
| EN-MSG-010 | has_screenshot() with screenshot | Returns True |
| EN-MSG-011 | has_screenshot() without screenshot | Returns False |

### 3.3 Aggregate Tests

#### 3.3.1 Conversation Aggregate Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AG-CV-001 | Create new conversation | Conversation created with ACTIVE status |
| AG-CV-002 | Add user message to active conversation | Message added |
| AG-CV-003 | Add assistant message to active conversation | Message added |
| AG-CV-004 | Add message to escalated conversation | ValueError raised |
| AG-CV-005 | Add message to resolved conversation | ValueError raised |
| AG-CV-006 | Add user message with screenshot | Message added with screenshot |
| AG-CV-007 | Add assistant message with screenshot | ValueError raised |
| AG-CV-008 | Add assistant message with doc links | Message added with links |
| AG-CV-009 | Add user message with doc links | ValueError raised |
| AG-CV-010 | Mark active conversation as resolved | Status changed to RESOLVED |
| AG-CV-011 | Mark conversation with no messages as resolved | ValueError raised |
| AG-CV-012 | Mark resolved conversation as resolved | ValueError raised |
| AG-CV-013 | Escalate active conversation | Status changed to ESCALATED |
| AG-CV-014 | Escalate already escalated conversation | ValueError raised |
| AG-CV-015 | Escalate resolved conversation | ValueError raised |
| AG-CV-016 | is_owned_by() with correct user | Returns True |
| AG-CV-017 | is_owned_by() with different user | Returns False |
| AG-CV-018 | can_add_message() for active | Returns True |
| AG-CV-019 | can_add_message() for escalated | Returns False |
| AG-CV-020 | get_recent_messages() with limit | Returns limited messages |
| AG-CV-021 | Messages ordered by timestamp | Messages in chronological order |
| AG-CV-022 | Title auto-generated from first message | Title set correctly |
| AG-CV-023 | Title truncated at 50 chars | Title truncated with "..." |
| AG-CV-024 | find_message() with valid ID | Returns message |
| AG-CV-025 | find_message() with invalid ID | Returns None |

### 3.4 Domain Service Tests

#### 3.4.1 ScreenshotValidationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| DS-SV-001 | Validate valid JPEG screenshot | ValidationResult.is_valid = True |
| DS-SV-002 | Validate valid PNG screenshot | ValidationResult.is_valid = True |
| DS-SV-003 | Validate invalid MIME type | ValidationResult.is_valid = False with error |
| DS-SV-004 | Validate oversized screenshot | ValidationResult.is_valid = False with error |
| DS-SV-005 | Sanitize filename with path separators | Path separators replaced |
| DS-SV-006 | Sanitize filename with special chars | Special chars replaced |
| DS-SV-007 | Sanitize filename exceeding 255 chars | Filename truncated |
| DS-SV-008 | Sanitize normal filename | Filename unchanged |

#### 3.4.2 ConversationHistoryService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| DS-CH-001 | Get conversation history for user | Returns user's conversations |
| DS-CH-002 | Get history with limit | Returns limited conversations |
| DS-CH-003 | Cleanup old conversations (> 30 days) | Old conversations deleted |
| DS-CH-004 | can_continue_conversation() for owner | Returns True |
| DS-CH-005 | can_continue_conversation() for non-owner | Returns False |

### 3.5 Application Service Tests

#### 3.5.1 SubmitQueryApplicationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AS-SQ-001 | Submit query with valid token (new conversation) | Conversation created, messages added |
| AS-SQ-002 | Submit query with invalid token | Authentication error |
| AS-SQ-003 | Submit query to existing conversation | Message added to existing |
| AS-SQ-004 | Submit query to non-existent conversation | ValueError raised |
| AS-SQ-005 | Submit query to conversation owned by other user | Authorization error |
| AS-SQ-006 | Submit query with valid screenshot | Screenshot stored, message added |
| AS-SQ-007 | Submit query with invalid screenshot format | Validation error |
| AS-SQ-008 | Submit query with oversized screenshot | Validation error |
| AS-SQ-009 | AI response includes documentation links | Links added to assistant message |
| AS-SQ-010 | ConversationCreated event published for new | Event published |
| AS-SQ-011 | MessageAdded events published | Events published for both messages |
| AS-SQ-012 | Analytics event recorded | Analytics client called |

#### 3.5.2 SubmitFeedbackApplicationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AS-SF-001 | Submit feedback with valid data | Feedback recorded |
| AS-SF-002 | Submit feedback with invalid token | Authentication error |
| AS-SF-003 | Submit feedback for non-existent conversation | ValueError raised |
| AS-SF-004 | Submit feedback for conversation owned by other | Authorization error |
| AS-SF-005 | Submit feedback for non-existent message | ValueError raised |
| AS-SF-006 | Submit feedback for user message | ValueError raised |
| AS-SF-007 | Submit feedback twice for same message | ValueError raised |
| AS-SF-008 | FeedbackSubmitted event published | Event published |
| AS-SF-009 | Analytics event recorded | Analytics client called |

#### 3.5.3 EscalateConversationApplicationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AS-EC-001 | Escalate active conversation | Status changed, email sent |
| AS-EC-002 | Escalate with invalid token | Authentication error |
| AS-EC-003 | Escalate non-existent conversation | ValueError raised |
| AS-EC-004 | Escalate conversation owned by other | Authorization error |
| AS-EC-005 | Escalate already escalated conversation | ValueError raised |
| AS-EC-006 | Escalate with reason | Reason included in event |
| AS-EC-007 | Escalation email sent | Communication client called |
| AS-EC-008 | ConversationEscalated event published | Event published |
| AS-EC-009 | Analytics event recorded | Analytics client called |
| AS-EC-010 | Conversation history included in email | History built correctly |

#### 3.5.4 GetConversationApplicationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AS-GC-001 | Get conversation with valid token | Conversation returned |
| AS-GC-002 | Get conversation with invalid token | Authentication error |
| AS-GC-003 | Get non-existent conversation | ValueError raised |
| AS-GC-004 | Get conversation owned by other user | Authorization error |
| AS-GC-005 | Response includes all messages | All messages in response |

#### 3.5.5 ListConversationsApplicationService Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| AS-LC-001 | List conversations with valid token | User's conversations returned |
| AS-LC-002 | List conversations with invalid token | Authentication error |
| AS-LC-003 | List with pagination (limit/offset) | Paginated results |
| AS-LC-004 | List returns only user's conversations | No other user's conversations |
| AS-LC-005 | List includes total count | Total count in response |

### 3.6 Controller Tests (API Integration)

#### 3.6.1 ConversationController Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| CT-CC-001 | GET /conversations - valid auth | 200 with conversation list |
| CT-CC-002 | GET /conversations - no auth header | 401 Unauthorized |
| CT-CC-003 | GET /conversations - invalid token | 401 Unauthorized |
| CT-CC-004 | GET /conversations - with pagination | 200 with paginated results |
| CT-CC-005 | GET /conversations/{id} - valid | 200 with conversation |
| CT-CC-006 | GET /conversations/{id} - not found | 404 Not Found |
| CT-CC-007 | GET /conversations/{id} - not owner | 403 Forbidden |
| CT-CC-008 | POST /conversations/{id}/escalate - valid | 200 with escalation response |
| CT-CC-009 | POST /conversations/{id}/escalate - already escalated | 409 Conflict |
| CT-CC-010 | POST /conversations/{id}/escalate - not owner | 403 Forbidden |

#### 3.6.2 MessageController Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| CT-MC-001 | POST /conversations/{id}/messages - new conversation | 200 with message response |
| CT-MC-002 | POST /conversations/{id}/messages - existing conversation | 200 with message response |
| CT-MC-003 | POST /conversations/{id}/messages - with screenshot | 200 with screenshot URL |
| CT-MC-004 | POST /conversations/{id}/messages - empty query | 400 Bad Request |
| CT-MC-005 | POST /conversations/{id}/messages - invalid screenshot | 400 Bad Request |
| CT-MC-006 | POST /conversations/{id}/messages - no auth | 401 Unauthorized |
| CT-MC-007 | POST /conversations/{id}/feedback - valid | 200 with feedback response |
| CT-MC-008 | POST /conversations/{id}/feedback - duplicate | 409 Conflict |
| CT-MC-009 | POST /conversations/{id}/feedback - user message | 400 Bad Request |
| CT-MC-010 | POST /conversations/{id}/feedback - not owner | 403 Forbidden |

### 3.7 Infrastructure Tests

#### 3.7.1 InMemoryConversationRepository Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| IF-CR-001 | Save new conversation | Conversation persisted |
| IF-CR-002 | Save updated conversation | Changes persisted |
| IF-CR-003 | Find by ID - exists | Conversation returned |
| IF-CR-004 | Find by ID - not exists | None returned |
| IF-CR-005 | Find by user ID | User's conversations returned |
| IF-CR-006 | Find by user ID with pagination | Paginated results |
| IF-CR-007 | Find recent by user ID | Recent conversations returned |
| IF-CR-008 | Delete conversation | Conversation removed |
| IF-CR-009 | Delete older than days | Old conversations removed |

#### 3.7.2 InMemoryScreenshotStorage Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| IF-SS-001 | Store screenshot | URL returned |
| IF-SS-002 | Retrieve stored screenshot | Content returned |
| IF-SS-003 | Retrieve non-existent screenshot | None/error returned |
| IF-SS-004 | Delete screenshot | Screenshot removed |

#### 3.7.3 InMemoryEventPublisher Tests
| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| IF-EP-001 | Publish event | Event stored/logged |
| IF-EP-002 | Get published events | Events returned |
| IF-EP-003 | Clear events | Events cleared |

---

## 4. Test Data Requirements

### 4.1 Mock Users
- Valid user with UUID and token
- Invalid/expired token scenarios
- Multiple users for ownership tests

### 4.2 Mock AI Responses
- Response with documentation links
- Response without documentation links
- AI service error scenarios

### 4.3 Mock Screenshots
- Valid JPEG under 5MB
- Valid PNG under 5MB
- Invalid format (GIF, BMP)
- Oversized file (> 5MB)

---

## 5. Questions for Clarification

[Question] Should we test rate limiting at the API layer, or is that handled by an API gateway?
[Answer] 

[Question] For the 30-day retention policy tests, should we use time mocking or actual date manipulation?
[Answer] 

[Question] Should integration tests use a real PostgreSQL database or continue with in-memory repository?
[Answer] 

---

## 6. Approval

**Prepared by:** QA Engineer  
**Date:** January 27, 2026

**Reviewed by:** _______________  
**Date:** _______________

**Approved by:** _______________  
**Date:** _______________

---

## 7. Notes

- Test coverage target: 80%+
- All tests should be independent and repeatable
- Use fixtures for common test data setup
- Mock external service clients in unit tests
- Use pytest markers to categorize tests (unit, integration, slow)
