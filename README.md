# System Error Bot

An AI-powered system support web application that helps users troubleshoot system errors and get task guidance with links to relevant documentation.

## Overview

System Error Bot is a conversational AI assistant designed to help users resolve system issues related to NetSuite and Transport Management System integrations. Users can describe their problems, upload screenshots, and receive AI-generated responses with links to relevant SOPs and documentation.

## Key Features

- **AI-Powered Troubleshooting**: Submit queries about system errors and receive intelligent responses
- **Screenshot Support**: Upload screenshots to help diagnose issues
- **Documentation Links**: Get relevant links to SOPs, PRDs, and system documentation from S3, Confluence, and ClickUp
- **Conversation History**: Save and review past conversations
- **Feedback System**: Rate responses and confirm if solutions resolved your issue
- **Human Escalation**: Escalate to human support via email when AI cannot help
- **Analytics Dashboard**: Track common issues and query patterns

## Architecture

The application follows Domain-Driven Design (DDD) principles with five bounded contexts:

| Service | Description |
|---------|-------------|
| **Chat Interface Service** | Manages conversations, messages, and user feedback |
| **Access Control Service** | Handles authentication, authorization, and sessions |
| **Document Repository Service** | Searches and retrieves documents from S3/Confluence |
| **AI Orchestration Service** | Processes queries and generates AI responses |
| **Communication & Analytics Service** | Sends escalation emails and tracks analytics |

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

### Running the Chat Interface Service

```bash
cd hackathon-2026-01-26/construction/unit1_chat_interface_service
uv run python demo.py
```

The demo will start a FastAPI server and run through all API endpoints.

## API Endpoints (Chat Interface Service)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/chat/conversations/new/messages` | Create conversation with first message |
| GET | `/api/v1/chat/conversations` | List user conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation details |
| POST | `/api/v1/chat/conversations/{id}/messages` | Add message to conversation |
| POST | `/api/v1/chat/conversations/{id}/feedback` | Submit feedback |
| POST | `/api/v1/chat/conversations/{id}/escalate` | Escalate to human support |

## User Roles

- **End User**: Basic access to public and basic-level documents
- **Administrator**: Full access to all documents and admin features

## License

Proprietary - AWS Hackathon 2026
