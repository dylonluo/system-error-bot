# Logical Design - Unit 2: Access Control Service

## Document Information
**Bounded Context:** Access Control Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Architecture Style:** Simplified Layered Architecture  
**Technology Stack:** Python/FastAPI or Node.js/Express (framework-agnostic design)  
**Special Role:** Shared Kernel - Foundation for all other contexts

---

## 1. Architecture Overview

### 1.1 Architectural Style
**Simplified Layered Architecture** with security-first design:

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  (REST Controllers, JWT Middleware, Request/Response)    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Application Service Layer                 │
│  (Authentication, Authorization, Token Management)       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Domain Layer                           │
│  (User Aggregate, Session Entity, Security Policies)     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                      │
│  (Repositories, JWT Provider, Password Hasher, Cache)    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles
- **Security First:** All operations prioritize security
- **Stateless Authentication:** JWT-based, no server-side session storage
- **Centralized Authorization:** Single source of truth for permissions
- **Fail Secure:** Default deny, explicit allow

---

## 2. Component Structure

### 2.1 API Layer Components

#### REST Controllers

**AuthenticationController**
- **Responsibility:** Handle authentication requests
- **Endpoints:**
  - `POST /api/v1/auth/login` → login()
  - `POST /api/v1/auth/logout` → logout()
  - `POST /api/v1/auth/refresh` → refreshToken()
  - `POST /api/v1/auth/validate` → validateToken()

**UserController**
- **Responsibility:** Handle user management (admin only)
- **Endpoints:**
  - `GET /api/v1/auth/users/{userId}` → getUser()
  - `POST /api/v1/auth/users` → createUser()
  - `PUT /api/v1/auth/users/{userId}` → updateUser()
  - `DELETE /api/v1/auth/users/{userId}` → deactivateUser()

**AuthorizationController**
- **Responsibility:** Handle authorization operations
- **Endpoints:**
  - `POST /api/v1/auth/filter-documents` → filterDocuments()

#### Middleware

**JWTAuthenticationMiddleware**
- **Responsibility:** Validate JWT token on every request
- **Operations:**
  - extractToken() - Extract from Authorization header
  - validateToken() - Verify signature and expiration
  - attachUser() - Attach user info to request context
  - handleErrors() - Return 401 for invalid tokens

#### DTOs (Data Transfer Objects)

**Request DTOs:**
- LoginRequest (username, password)
- RefreshTokenRequest (refreshToken)
- CreateUserRequest (username, email, password, role)
- UpdateUserRequest (email, role, accessLevel)
- FilterDocumentsRequest (documents array)

**Response DTOs:**
- LoginResponse (accessToken, refreshToken, expiresIn, user)
- UserResponse (id, username, email, role, accessLevel)
- ValidationResponse (valid, user)
- FilteredDocumentsResponse (filteredDocuments, removedCount)

---

### 2.2 Application Service Layer Components

#### Application Services

**LoginApplicationService**
- **Responsibility:** Orchestrate user login
- **Key Operations:**
  - validateCredentials() - Check username/password format
  - authenticate() - Call AuthenticationService
  - createSession() - Generate JWT tokens
  - updateLastLogin() - Update user's last login timestamp
  - publishEvent() - Publish UserAuthenticated event
  - returnTokens() - Return access and refresh tokens

**LogoutApplicationService**
- **Responsibility:** Orchestrate user logout
- **Key Operations:**
  - validateToken() - Verify access token
  - revokeSession() - Invalidate session
  - publishEvent() - Publish SessionRevoked event
  - returnConfirmation()

**ValidateTokenApplicationService**
- **Responsibility:** Validate JWT token and return user info
- **Key Operations:**
  - decodeToken() - Decode JWT
  - verifySignature() - Verify token signature
  - checkExpiration() - Check if token expired
  - retrieveUser() - Get user from database
  - returnUserInfo()

