# Domain Model - Unit 2: Access Control Service

## Document Information
**Bounded Context:** Access Control Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Technology:** Python/JavaScript  
**Database Schema:** `access_control`

---

## Bounded Context Definition

**Purpose:** Manage authentication, authorization, and access control for all system resources.

**Responsibilities:**
- Authenticate users (username/password)
- Manage user sessions and JWT tokens
- Enforce role-based access control (RBAC)
- Filter documents based on user permissions
- Provide centralized permission verification
- Audit security events

**MVP Authorization Scope:**
- **Two roles only**: END_USER, ADMINISTRATOR
- **Two access levels**: BASIC (for end users), ALL (for administrators)
- **Document filtering**: Based on access level (public, basic, advanced)
- **Feature access**: Conversation ownership, dashboard access (admin only)
- **Future-ready entities**: User, Role, Permission structures designed to support fine-grained RBAC post-MVP

**What This Context Does NOT Do:**
- Store conversation data (belongs to Chat Interface Context)
- Process AI queries (belongs to AI Orchestration Context)
- Search documents (belongs to Document Repository Context)

**Special Role:** This is a **Shared Kernel** - all other contexts depend on it for authentication and authorization.

---

## Aggregates

### 1. User (Aggregate Root)

**Description:** Represents a person who uses the system with their credentials and permissions.

**Aggregate Root:** User

**Entities:**
- User (root)
- Session

**Value Objects:**
- UserId
- Username
- Password (hashed)
- Email
- Role
- AccessLevel

**Invariants:**
- A user must have exactly one role
- A user must have a valid email address
- Username must be unique across the system
- Password must meet security requirements (hashed)
- A user can have multiple active sessions
- Sessions must have valid expiration times

**Lifecycle:**
- Created by administrator
- Activated upon first login
- Can be deactivated (soft delete)
- Sessions created on login, expired after timeout

---

## Entities

### User (Aggregate Root)

**Identity:** UserId (UUID)

**Attributes:**
- userId: UserId
- username: Username
- password: Password (hashed with bcrypt)
- email: Email
- role: Role
- accessLevel: AccessLevel
- isActive: Boolean
- createdAt: Timestamp
- lastLoginAt: Timestamp

**Behaviors:**
- authenticate(plainPassword): Boolean
- changePassword(oldPassword, newPassword): void
- login(): Session
- logout(sessionId): void
- hasPermission(permission): Boolean
- canAccessDocument(documentAccessLevel): Boolean
- deactivate(): void
- activate(): void
- updateLastLogin(): void

**Business Rules:**
- Password must be hashed before storage (never store plain text)
- Username cannot be changed after creation
- Email must be unique
- End Users have "basic" access level
- Administrators have "all" access level
- Inactive users cannot login
- Last login timestamp updated on successful authentication

---

### Session (Entity within User)

**Identity:** SessionId (UUID)

**Attributes:**
- sessionId: SessionId
- userId: UserId
- accessToken: JWTToken
- refreshToken: JWTToken
- createdAt: Timestamp
- expiresAt: Timestamp
- lastActivityAt: Timestamp
- ipAddress: String (optional)
- userAgent: String (optional)

**Behaviors:**
- isValid(): Boolean
- isExpired(): Boolean
- refresh(): JWTToken
- revoke(): void
- updateActivity(): void

**Business Rules:**
- Access token expires after 1 hour
- Refresh token expires after 7 days
- Expired sessions cannot be refreshed
- Revoked sessions cannot be reactivated
- **Session activity tracking**: lastActivityAt updated on each validated API call (responsibility of this service, not delegated)

---

## Value Objects

### UserId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): Boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### Username

**Attributes:**
- value: String

**Behaviors:**
- equals(other): Boolean
- toString(): String
- isValid(): Boolean

**Invariants:**
- Length: 3-50 characters
- Alphanumeric and underscore only
- Case-insensitive for uniqueness
- Cannot be empty

---

### Password

**Attributes:**
- hashedValue: String (bcrypt hash)

**Behaviors:**
- verify(plainPassword): Boolean
- hash(plainPassword): Password
- meetsRequirements(plainPassword): Boolean

