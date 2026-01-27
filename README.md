# System Error Bot

An AI-powered system support web application that helps users troubleshoot system errors and get task guidance with links to relevant documentation.

## Overview

System Error Bot is a conversational AI assistant designed to help users resolve system issues related to NetSuite and Transport Management System integrations. Users can describe their problems, upload screenshots, and receive AI-generated responses with links to relevant SOPs and documentation.

## Key Features

### Unit 1: Chat Interface
- **AI-Powered Troubleshooting**: Submit queries about system errors and receive intelligent responses
- **Screenshot Support**: Upload screenshots to help diagnose issues
- **Conversation History**: Save and review past conversations
- **Feedback System**: Rate responses and confirm if solutions resolved your issue
- **Human Escalation**: Escalate to human support via email when AI cannot help

### Unit 2: Access Control
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: End User and Administrator roles
- **Session Management**: 1-hour access tokens, 7-day refresh tokens
- **Password Security**: Bcrypt hashing with salt

### Unit 3: Document Repository
- **Multi-Source Search**: Search across S3 and Confluence (MVP: S3 focus)
- **Relevance Ranking**: Intelligent scoring (60% keyword, 20% recency, 20% popularity)
- **Access Control**: 3-level filtering (PUBLIC, BASIC, ADVANCED)
- **Performance**: 5-minute caching, < 10ms response times
- **Sample Data**: 5 pre-loaded documents for testing

### Unit 4: AI Orchestration
- **Intent Detection**: Automatically classify query types
- **Context Management**: Use conversation history for better responses
- **Confidence Scoring**: Measure AI response confidence
- **Off-Topic Handling**: Politely reject non-system queries

### Unit 5: Communication & Analytics
- **Email Escalation**: Automated email to support team
- **Event Tracking**: Record all system events
- **Metrics Dashboard**: Track usage patterns and resolution rates
- **Analytics**: 30-day rolling metrics

## Architecture

The application follows Domain-Driven Design (DDD) principles with Hexagonal Architecture. Five bounded contexts work together:

| Service | Status | Description |
|---------|--------|-------------|
| **Unit 1: Chat Interface Service** | ✅ Complete | Manages conversations, messages, and user feedback |
| **Unit 2: Access Control Service** | ✅ Complete | Handles authentication, authorization, and sessions |
| **Unit 3: Document Repository Service** | ✅ Complete | Searches and retrieves documents from S3/Confluence with relevance ranking |
| **Unit 4: AI Orchestration Service** | ✅ Complete | Processes queries and generates AI responses |
| **Unit 5: Communication & Analytics Service** | ✅ Complete | Sends escalation emails and tracks analytics |

## Project Structure

```
hackathon-2026-01-26/
├── inception/              # Requirements and user stories
│   ├── units/              # Service unit specifications
│   ├── user_stories.md     # Complete user stories
│   └── user_stories_mvp.md # MVP scope user stories
├── architecture/           # Architecture diagrams (PlantUML)
├── construction/           # Implementation
│   ├── unit1_chat_interface_service/    # Chat service implementation
│   ├── unit2_access_control_service/    # Auth service
│   ├── unit3_document_repository_service/
│   ├── unit4_ai_orchestration_service/
│   ├── unit5_communication_analytics_service/
│   └── *.md                # Domain models and design docs
├── examples/               # Integration examples
└── plan.md                 # Project plan
```

## Tech Stack

- **Backend**: Python, FastAPI
- **AI**: AWS Bedrock
- **Database**: PostgreSQL (schema-per-service)
- **Authentication**: JWT-based
- **Document Sources**: S3, Confluence, ClickUp

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
cd hackathon-2026-01-26/construction
uv sync
```

### Running Individual Services

#### Unit 1: Chat Interface Service
```bash
cd hackathon-2026-01-26/construction/unit1_chat_interface_service
python demo.py
```

#### Unit 2: Access Control Service
```bash
cd hackathon-2026-01-26/construction/unit2_access_control_service
python demo.py
```

#### Unit 3: Document Repository Service
```bash
cd hackathon-2026-01-26/construction/unit3_document_repository_service
python demo.py
```

#### Unit 4: AI Orchestration Service
```bash
cd hackathon-2026-01-26/construction/unit4_ai_orchestration_service
python demo.py
```

#### Unit 5: Communication & Analytics Service
```bash
cd hackathon-2026-01-26/construction/unit5_communication_analytics_service
python demo.py
```

Each demo script will demonstrate the service's functionality with pre-loaded sample data.

## API Endpoints

### Unit 1: Chat Interface Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/chat/conversations/new/messages` | Create conversation with first message |
| GET | `/api/v1/chat/conversations` | List user conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation details |
| POST | `/api/v1/chat/conversations/{id}/messages` | Add message to conversation |
| POST | `/api/v1/chat/conversations/{id}/feedback` | Submit feedback |
| POST | `/api/v1/chat/conversations/{id}/escalate` | Escalate to human support |

### Unit 2: Access Control Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/validate` | Validate token |
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users/{id}` | Get user details |
| PUT | `/api/v1/users/{id}` | Update user |

### Unit 3: Document Repository Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/documents/search` | Search documents with filters |
| GET | `/api/v1/documents/{id}` | Get document by ID |
| GET | `/api/v1/documents/{id}/metadata` | Get document metadata |

**Search Parameters:**
- `query` (required): Search query text
- `sources`: Filter by sources (s3, confluence)
- `document_types`: Filter by types (sop, prd, guide, other)
- `formats`: Filter by formats (webpage, pdf, markdown)
- `access_levels`: Filter by access (public, basic, advanced)
- `limit`: Maximum results (default: 50, max: 100)

**Features:**
- Relevance ranking (60% keyword, 20% recency, 20% popularity)
- Access level filtering (PUBLIC, BASIC, ADVANCED)
- 5-minute search result caching
- Pre-loaded with 5 sample documents

### Unit 4: AI Orchestration Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/ai/query` | Process AI query |
| GET | `/api/v1/ai/query/{id}` | Get query details |

### Unit 5: Communication & Analytics Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/escalations` | Send escalation email |
| POST | `/api/v1/analytics/events` | Record analytics event |
| GET | `/api/v1/analytics/metrics` | Get metrics |

## User Roles

- **End User**: Basic access to public and basic-level documents
- **Administrator**: Full access to all documents including advanced-level content

### Access Levels (Unit 3)

| Level | End User | Administrator |
|-------|----------|---------------|
| PUBLIC | ✅ | ✅ |
| BASIC | ✅ | ✅ |
| ADVANCED | ❌ | ✅ |

### Sample Documents (Unit 3)

The Document Repository Service includes 5 pre-loaded sample documents:

1. **NetSuite Error Troubleshooting Guide** (BASIC)
   - Type: GUIDE
   - Tags: netsuite, troubleshooting, errors
   
2. **TMS Integration SOP** (ADVANCED)
   - Type: SOP
   - Tags: tms, integration, sop
   
3. **NetSuite API Integration Guide** (BASIC)
   - Type: GUIDE
   - Tags: netsuite, api, integration
   
4. **TMS User Manual** (PUBLIC)
   - Type: GUIDE
   - Tags: tms, user-manual, guide
   
5. **System Architecture PRD** (ADVANCED)
   - Type: PRD
   - Tags: architecture, prd, technical

## License

Proprietary - AWS Hackathon 2026