**FilterDocumentsApplicationService**
- **Responsibility:** Filter documents based on user access level
- **Key Operations:**
  - validateToken()
  - retrieveUser()
  - filterByAccessLevel() - Call AuthorizationService
  - returnFilteredDocuments()

**CreateUserApplicationService**
- **Responsibility:** Create new user (admin only)
- **Key Operations:**
  - validateAdminPermission()
  - validateUserData()
  - hashPassword() - Call PasswordPolicyService
  - createUser()
  - assignRole()
  - publishEvent() - Publish UserCreated event
  - returnUser()

---

### 2.3 Domain Layer Components

#### Aggregates

**User (Aggregate Root)**
- **Identity:** UserId
- **Entities:** Session (collection)
- **Value Objects:** Username, Password, Email, Role, AccessLevel
- **Key Methods:**
  - authenticate(plainPassword) → Boolean
  - changePassword(oldPassword, newPassword) → void
  - login() → Session
  - logout(sessionId) → void
  - hasPermission(permission) → Boolean
  - canAccessDocument(documentAccessLevel) → Boolean
  - deactivate() → void
  - activate() → void
  - updateLastLogin() → void

#### Entities

**Session**
- **Identity:** SessionId
- **Attributes:** accessToken, refreshToken, createdAt, expiresAt, lastActivityAt
- **Key Methods:**
  - isValid() → Boolean
  - isExpired() → Boolean
  - refresh() → JWTToken
  - revoke() → void
  - updateActivity() → void

#### Value Objects

**UserId** - UUID wrapper
**Username** - String with validation (3-50 chars, alphanumeric)
**Password** - Hashed value with bcrypt
**Email** - String with email format validation
**Role** - Enum (END_USER, ADMINISTRATOR) with permissions
**AccessLevel** - Enum (BASIC, ALL) with document access rules
**Permission** - resource + action pair
**JWTToken** - JWT string with expiration

#### Domain Services

**AuthenticationService**
- **Responsibility:** Handle authentication logic
- **Operations:**
  - authenticate(username, password) → AuthenticationResult
  - validateToken(token) → ValidationResult
  - refreshToken(refreshToken) → JWTToken
- **Business Rules:**
  - Max 5 failed attempts per 15 minutes
  - Tokens validated on every request
  - Refresh tokens single-use only

**AuthorizationService**
- **Responsibility:** Enforce access control
- **Operations:**
  - canAccessResource(userId, resource, action) → Boolean
  - filterDocumentsByAccess(documents, userId) → List<Document>
  - hasPermission(userId, permission) → Boolean
- **Business Rules:**
  - BASIC access: public + basic documents
  - ALL access: all documents
  - Administrators can access all resources

**PasswordPolicyService**
- **Responsibility:** Enforce password security
- **Operations:**
  - validatePassword(plainPassword) → ValidationResult
  - hashPassword(plainPassword) → Password
  - verifyPassword(plainPassword, hashedPassword) → Boolean
- **Business Rules:**
  - Minimum 8 characters
  - At least one letter and one number
  - Bcrypt with cost factor 12

#### Domain Events

- UserAuthenticated
- UserAuthenticationFailed
- SessionCreated
- SessionExpired
- SessionRevoked
- UserCreated
- UserDeactivated

---

### 2.4 Infrastructure Layer Components

#### Repositories

**UserRepository (implements IUserRepository)**
- **Responsibility:** Persist and retrieve User aggregates
- **Operations:**
  - save(user) → void
  - findById(userId) → User
  - findByUsername(username) → User
  - findByEmail(email) → User
  - findAll(limit, offset) → List<User>
  - existsByUsername(username) → Boolean
  - existsByEmail(email) → Boolean
  - delete(userId) → void
- **Implementation:** PostgreSQL with `access_control` schema

**SessionRepository (implements ISessionRepository)**
- **Responsibility:** Persist and retrieve Session entities
- **Operations:**
  - save(session) → void
  - findById(sessionId) → Session
  - findByUserId(userId) → List<Session>
  - findByAccessToken(token) → Session
  - deleteExpired() → Integer
  - revokeAllForUser(userId) → void