**Invariants:**
- Must be hashed with bcrypt (cost factor 12)
- Plain password requirements (for MVP):
  - Minimum 8 characters
  - At least one letter
  - At least one number
- Never store or log plain text passwords

---

### Email

**Attributes:**
- value: String

**Behaviors:**
- equals(other): Boolean
- toString(): String
- isValid(): Boolean

**Invariants:**
- Must be valid email format (RFC 5322)
- Must be unique across system
- Cannot be empty

---

### Role

**Attributes:**
- value: Enum (END_USER, ADMINISTRATOR)

**Behaviors:**
- isEndUser(): Boolean
- isAdministrator(): Boolean
- getPermissions(): List<Permission>
- canAccessFeature(feature): Boolean

**Invariants:**
- Must be one of the defined roles
- Each role has predefined permissions

**Role Definitions:**

**END_USER:**
- Submit queries
- View own conversations
- Provide feedback
- Escalate to support
- Access basic and public documents

**ADMINISTRATOR:**
- All END_USER permissions
- View analytics dashboard
- Manage users (create, edit, deactivate)
- View all conversations
- Access all documents (public, basic, advanced)

---

### AccessLevel

**Attributes:**
- value: Enum (BASIC, ALL)

**Behaviors:**
- canAccess(documentAccessLevel): Boolean
- isBasic(): Boolean
- isAll(): Boolean

**Invariants:**
- END_USER role → BASIC access level
- ADMINISTRATOR role → ALL access level

**Access Level Rules:**
- BASIC: Can access "public" and "basic" documents
- ALL: Can access all documents (public, basic, advanced)

---

### Permission

**Attributes:**
- resource: String (e.g., "conversations", "analytics", "users")
- action: String (e.g., "read", "write", "delete")

**Behaviors:**
- matches(resource, action): Boolean
- toString(): String

**Invariants:**
- Resource and action must not be empty

---

### JWTToken

**Attributes:**
- value: String (JWT encoded)
- issuedAt: Timestamp
- expiresAt: Timestamp

**Behaviors:**
- isExpired(): Boolean
- isValid(): Boolean
- decode(): TokenPayload
- getRemainingTime(): Duration

**Invariants:**
- Must be valid JWT format
- Must have expiration time
- Must contain userId in payload

---

## Domain Events

### UserAuthenticated

**Attributes:**
- userId: UserId
- sessionId: SessionId
- authenticatedAt: Timestamp
- ipAddress: String

**Triggered When:** User successfully logs in

**Consumers:** 
- Communication & Analytics Context (for audit logging)
- Internal (for session tracking)

---

### UserAuthenticationFailed

**Attributes:**
- username: Username
- attemptedAt: Timestamp
- ipAddress: String
- reason: String

**Triggered When:** Login attempt fails

**Consumers:** 
- Internal (for rate limiting and security monitoring)
- Communication & Analytics Context (for security audit)

---

### SessionCreated

**Attributes:**
- sessionId: SessionId
- userId: UserId
- createdAt: Timestamp
- expiresAt: Timestamp

**Triggered When:** New session is created on login

**Consumers:** Internal (for session management)

---

### SessionExpired

**Attributes:**
- sessionId: SessionId
- userId: UserId
- expiredAt: Timestamp

**Triggered When:** Session expires

**Consumers:** Internal (for cleanup)

---

### SessionRevoked

**Attributes:**
- sessionId: SessionId
- userId: UserId
- revokedAt: Timestamp
- reason: String (logout, admin action, security)

**Triggered When:** User logs out or session is revoked

**Consumers:** Internal (for session cleanup)

---

### UserCreated

**Attributes:**
- userId: UserId
- username: Username
- role: Role
- createdBy: UserId (administrator)
- createdAt: Timestamp

**Triggered When:** Administrator creates a new user

**Consumers:** Communication & Analytics Context (for audit)

---

### UserDeactivated

**Attributes:**
- userId: UserId
- deactivatedBy: UserId (administrator)
- deactivatedAt: Timestamp
- reason: String

**Triggered When:** Administrator deactivates a user

**Consumers:** 
- Internal (revoke all sessions)
- Communication & Analytics Context (for audit)

---

## Repositories

### IUserRepository

**Purpose:** Persist and retrieve User aggregates

