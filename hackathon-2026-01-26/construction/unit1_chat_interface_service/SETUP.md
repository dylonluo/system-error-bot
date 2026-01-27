# Quick Setup Guide

## Prerequisites

- Python 3.13 installed
- pip package manager

## Installation Steps

### 1. Check Python Version

```bash
python3 --version
# Should show Python 3.13.x
```

If you don't have Python 3.13, install it:

**macOS (with Homebrew):**
```bash
brew install python@3.13
```

**macOS (without Homebrew):**
Download from [python.org](https://www.python.org/downloads/)

### 2. Navigate to Project Directory

```bash
cd /Users/dylonluo/system-error-bot/hackathon-2026-01-26/construction/unit1_chat_interface_service
```

### 3. Install Dependencies

**Option A: Using pyproject.toml (Recommended)**
```bash
python3 -m pip install -e .
```

**Option B: Using requirements.txt**
```bash
python3 -m pip install -r requirements.txt
```

**Option C: With development tools**
```bash
python3 -m pip install -e ".[dev]"
```

### 4. Run the Demo

```bash
python3 demo.py
```

## What the Demo Does

The demo script will:
1. ✅ Start FastAPI server on port 8000
2. ✅ Create a conversation implicitly on first message
3. ✅ Submit multiple messages
4. ✅ Submit feedback on AI responses
5. ✅ List and retrieve conversations
6. ✅ Escalate conversation to human support
7. ✅ Verify domain invariants (e.g., can't add messages to escalated conversations)

## Troubleshooting

### Port 8000 Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Module Not Found Errors

Make sure you're in the correct directory:
```bash
pwd
# Should show: /Users/dylonluo/system-error-bot/hackathon-2026-01-26/construction/unit1_chat_interface_service
```

### Python Version Issues

If `python3` points to an older version:
```bash
# Use explicit version
python3.13 -m pip install -e .
python3.13 demo.py
```

## Manual Testing

Once the server is running, you can test endpoints manually:

### Health Check
```bash
curl http://localhost:8000/health
```

### Submit First Message
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations/new/messages" \
  -H "Authorization: Bearer demo-token" \
  -F "query_text=How do I create an S3 bucket?"
```

### API Documentation
Visit: http://localhost:8000/docs

## Project Structure

```
src/
├── domain/           # Business logic (aggregates, entities, value objects)
├── application/      # Use cases and orchestration
├── infrastructure/   # Technical implementations (in-memory storage)
└── api/             # REST endpoints (FastAPI controllers)
```

## Next Steps

After running the demo successfully:
1. Explore the code structure
2. Review domain model in `src/domain/`
3. Check API documentation at http://localhost:8000/docs
4. Modify and extend as needed

## Support

For issues or questions, refer to:
- README.md - Full documentation
- plan.md - Implementation plan
- Domain model: `hackathon-2026-01-26/construction/unit1_chat_interface_service/domain_model.md`
- Logical design: `hackathon-2026-01-26/construction/unit1_chat_interface_service/logical_design.md`
