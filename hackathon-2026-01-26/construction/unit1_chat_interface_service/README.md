# Chat Interface Service - Unit 1

## Overview

This is a Python implementation of the Chat Interface Service (Unit 1) following Domain-Driven Design principles with a simplified layered architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  (FastAPI Controllers, Request/Response DTOs)            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Application Service Layer                 │
│  (Use Case Orchestration, External Clients)              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Domain Layer                           │
│  (Aggregates, Entities, Value Objects, Domain Services)  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                      │
│  (In-Memory Repositories, Storage, Event Publisher)      │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
src/
├── domain/                    # Core business logic
│   ├── aggregates/           # Conversation, Message
│   ├── value_objects/        # ConversationId, MessageId, etc.
│   ├── services/             # Domain services
│   ├── events/               # Domain events
│   └── repositories/         # Repository interfaces
├── infrastructure/           # Technical implementations
│   ├── repositories/         # In-memory repository
│   ├── storage/              # In-memory screenshot storage
│   └── events/               # In-memory event publisher
├── application/              # Use case orchestration
│   ├── services/             # Application services
│   ├── dtos/                 # Request/Response DTOs
│   └── clients/              # Mock external service clients
└── api/                      # REST API
    ├── controllers/          # FastAPI controllers
    ├── middleware/           # Error handling
    └── main.py               # FastAPI app entry point
```

## Setup

### Prerequisites

- Python 3.13 or higher
- pip

### Installation

1. Navigate to the project directory:
```bash
cd hackathon-2026-01-26/construction/unit1_chat_interface_service
```

2. Install dependencies (choose one method):

**Method A: Using pyproject.toml (Recommended)**
```bash
pip install -e .
```

**Method B: Using requirements.txt**
```bash
pip install -r requirements.txt
```

**Method C: Install with dev dependencies**
```bash
pip install -e ".[dev]"
```

## Running the Demo

The demo script starts the FastAPI server and runs through a complete workflow:

```bash
python demo.py
```

The demo will:
1. Check server health
2. Submit first message (creates conversation implicitly)
3. List conversations
4. Get conversation details
5. Submit follow-up message
6. Submit feedback on assistant response
7. Get updated conversation
8. Escalate conversation to human support
9. Try to add message to escalated conversation (should fail)
10. Show final conversation list

## Running the Server Manually

To run the server manually:

```bash
python -m src.api.main
```

Or using uvicorn directly:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Conversations

- `GET /api/v1/chat/conversations` - List user's conversations
- `GET /api/v1/chat/conversations/{id}` - Get conversation details
- `POST /api/v1/chat/conversations/{id}/escalate` - Escalate conversation

### Messages

- `POST /api/v1/chat/conversations/{id}/messages` - Submit message
  - Use `conversation_id="new"` for first message (creates conversation implicitly)
- `POST /api/v1/chat/conversations/{id}/feedback` - Submit feedback

### Health

- `GET /health` - Health check

## Authentication

All endpoints (except `/health`) require an `Authorization` header:

```
Authorization: Bearer <token>
```

For the demo, any token is accepted and returns a mock user.

## Testing with cURL

### Submit first message (create conversation):
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations/new/messages" \
  -H "Authorization: Bearer demo-token" \
  -F "query_text=How do I create an S3 bucket?"
```

### List conversations:
```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer demo-token"
```

### Get conversation:
```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations/{conversation_id}" \
  -H "Authorization: Bearer demo-token"
```

### Submit feedback:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations/{conversation_id}/feedback" \
  -H "Authorization: Bearer demo-token" \
  -H "Content-Type: application/json" \
  -d '{"message_id": "{message_id}", "answered_question": true, "problem_solved": true}'
```

### Escalate conversation:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations/{conversation_id}/escalate" \
  -H "Authorization: Bearer demo-token" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Need more help"}'
```

## Domain Model Highlights

### Aggregates
- **Conversation** (Aggregate Root) - Manages conversation lifecycle and messages
- **Message** (Entity) - Individual messages within a conversation

### Value Objects
- ConversationId, MessageId - Identity wrappers
- ConversationStatus - ACTIVE, RESOLVED, ESCALATED
- MessageRole - USER, ASSISTANT
- Screenshot - Metadata reference to uploaded files
- Feedback - User feedback on assistant responses
- DocumentationLink - Links to relevant documentation

### Domain Events
- ConversationCreated
- MessageAdded
- FeedbackSubmitted
- ConversationResolved
- ConversationEscalated

### Business Rules Enforced
- Conversations created implicitly on first message
- Messages ordered by timestamp
- Only assistant messages can have documentation links
- Only user messages can have screenshots
- Feedback can only be submitted once per message
- Cannot add messages to escalated conversations
- Users can only access their own conversations

## Implementation Notes

- **In-Memory Storage**: All data stored in memory (no database)
- **Mock External Services**: AI, Access Control, and Analytics clients are mocked
- **Event Publishing**: Events collected in memory for inspection
- **Screenshot Storage**: Screenshots stored as base64 strings in memory
- **Simple Authentication**: Any token accepted, returns fixed mock user

## Next Steps

For production deployment:
1. Replace in-memory repository with PostgreSQL
2. Implement real external service clients
3. Add proper JWT token validation
4. Implement file storage (S3)
5. Add message queue for event publishing
6. Add comprehensive error handling
7. Add logging and monitoring
8. Add unit and integration tests
9. Add rate limiting
10. Add API versioning

## License

Internal use only - Hackathon 2026-01-26