**Methods:**
- save(user: User): void
- findById(userId: UserId): User
- findByUsername(username: Username): User
- findByEmail(email: Email): User
- findAll(limit: Integer, offset: Integer): List<User>
- existsByUsername(username: Username): Boolean
- existsByEmail(email: Email): Boolean
- delete(userId: UserId): void

**Implementation Notes:**
- Uses `access_control.users` and `access_control.sessions` tables
- Implements unique constraints on username and email
- Passwords stored as bcrypt hashes

---

### ISessionRepository

**Purpose:** Persist and retrieve Session entities

**Methods:**
- save(session: Session): void
- findById(sessionId: SessionId): Session
- findByUserId(userId: UserId): List<Session>
- findByAccessToken(token: String): Session
- deleteExpired(): Integer
- revokeAllForUser(userId: UserId): void

**Implementation Notes:**
- Uses `access_control.sessions` table
- Implements TTL for automatic cleanup
- Indexes on accessToken for fast lookup

---

## Domain Services

### AuthenticationService

**Purpose:** Handle user authentication logic

**Methods:**
- authenticate(username: Username, password: String): AuthenticationResult
- validateToken(token: JWTToken): ValidationResult
- refreshToken(refreshToken: JWTToken): JWTToken

**Business Rules:**
- Maximum 5 failed login attempts per username per 15 minutes
- Tokens must be validated on every request
- Refresh tokens can only be used once

**Rationale:** This is a domain service because it orchestrates authentication across User and Session entities and enforces security policies.

---

### AuthorizationService

**Purpose:** Enforce access control and permissions

**Methods:**
- canAccessResource(userId: UserId, resource: String, action: String): Boolean
- filterDocumentsByAccess(documents: List<Document>, userId: UserId): List<Document>
- hasPermission(userId: UserId, permission: Permission): Boolean

**Business Rules:**
- All document access must be filtered by user's access level
- Administrators can access all resources
- End Users have restricted access

**Rationale:** This is a domain service because it operates across multiple aggregates and enforces centralized authorization rules.

---

### PasswordPolicyService

**Purpose:** Enforce password security requirements

**Methods:**
- validatePassword(plainPassword: String): ValidationResult
- hashPassword(plainPassword: String): Password
- verifyPassword(plainPassword: String, hashedPassword: Password): Boolean

**Business Rules:**
- Minimum 8 characters
- Must contain at least one letter and one number
- Passwords hashed with bcrypt (cost factor 12)
- Never log or store plain text passwords

**Rationale:** This is a domain service because it contains security policies that apply across all User aggregates.

---

## Application Services

### LoginApplicationService

**Purpose:** Orchestrate user login workflow

**Responsibilities:**
1. Validate username and password format
2. Call AuthenticationService to authenticate
3. Create session for user
4. Generate JWT tokens
5. Publish UserAuthenticated event
6. Return tokens to client

**Not a Domain Service because:** It orchestrates workflow and handles infrastructure concerns (JWT generation).

---

### LogoutApplicationService

**Purpose:** Orchestrate user logout workflow

**Responsibilities:**
1. Validate access token
2. Retrieve session
3. Revoke session
4. Publish SessionRevoked event
5. Return confirmation

---

### ValidateTokenApplicationService

**Purpose:** Validate JWT tokens for other contexts

**Responsibilities:**
1. Decode JWT token
2. Verify signature and expiration
3. Retrieve user and session
4. Return user information

---

### FilterDocumentsApplicationService

**Purpose:** Filter documents based on user access level

**Responsibilities:**
1. Validate user token
2. Retrieve user and access level
3. Call AuthorizationService to filter documents
4. Return filtered document list

---

## Policies

### PasswordPolicy

**Rule:** Passwords must meet minimum security requirements

**Implementation:**
- Enforced by PasswordPolicyService
- Validated on user creation and password change
- Minimum 8 characters, at least one letter and one number

---

### SessionExpirationPolicy

**Rule:** Sessions must expire after defined periods

**Implementation:**
- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Expired sessions automatically cleaned up daily

---

### RateLimitingPolicy

**Rule:** Limit failed login attempts to prevent brute force attacks

**Implementation:**
- Maximum 5 failed attempts per username per 15 minutes
- Temporary account lockout after threshold
- Tracked via AuthenticationService

