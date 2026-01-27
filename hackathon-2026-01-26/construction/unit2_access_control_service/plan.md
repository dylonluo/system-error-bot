# Implementation Plan - Unit 2: Access Control Service

## Overview
This plan outlines the implementation of the Access Control Service based on the Domain-Driven Design logical design. The implementation will use Python with a simplified layered architecture, in-memory repositories, and in-memory event stores.

---

## Project Structure

```
unit2_access_control_service/
├── src/
│   ├── domain/
│   │   ├── aggregates/
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── __init__.py
│   │   ├── value_objects/
│   │   │   ├── user_id.py
│   │   │   ├── username.py
│   │   │   ├── password.py
│   │   │   ├── email.py
│   │   │   ├── role.py
│   │   │   ├── access_level.py
│   │   │   ├── permission.py
│   │   │   ├── session_id.py
│   │   │   ├── jwt_token.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── authentication_service.py
│   │   │   ├── authorization_service.py
│   │   │   ├── password_policy_service.py
│   │   │   └── __init__.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── session_repository.py
│   │   │   └── __init__.py
│   │   ├── events/
│   │   │   ├── domain_events.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── application/
│   │   ├── services/
│   │   │   ├── login_application_service.py
│   │   │   ├── logout_application_service.py
│   │   │   ├── validate_token_application_service.py
│   │   │   ├── filter_documents_application_service.py
│   │   │   ├── create_user_application_service.py
│   │   │   ├── get_user_application_service.py
│   │   │   ├── update_user_application_service.py
│   │   │   ├── deactivate_user_application_service.py
│   │   │   └── __init__.py
│   │   ├── dtos/
│   │   │   ├── requests.py
│   │   │   ├── responses.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── infrastructure/
│   │   ├── repositories/
│   │   │   ├── in_memory_user_repository.py
│   │   │   ├── in_memory_session_repository.py
│   │   │   └── __init__.py
│   │   ├── security/
│   │   │   ├── jwt_provider.py
│   │   │   ├── password_hasher.py
│   │   │   ├── rate_limiter.py
│   │   │   └── __init__.py
│   │   ├── events/
│   │   │   ├── in_memory_event_publisher.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── api/
│   │   ├── controllers/
│   │   │   ├── authentication_controller.py
│   │   │   ├── user_controller.py
│   │   │   ├── authorization_controller.py
│   │   │   └── __init__.py
│   │   ├── middleware/
│   │   │   ├── jwt_authentication_middleware.py
│   │   │   ├── error_handler.py
│   │   │   └── __init__.py
│   │   ├── main.py
│   │   └── __init__.py
│   └── __init__.py
├── demo.py
├── requirements.txt
└── README.md
```

---

## Implementation Steps

### Phase 1: Domain Layer - Value Objects
- [ ] **Step 1.1**: Create `user_id.py` - UserId value object with UUID validation
- [ ] **Step 1.2**: Create `username.py` - Username value object with validation (3-50 chars, alphanumeric)
- [ ] **Step 1.3**: Create `password.py` - Password value object with hashing and verification
- [ ] **Step 1.4**: Create `email.py` - Email value object with format validation
- [ ] **Step 1.5**: Create `role.py` - Role enum (END_USER, ADMINISTRATOR) with permissions
- [ ] **Step 1.6**: Create `access_level.py` - AccessLevel enum (BASIC, ALL) with access rules
- [ ] **Step 1.7**: Create `permission.py` - Permission value object (resource + action)
- [ ] **Step 1.8**: Create `session_id.py` - SessionId value object with UUID validation
- [ ] **Step 1.9**: Create `jwt_token.py` - JWTToken value object with expiration logic
- [ ] **Step 1.10**: Create `value_objects/__init__.py` - Export all value objects

### Phase 2: Domain Layer - Events
- [ ] **Step 2.1**: Create `domain_events.py` - Define all domain events (UserAuthenticated, SessionCreated, etc.)
- [ ] **Step 2.2**: Create `events/__init__.py` - Export all events

### Phase 3: Domain Layer - Aggregates & Entities
- [ ] **Step 3.1**: Create `session.py` - Session entity with validation, expiration, and revocation logic
- [ ] **Step 3.2**: Create `user.py` - User aggregate root with authentication, session management, and permission checks
- [ ] **Step 3.3**: Create `aggregates/__init__.py` - Export User and Session

### Phase 4: Domain Layer - Repositories (Interfaces)
- [ ] **Step 4.1**: Create `user_repository.py` - IUserRepository interface (abstract base class)
- [ ] **Step 4.2**: Create `session_repository.py` - ISessionRepository interface (abstract base class)
- [ ] **Step 4.3**: Create `repositories/__init__.py` - Export repository interfaces

### Phase 5: Domain Layer - Domain Services
- [ ] **Step 5.1**: Create `authentication_service.py` - AuthenticationService with login logic and rate limiting
- [ ] **Step 5.2**: Create `authorization_service.py` - AuthorizationService with permission checks and document filtering
- [ ] **Step 5.3**: Create `password_policy_service.py` - PasswordPolicyService with password validation and hashing
- [ ] **Step 5.4**: Create `services/__init__.py` - Export all domain services

### Phase 6: Infrastructure Layer - Security
- [ ] **Step 6.1**: Create `password_hasher.py` - PasswordHasher using bcrypt
- [ ] **Step 6.2**: Create `jwt_provider.py` - JWTProvider for token generation and validation
- [ ] **Step 6.3**: Create `rate_limiter.py` - In-memory RateLimiter for brute force prevention
- [ ] **Step 6.4**: Create `security/__init__.py` - Export all security components

