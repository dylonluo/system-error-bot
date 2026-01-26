# Unit 2: Access Control Service (MVP)

## Unit Overview
**Purpose:** Centralized authentication, authorization, and role-based access control for all system resources.

**Responsibility:** This unit ensures secure access to the system and enforces access restrictions across all units, filtering responses based on user permissions.

**Team Size:** Can be built by a single development team

**MVP Timeline:** 2-3 weeks

---

## User Stories (2 stories)

### US-020: Access System Based on Role
**As a** user with a specific role  
**I want to** access documentation appropriate to my role  
**So that** I see only content I'm authorized to view

**Priority:** Must Have (MVP)

**Acceptance Criteria:**
- End Users can access basic documentation
- Administrators can access all documentation and user management
- Role-based permissions are enforced
- Users cannot access documentation outside their permissions
- AI responses are filtered based on user's access restrictions

**MVP Simplifications:**
- Two roles only: End User and Administrator
- Basic permission model
- Simple access control rules

---

### US-021: Authenticate and Login
**As a** user  
**I want to** securely log in to the system  
**So that** my conversations are protected and my access level is determined

**Priority:** Must Have (MVP)

**Acceptance Criteria:**
- User can log in with username and password
- User session is maintained
- User can log out securely
- Unauthorized access is prevented
- User's access permissions are loaded upon login

**MVP Simplifications:**
- Basic username/password authentication (SSO deferred)
- Simple session management
- No password reset functionality in MVP

---

## Dependencies

### Inbound Dependencies (APIs this unit consumes):
- **User Database:** Local user store with username/password hashes

### Outbound Dependencies (APIs this unit provides):
- Authentication API (login, logout, token validation)
- Authorization API (role verification, permission checks)
- Access restriction filtering API (document access filtering)
- User profile API (user information retrieval)
- Session management API

---

## Key Responsibilities
1. User authentication (username/password)
2. Session management and JWT token generation
3. Role-based access control (RBAC)
4. **Centralized access restriction filtering**
5. Permission verification for all system operations
6. User profile management
7. Security audit logging
8. Token refresh and expiration handling
9. **Document-level access control**

---

## User Roles Defined (MVP)

### End User
**Permissions:**
- Submit queries and attach screenshots
- View AI responses (filtered by access level)
- Access basic NetSuite and TMS documentation
- Save conversation history
- Provide feedback (Yes/No, Solved/Not Solved)
- Escalate to human support

**Access Restrictions:**
- Cannot view advanced technical documentation
- Cannot access other users' conversations
- Cannot view admin analytics
- Limited to public and basic-level documents

### Administrator
**Permissions:**
- All End User permissions
- Access analytics dashboard
- View basic usage reports
- Manage user accounts (create, edit, delete)
- View all conversations (for support purposes)
- Access all documentation levels

**Access Restrictions:**
- None in MVP (full access)

---

## Access Restriction Filtering

### Document Access Filtering
- Each document has access level tags (public, basic, advanced)
- User's role determines accessible document levels
- Filtering applied before returning search results
- Audit log maintained for document access attempts

### Feature Access Filtering
- Admin dashboard only for Administrators
- Conversation history filtered by user ownership
- User management only for Administrators

### API Response Filtering
- All API responses filtered based on user's access level
- Sensitive data redacted for unauthorized users
- Error messages don't reveal unauthorized information
- Links only provided for accessible documents

---

## MVP Simplifications

### What's Included:
- Basic username/password authentication
- Two roles (End User, Administrator)
- Simple permission model
- Document access filtering
- JWT token-based session management

### What's Deferred:
- SSO integration
- Additional roles (IT Support Staff, Developer)
- Password reset functionality
- Multi-factor authentication
- Advanced permission models
- LDAP/Active Directory integration

---

## Security Considerations
- Passwords hashed with bcrypt or similar
- JWT tokens with 1-hour expiration
- Refresh tokens with 7-day expiration
- HTTPS/TLS for all communications
- Session invalidation on logout
- Audit logging for authentication events
- Rate limiting for login attempts

---

## Notes
- This unit is foundational and consumed by all other units
- All API calls to other units must include authentication tokens
- Implements JWT token-based authentication
- Does not store plain-text passwords
- **Centralized access restriction filtering is critical for security**
- All document and feature access must go through this unit's filtering
- MVP uses simple local user database (not corporate SSO)
