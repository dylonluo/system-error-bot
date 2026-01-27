# Access Control Service - Unit 2

A Domain-Driven Design implementation of an authentication and authorization service for the System Support Web Application.

## Overview

This service provides:
- **Authentication**: User login with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **User Management**: Create, update, and deactivate users
- **Document Filtering**: Filter documents based on user access levels
- **Rate Limiting**: Brute force protection
- **Security**: Bcrypt password hashing, JWT tokens, session management

## Architecture

The implementation follows **Domain-Driven Design** principles with a **Simplified Layered Architecture**:

```
├── Domain Layer
│   ├── Aggregates (User, Session)
│   ├── Value Objects (UserId, Username, Password, Email, Role, AccessLevel, etc.)
│   ├── Domain Services (AuthenticationService, AuthorizationService, PasswordPolicyService)
│   ├── Repository Interfaces
│   └── Domain Events
├── Application Layer
│   ├── Application Services (LoginApplicationService, CreateUserApplicationService, etc.)
│   └── DTOs (Request/Response objects)
├── Infrastructure Layer
│   ├── Repositories (In-memory implementations)
│   ├── Security (PasswordHasher, JWTProvider, RateLimiter)
│   └── Events (InMemoryEventPublisher)
└── API Layer
    ├── Controllers (REST endpoints)
    ├── Middleware (JWT authentication, error handling)
    └── Main Application (FastAPI setup)
```

## Features

### Authentication
- Username/password login
- JWT access tokens (5 minutes expiry for demo)
- JWT refresh tokens (1 hour expiry for demo)
- Session management
- Rate limiting (5 failed attempts per 15 minutes)

### Authorization
- Two roles: `END_USER` and `ADMINISTRATOR`
- Two access levels: `BASIC` and `ALL`
- Document filtering based on access level
- Permission-based resource access

### User Management
- Create users (admin only)
- Update user information (admin only)
- Deactivate users (admin only)
- Get user information

### Security
- Bcrypt password hashing (cost factor 12)
- JWT token signing and validation
- Rate limiting for brute force protection
- Session revocation
- Audit logging via domain events

## Installation

1. **Install Python 3.9+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the service:**
   Edit `config.txt` to customize settings:
   - JWT secret key
   - Rate limiting parameters
   - Token expiration times

## Usage

### Running the Demo Script

The demo script demonstrates all features without starting the API server:

```bash
python demo.py
```

The demo will:
1. Create an initial admin user
2. Demonstrate login and token validation
3. Create an end user
4. Show document filtering for different access levels
5. Demonstrate rate limiting
6. Show user deactivation
7. Display published domain events

### Running the API Server

Start the FastAPI server:

```bash
python -m src.api.main
```

Or using uvicorn directly:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Initial Admin User

An admin user is automatically created on startup:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `administrator`
- **Access Level**: `all`

## API Endpoints

### Authentication

#### POST /api/v1/auth/login
Login with username and password.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "administrator",
    "access_level": "all",
    "is_active": true,
    "created_at": "2026-01-27T...",
    "last_login_at": "2026-01-27T..."
  }
}
```

#### POST /api/v1/auth/validate
Validate a JWT token.

**Request:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "valid": true,
  "user": { ... }
}
```

### Authorization

#### POST /api/v1/auth/filter-documents
Filter documents based on user's access level.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "documents": [
    {"id": "doc1", "title": "Public Doc", "access_level": "public"},
    {"id": "doc2", "title": "Basic Doc", "access_level": "basic"},
    {"id": "doc3", "title": "Advanced Doc", "access_level": "advanced"}
  ]
}
```

**Response:**
```json
{
  "filtered_documents": [ ... ],
  "removed_count": 1,
  "total_count": 3
}
```

### User Management

#### POST /api/v1/auth/users
Create a new user (admin only).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "end_user"
}
```

#### GET /api/v1/auth/users/{user_id}
Get user information.

#### PUT /api/v1/auth/users/{user_id}
Update user information (admin only).

#### DELETE /api/v1/auth/users/{user_id}
Deactivate user (admin only).

## Configuration

Edit `config.txt` to customize:

```ini
# JWT Secret Key
jwt_secret=your-secret-key-here

# Rate Limiting
max_failed_attempts=5
rate_limit_window_minutes=15

# Token Expiration (seconds)
access_token_expiry_seconds=300
refresh_token_expiry_seconds=3600
```

## Domain Model

### Aggregates

**User (Aggregate Root)**
- Identity: UserId (UUID)
- Attributes: username, password (hashed), email, role, access_level, is_active
- Behaviors: authenticate, login, logout, change_password, has_permission, can_access_document

**Session (Entity)**
- Identity: SessionId (UUID)
- Attributes: access_token, refresh_token, created_at, expires_at, last_activity_at
- Behaviors: is_valid, is_expired, refresh, revoke, update_activity

### Value Objects

- **UserId**: UUID wrapper
- **Username**: 3-50 chars, alphanumeric + underscore
- **Password**: Bcrypt hashed value
- **Email**: RFC 5322 compliant
- **Role**: END_USER or ADMINISTRATOR
- **AccessLevel**: BASIC or ALL
- **Permission**: resource + action pair
- **SessionId**: UUID wrapper
- **JWTToken**: JWT string with expiration

### Domain Events

- UserAuthenticated
- UserAuthenticationFailed
- SessionCreated
- SessionExpired
- SessionRevoked
- UserCreated
- UserDeactivated

## Business Rules

### Authentication Rules
1. Maximum 5 failed login attempts per 15 minutes
2. Passwords must be at least 8 characters with letter and number
3. Tokens validated on every request
4. Inactive users cannot login

### Authorization Rules
1. BASIC access: public and basic documents only
2. ALL access: all documents
3. Administrators can access all resources
4. Users can only access their own data (except admins)

### Session Rules
1. Access tokens expire after configured time (default 5 minutes)
2. Refresh tokens expire after configured time (default 1 hour)
3. Expired sessions cannot be refreshed
4. Revoked sessions cannot be reactivated
5. All sessions revoked when user is deactivated

## Testing

Run the demo script to test all functionality:

```bash
python demo.py
```

The demo covers:
- User creation
- Authentication
- Token validation
- Document filtering
- Rate limiting
- User deactivation
- Event publishing

## Security Considerations

1. **Passwords**: Never stored in plain text, always bcrypt hashed
2. **Tokens**: Short-lived access tokens, longer refresh tokens
3. **Rate Limiting**: Prevents brute force attacks
4. **Session Management**: Tracks activity, supports revocation
5. **Audit Logging**: All security events published as domain events

## Future Enhancements

- Multi-factor authentication (MFA)
- OAuth 2.0 / SSO integration
- Fine-grained permissions
- Password reset functionality
- Session management UI
- Persistent storage (PostgreSQL)
- Redis for caching and rate limiting

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please contact the development team.