### Phase 7: Infrastructure Layer - Repositories (Implementations)
- [ ] **Step 7.1**: Create `in_memory_user_repository.py` - In-memory implementation of IUserRepository
- [ ] **Step 7.2**: Create `in_memory_session_repository.py` - In-memory implementation of ISessionRepository
- [ ] **Step 7.3**: Create `repositories/__init__.py` - Export repository implementations

### Phase 8: Infrastructure Layer - Events
- [ ] **Step 8.1**: Create `in_memory_event_publisher.py` - In-memory event publisher
- [ ] **Step 8.2**: Create `events/__init__.py` - Export event publisher

### Phase 9: Application Layer - DTOs
- [ ] **Step 9.1**: Create `requests.py` - All request DTOs (LoginRequest, CreateUserRequest, etc.)
- [ ] **Step 9.2**: Create `responses.py` - All response DTOs (LoginResponse, UserResponse, etc.)
- [ ] **Step 9.3**: Create `dtos/__init__.py` - Export all DTOs

### Phase 10: Application Layer - Application Services
- [ ] **Step 10.1**: Create `login_application_service.py` - Orchestrate login workflow
- [ ] **Step 10.2**: Create `logout_application_service.py` - Orchestrate logout workflow
- [ ] **Step 10.3**: Create `validate_token_application_service.py` - Validate JWT tokens
- [ ] **Step 10.4**: Create `filter_documents_application_service.py` - Filter documents by access level
- [ ] **Step 10.5**: Create `create_user_application_service.py` - Create new user (admin only)
- [ ] **Step 10.6**: Create `get_user_application_service.py` - Get user by ID
- [ ] **Step 10.7**: Create `update_user_application_service.py` - Update user (admin only)
- [ ] **Step 10.8**: Create `deactivate_user_application_service.py` - Deactivate user (admin only)
- [ ] **Step 10.9**: Create `services/__init__.py` - Export all application services

### Phase 11: API Layer - Middleware
- [ ] **Step 11.1**: Create `error_handler.py` - Global error handler for API
- [ ] **Step 11.2**: Create `jwt_authentication_middleware.py` - JWT validation middleware
- [ ] **Step 11.3**: Create `middleware/__init__.py` - Export all middleware

### Phase 12: API Layer - Controllers
- [ ] **Step 12.1**: Create `authentication_controller.py` - Authentication endpoints (login, logout, validate, refresh)
- [ ] **Step 12.2**: Create `user_controller.py` - User management endpoints (CRUD operations)
- [ ] **Step 12.3**: Create `authorization_controller.py` - Authorization endpoints (filter documents)
- [ ] **Step 12.4**: Create `controllers/__init__.py` - Export all controllers

### Phase 13: API Layer - Main Application
- [ ] **Step 13.1**: Create `main.py` - FastAPI application setup with routes and middleware

### Phase 14: Demo & Documentation
- [ ] **Step 14.1**: Create `requirements.txt` - List all Python dependencies
- [ ] **Step 14.2**: Create `demo.py` - Comprehensive demo script showcasing all features
- [ ] **Step 14.3**: Create `README.md` - Documentation with setup and usage instructions

### Phase 15: Testing & Verification
- [ ] **Step 15.1**: Run demo script to verify implementation
- [ ] **Step 15.2**: Test all authentication flows (login, logout, token validation)
- [ ] **Step 15.3**: Test authorization flows (document filtering, permission checks)
- [ ] **Step 15.4**: Test user management flows (create, update, deactivate)
- [ ] **Step 15.5**: Test error handling and edge cases

---

## Questions for Clarification

### [Question 1] JWT Secret Key
For JWT token generation, should I use a hardcoded secret key in the demo, or would you prefer it to be configurable via environment variable?

**[Answer]**: configurable via environment variable. to make it simple, we can make the configuration in a notepad or smthg for this mvp version.

### [Question 2] Rate Limiting Configuration
The design specifies "max 5 failed attempts per 15 minutes". Should this be configurable, or hardcoded in the implementation?

**[Answer]**: configurable. can try to use the same notepad text file for the configuration.

### [Question 3] Token Expiration Times
The design specifies:
- Access token: 1 hour expiration
- Refresh token: 7 days expiration

For the demo, should I keep these durations or use shorter times (e.g., 5 minutes for access token) to make testing easier?

**[Answer]**: yes please. loves

### [Question 4] Initial Admin User
Should the demo script create an initial administrator user automatically, or should this be done manually?

**[Answer]**: automatically

### [Question 5] Document Structure for Filtering
For the `filter_documents` endpoint, what structure should the documents have? Should I assume a simple structure like:
```python
{
    "id": "doc-123",
    "title": "Document Title",
    "access_level": "basic"  # or "public", "advanced"
}
```

**[Answer]**: yes please

---

## Dependencies

The following Python packages will be required:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `bcrypt` - Password hashing
- `pyjwt` - JWT token handling
- `python-multipart` - Form data handling

---

## Success Criteria

- [ ] All domain entities and value objects implemented with proper validation
- [ ] All domain services implement business rules correctly
- [ ] In-memory repositories work correctly for CRUD operations
- [ ] JWT authentication and authorization work end-to-end
- [ ] Rate limiting prevents brute force attacks
- [ ] Document filtering works based on access levels
- [ ] Demo script successfully demonstrates all features
- [ ] Code is clean, well-documented, and follows DDD principles

---

## Notes

- Implementation will be minimal but complete
- Focus on correctness over performance (in-memory storage is acceptable)
- All business rules from the logical design must be enforced
- Error handling should be comprehensive
- Demo script should be self-contained and easy to run
