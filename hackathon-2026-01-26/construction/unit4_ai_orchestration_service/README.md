# Unit 4: AI Orchestration Service

AI-powered query processing for NetSuite and TMS support.

## Quick Start

```bash
cd hackathon-2026-01-26/construction/unit4_ai_orchestration_service

# Install dependencies
pip install -r requirements.txt

# Run demo
python demo.py
```

## Architecture

Hexagonal architecture with:
- **Domain Layer**: Business logic (aggregates, services, value objects)
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: Mock AI provider, in-memory storage
- **API Layer**: FastAPI REST endpoints

## Key Features

- Intent detection (error troubleshooting, task guidance, general questions)
- Off-topic query rejection (no AI calls wasted)
- Confidence scoring with escalation logic
- Documentation link retrieval

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/ai/process-query | Process a user query |
| POST | /api/v1/ai/detect-intent | Detect intent only |
| GET | /api/v1/ai/queries/{id} | Get query details |

## Run API Server

```bash
uvicorn src.api.main:app --reload --port 8003
```