- **Implementation:** PostgreSQL with TTL cleanup

#### Security Infrastructure

**JWTProvider**
- **Responsibility:** Generate and validate JWT tokens
- **Operations:**
  - generateAccessToken(user) → JWTToken (1-hour expiry)
  - generateRefreshToken(user) → JWTToken (7-day expiry)
  - validateToken(token) → TokenPayload
  - decodeToken(token) → TokenPayload
- **Implementation:** JWT library (PyJWT, jsonwebtoken)

**PasswordHasher**
- **Responsibility:** Hash and verify passwords
- **Operations:**
  - hash(plainPassword) → String
  - verify(plainPassword, hashedPassword) → Boolean
- **Implementation:** bcrypt library (cost factor 12)

**RateLimiter**
- **Responsibility:** Prevent brute force attacks
- **Operations:**
  - checkLimit(username) → Boolean
  - recordAttempt(username) → void
  - resetAttempts(username) → void
- **Implementation:** Redis or in-memory cache

#### Event Publisher

**EventPublisher**
- **Responsibility:** Publish domain events
- **Operations:**
  - publish(event) → void
- **Implementation:** Message queue or HTTP webhooks

---

## 3. Data Flow Diagrams

### 3.1 Login Flow

```
User Request (username, password)
    ↓
AuthenticationController.login()
    ↓
LoginApplicationService.execute()
    ├─→ RateLimiter.checkLimit(username)
    │       ↓
    │   If exceeded → Return 429 Too Many Requests
    ├─→ UserRepository.findByUsername(username)
    │       ↓
    │   If not found → Record failed attempt → Return 401
    ├─→ User.authenticate(plainPassword)
    │   ├─→ PasswordHasher.verify(plainPassword, hashedPassword)
    │   │       ↓
    │   │   If invalid → Record failed attempt → Return 401
    │   └─→ If valid → Continue
    ├─→ User.login() → Create Session
    ├─→ JWTProvider.generateAccessToken(user)
    ├─→ JWTProvider.generateRefreshToken(user)
    ├─→ SessionRepository.save(session)
    ├─→ User.updateLastLogin()
    ├─→ UserRepository.save(user)
    ├─→ RateLimiter.resetAttempts(username)
    ├─→ EventPublisher.publish(UserAuthenticated)
    ↓
Return LoginResponse (tokens, user info)
```

### 3.2 Validate Token Flow

```
External Service Request (JWT token)
    ↓
AuthenticationController.validateToken()
    ↓
ValidateTokenApplicationService.execute()
    ├─→ JWTProvider.validateToken(token)
    │       ↓
    │   If invalid/expired → Return 401
    ├─→ JWTProvider.decodeToken(token)
    ├─→ SessionRepository.findByAccessToken(token)
    │       ↓
    │   If session revoked → Return 401
    ├─→ UserRepository.findById(userId from token)
    │       ↓
    │   If user inactive → Return 401
    ├─→ Session.updateActivity()
    ├─→ SessionRepository.save(session)
    ↓
Return ValidationResponse (valid=true, user info)
```

### 3.3 Filter Documents Flow

```
External Service Request (documents array, JWT token)
    ↓
AuthorizationController.filterDocuments()
    ↓
FilterDocumentsApplicationService.execute()
    ├─→ ValidateTokenApplicationService.execute()
    │       ↓
    │   Return User
    ├─→ AuthorizationService.filterDocumentsByAccess(documents, user)
    │   ├─→ For each document:
    │   │   ├─→ User.canAccessDocument(document.accessLevel)
    │   │   │   ├─→ If user.accessLevel = BASIC:
    │   │   │   │       Allow if document.accessLevel in [public, basic]
    │   │   │   └─→ If user.accessLevel = ALL:
    │   │   │           Allow all documents
    │   │   └─→ Include if allowed, exclude if not
    │   └─→ Return filtered list
    ↓
Return FilteredDocumentsResponse (filtered documents, removed count)
```

