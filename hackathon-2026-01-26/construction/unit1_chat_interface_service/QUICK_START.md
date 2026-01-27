# Quick Start - Chat Interface Service

## 🚀 Run in 3 Steps

```bash
# 1. Navigate to project
cd /Users/dylonluo/system-error-bot/hackathon-2026-01-26/construction/unit1_chat_interface_service

# 2. Install dependencies
python3 -m pip install -e .

# 3. Run demo
python3 demo.py
```

## 📋 What You'll See

```
================================================================================
  Chat Interface Service - Demo
  Unit 1: Chat Interface Context
================================================================================

Waiting for server to start...

================================================================================
  1. Health Check
================================================================================

Status: 200
Response:
{
  "status": "healthy",
  "service": "chat-interface-service"
}

================================================================================
  2. Submit First Message (Create Conversation Implicitly)
================================================================================

Status: 200
Response:
{
  "message_id": "...",
  "conversation_id": "...",
  "role": "assistant",
  "content": "Based on your query...",
  "documentation_links": [...]
}

... and 8 more steps demonstrating the complete workflow
```

## 🎯 Key Features Demonstrated

- ✅ Implicit conversation creation
- ✅ Message submission with AI responses
- ✅ Feedback collection
- ✅ Conversation listing and retrieval
- ✅ Escalation to human support
- ✅ Domain invariant enforcement

## 🔍 Explore the API

While demo is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📖 More Information

- **Full Documentation:** README.md
- **Setup Guide:** SETUP.md
- **Implementation Details:** IMPLEMENTATION_SUMMARY.md
- **Project Plan:** plan.md

## 🛠️ Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Submit message
curl -X POST "http://localhost:8000/api/v1/chat/conversations/new/messages" \
  -H "Authorization: Bearer demo-token" \
  -F "query_text=How do I use S3?"

# List conversations
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer demo-token"
```

## 🐛 Troubleshooting

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill -9
```

**Module not found?**
```bash
# Make sure you're in the right directory
pwd
# Should show: .../unit1_chat_interface_service
```

**Python version?**
```bash
python3 --version
# Should be 3.13 or higher (3.9+ will work)
```

## 🎓 Learning Path

1. Run the demo ✅
2. Read IMPLEMENTATION_SUMMARY.md
3. Explore `src/domain/` - business logic
4. Check `src/application/` - use cases
5. Review `src/api/` - REST endpoints
6. Modify and experiment!

---

**Ready to go? Run:** `python3 demo.py`
