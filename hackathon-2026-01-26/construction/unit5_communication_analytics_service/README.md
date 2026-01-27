# Unit 5: Communication & Analytics Service

## Overview
This service handles email escalations to human support and tracks system usage analytics following Domain-Driven Design principles.

## Architecture
- **Style**: Simplified Layered Architecture
- **Technology**: Python with FastAPI
- **Storage**: In-memory repositories (for demo purposes)

## Features
- Send escalation emails to support team
- Record analytics events from other services
- Calculate usage metrics (daily batch processing)
- Provide dashboard data for administrators

## Project Structure
```
src/
├── api/                    # API Layer (Controllers, Middleware)
├── application/            # Application Layer (Services, DTOs, Clients)
├── domain/                 # Domain Layer (Aggregates, Entities, Value Objects, Services)
└── infrastructure/         # Infrastructure Layer (Repositories, Email Provider, Events)
```

## Running the Demo
```bash
python demo.py
```

## Dependencies
- FastAPI: Web framework
- Pydantic: Data validation
- python-dateutil: Date/time utilities

## Key Domain Concepts

### Aggregates
- **EscalationEmail**: Represents an email sent to support
- **AnalyticsEvent**: Represents a recorded system event
- **Metric**: Represents calculated analytics metrics

### Business Rules
- Maximum 3 retry attempts for failed emails
- Events are immutable (append-only)
- Metrics calculated daily at midnight
- Dashboard accessible to administrators only
- Rate limit: 10 escalation emails per hour per user

## API Endpoints
- `POST /api/v1/communication/send-escalation-email` - Send escalation email
- `POST /api/v1/communication/analytics/record-event` - Record analytics event
- `GET /api/v1/communication/analytics/dashboard` - Get dashboard data (admin only)