---

## 4. Database Schema Design

### 4.1 Schema: `access_control`

#### Table: `users`
```
users
├── user_id (UUID, PK)
├── username (VARCHAR(50), UNIQUE, NOT NULL)
├── password_hash (VARCHAR(255), NOT NULL)
├── email (VARCHAR(255), UNIQUE, NOT NULL)
├── role (ENUM: end_user, administrator, NOT NULL)
├── access_level (ENUM: basic, all, NOT NULL)
├── is_active (BOOLEAN, DEFAULT true)
├── created_at (TIMESTAMP, NOT NULL)
├── last_login_at (TIMESTAMP, nullable)
└── UNIQUE INDEX on username (case-insensitive)
└── UNIQUE INDEX on email (case-insensitive)
```

#### Table: `sessions`
```
sessions
├── session_id (UUID, PK)
├── user_id (UUID, FK to users, NOT NULL)
├── access_token_hash (VARCHAR(255), UNIQUE, NOT NULL)
├── refresh_token_hash (VARCHAR(255), UNIQUE, NOT NULL)
├── created_at (TIMESTAMP, NOT NULL)
├── expires_at (TIMESTAMP, NOT NULL)
├── last_activity_at (TIMESTAMP, NOT NULL)
├── ip_address (VARCHAR(45), nullable)
├── user_agent (TEXT, nullable)
├── is_revoked (BOOLEAN, DEFAULT false)
└── INDEX on user_id
└── INDEX on access_token_hash
└── INDEX on expires_at (for cleanup)
```

#### Table: `failed_login_attempts`
```
failed_login_attempts
├── attempt_id (UUID, PK)
├── username (VARCHAR(50), NOT NULL)
├── ip_address (VARCHAR(45), nullable)
├── attempted_at (TIMESTAMP, NOT NULL)
└── INDEX on username, attempted_at (for rate limiting)
```

### 4.2 Relationships
- One User has many Sessions (1:N)
- Failed login attempts tracked separately (no FK)

---

## 5. API-to-Component Mapping

### 5.1 Endpoint Mappings

| HTTP Method | Endpoint | Controller | Application Service | Domain Aggregate |
|-------------|----------|------------|---------------------|------------------|
| POST | /api/v1/auth/login | AuthenticationController | LoginApplicationService | User, Session |
| POST | /api/v1/auth/logout | AuthenticationController | LogoutApplicationService | Session |
| POST | /api/v1/auth/refresh | AuthenticationController | RefreshTokenApplicationService | Session |
| POST | /api/v1/auth/validate | AuthenticationController | ValidateTokenApplicationService | User, Session |
| POST | /api/v1/auth/filter-documents | AuthorizationController | FilterDocumentsApplicationService | User |
| GET | /api/v1/auth/users/{userId} | UserController | GetUserApplicationService | User |
| POST | /api/v1/auth/users | UserController | CreateUserApplicationService | User |
| PUT | /api/v1/auth/users/{userId} | UserController | UpdateUserApplicationService | User |
| DELETE | /api/v1/auth/users/{userId} | UserController | DeactivateUserApplicationService | User |

---

## 6. Integration Points

### 6.1 Outbound Integrations

**None** - This is a foundational service with no external dependencies

### 6.2 Inbound Integrations

**All Other Contexts** - All contexts call this service for:
- Token validation
- User information retrieval
- Document filtering by access level
- Permission verification

---

## 7. Error Handling Strategy

### 7.1 Error Categories

**Authentication Errors (401 Unauthorized)**
- Invalid credentials
- Invalid token
- Expired token
- Revoked session
- Inactive user

**Authorization Errors (403 Forbidden)**
- Insufficient permissions
- Non-admin trying to access admin endpoints

**Validation Errors (400 Bad Request)**
- Invalid username format
- Invalid email format
- Password doesn't meet requirements
- Missing required fields