---

### AccessLevelPolicy

**Rule:** User's role determines their access level

**Implementation:**
- END_USER → BASIC access level
- ADMINISTRATOR → ALL access level
- Enforced on user creation and role change

---

## Business Rules Summary

### User Rules
1. Username must be unique (case-insensitive)
2. Email must be unique
3. Password must be hashed (never store plain text)
4. Each user has exactly one role
5. Role determines access level
6. Inactive users cannot login
7. Last login timestamp updated on successful authentication

### Session Rules
1. Access token expires after 1 hour
2. Refresh token expires after 7 days
3. Expired sessions cannot be refreshed
4. Revoked sessions cannot be reactivated
5. User can have multiple active sessions
6. All sessions revoked when user is deactivated

### Authentication Rules
1. Maximum 5 failed login attempts per 15 minutes
2. Passwords must meet security requirements
3. Tokens must be validated on every request
4. Refresh tokens can only be used once

### Authorization Rules
1. All document access filtered by user's access level
2. BASIC access: public and basic documents only
3. ALL access: all documents
4. Administrators can access all resources
5. Users can only access their own conversations (except administrators)

---

## Aggregate Relationships

```
User (Aggregate Root)
├── userId: UserId (identity)
├── username: Username (value object, unique)
├── password: Password (value object, hashed)
├── email: Email (value object, unique)
├── role: Role (value object)
├── accessLevel: AccessLevel (value object)
├── isActive: Boolean
├── Sessions (entities, 1-to-many)
│   ├── Session 1
│   │   ├── sessionId: SessionId
│   │   ├── accessToken: JWTToken
│   │   ├── refreshToken: JWTToken
│   │   ├── expiresAt: Timestamp
│   │   └── lastActivityAt: Timestamp
│   ├── Session 2
│   └── Session N
└── Timestamps (createdAt, lastLoginAt)
```

---

## Consistency Boundaries

**Strong Consistency (within aggregate):**
- User authentication and session creation are atomic
- Password changes are immediately consistent
- Session revocation is immediate

**Eventual Consistency (across aggregates):**
- Security audit events published asynchronously
- Session cleanup happens periodically
- Failed login tracking may have slight delay

---

## Integration Points

### Inbound (APIs this context provides)

**REST Endpoints:**
- POST /api/v1/auth/login - Authenticate user
- POST /api/v1/auth/logout - Logout user
- POST /api/v1/auth/validate - Validate token
- POST /api/v1/auth/refresh - Refresh token
- POST /api/v1/auth/filter-documents - Filter documents by access
- GET /api/v1/auth/users/{userId} - Get user profile
- POST /api/v1/auth/users - Create user (admin only)
- PUT /api/v1/auth/users/{userId} - Update user (admin only)
- DELETE /api/v1/auth/users/{userId} - Deactivate user (admin only)

### Outbound (APIs this context consumes)

**None** - This is a foundational service with no outbound dependencies.

---

## Infrastructure Concerns

**Not part of domain model, but noted for completeness:**

- JWT token generation and validation (using library like PyJWT or jsonwebtoken)
- Password hashing (bcrypt)
- Database persistence (PostgreSQL with `access_control` schema)
- Rate limiting (Redis or in-memory cache)
- Security audit logging
- Token blacklist for revoked tokens

---

## Security Considerations

1. **Password Security:**
   - Never store plain text passwords
   - Use bcrypt with cost factor 12
   - Never log passwords

2. **Token Security:**
   - Short-lived access tokens (1 hour)
   - Longer refresh tokens (7 days)
   - Tokens signed with secret key
   - Validate on every request

3. **Session Security:**
   - Track IP address and user agent
   - Detect suspicious activity
   - Revoke all sessions on password change

4. **Rate Limiting:**
   - Prevent brute force attacks
   - Limit failed login attempts
   - Temporary lockout after threshold

5. **Audit Logging:**
   - Log all authentication events
   - Log authorization failures
   - Log user management actions

---

## Notes

- This context is the foundation for all other contexts
- All contexts depend on this for authentication and authorization
- Implements JWT-based stateless authentication
- Centralized access control ensures consistent security
- Domain events enable security audit trail
- MVP uses simple username/password (SSO deferred to post-MVP)