**Conflict Errors (409 Conflict)**
- Username already exists
- Email already exists

**Rate Limit Errors (429 Too Many Requests)**
- Too many failed login attempts
- Rate limit exceeded

**Server Errors (500 Internal Server Error)**
- Database connection failure
- JWT generation failure

### 7.2 Security Considerations for Errors

**Never reveal:**
- Whether username exists (use generic "Invalid credentials")
- Password requirements in error (show on registration page only)
- Internal system details

**Always log:**
- Failed login attempts with IP address
- Token validation failures
- Permission denials

---

## 8. Security Considerations

### 8.1 Password Security
- Bcrypt hashing with cost factor 12
- Never store plain text passwords
- Never log passwords (plain or hashed)
- Password requirements enforced on creation/change

### 8.2 Token Security
- JWT signed with secret key (HS256 or RS256)
- Access token: 1-hour expiration
- Refresh token: 7-day expiration
- Tokens stored as hashes in database
- Revoked tokens tracked in database

### 8.3 Session Security
- Track IP address and user agent
- Detect suspicious activity (IP changes)
- Revoke all sessions on password change
- Automatic cleanup of expired sessions

### 8.4 Rate Limiting
- Max 5 failed login attempts per 15 minutes per username
- Max 100 requests per minute per user (general)
- Temporary account lockout after threshold

### 8.5 Audit Logging
- Log all authentication events
- Log all authorization failures
- Log user management actions
- Include correlation IDs for tracing

---

## 9. Performance Considerations

### 9.1 Token Validation Optimization
- Cache user info for 1 minute (reduce DB queries)
- Cache token validation results for 30 seconds
- Use Redis for rate limiting (fast lookups)

### 9.2 Database Optimization
- Indexes on username, email, access_token_hash
- Connection pooling
- Prepared statements for SQL injection prevention

### 9.3 Password Hashing
- Bcrypt is intentionally slow (security feature)
- Consider async hashing for non-blocking operations
- Cost factor 12 balances security and performance

### 9.4 Response Time Targets
- Login: < 500ms (including bcrypt verification)
- Validate token: < 100ms (with caching)
- Filter documents: < 200ms
- Create user: < 300ms

---

## 10. Deployment Considerations

### 10.1 Service Deployment
- Containerized application (Docker)
- Stateless service (horizontal scaling possible)
- Environment-specific secrets (JWT secret, DB credentials)

### 10.2 Database Deployment
- PostgreSQL with `access_control` schema
- Automated migrations on deployment
- Backup strategy: Daily full backup

### 10.3 Secret Management
- JWT secret stored in environment variable or secret manager
- Database credentials in secret manager
- Never commit secrets to version control

### 10.4 Monitoring
- Health check endpoint: `GET /health`
- Metrics: Login success/failure rate, token validation rate
- Alerts: High failed login rate, token validation failures
- Security alerts: Brute force attempts, suspicious activity

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Domain layer: Test User aggregate, Session entity, domain services
- Password hashing and verification
- Token generation and validation
- Access level filtering logic
- Coverage target: 90%+ (security-critical)

### 11.2 Integration Tests
- API layer: Test authentication endpoints
- Database operations
- Rate limiting
- Token expiration handling

### 11.3 Security Tests
- Brute force attack simulation
- Token tampering attempts
- SQL injection attempts
- Password policy enforcement

---

## 12. Future Enhancements (Post-MVP)

- Multi-factor authentication (MFA)
- Single Sign-On (SSO) integration
- OAuth 2.0 support
- Role-based access control (RBAC) with custom roles
- Fine-grained permissions
- Password reset functionality
- Account lockout policies
- Session management UI
- Audit log viewer

---

## Notes

- This service is the foundation for all other services
- Security is the top priority
- Stateless design enables horizontal scaling
- JWT-based authentication simplifies integration
- Rate limiting prevents abuse
- Comprehensive audit logging for compliance
