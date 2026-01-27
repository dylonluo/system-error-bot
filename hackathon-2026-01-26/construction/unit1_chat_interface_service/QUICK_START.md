# 🏰 Castlery AI Support - Quick Start

## 🚀 Run in 3 Steps

```bash
# 1. Navigate to project
cd hackathon-2026-01-26/construction/unit1_chat_interface_service

# 2. Install dependencies
pip install -e .

# 3. Run the service with UI
python run.py
```

## 🌐 Open the UI

Navigate to **http://localhost:8000** in your browser.

You'll see a beautiful chat interface where you can:
- 💬 Chat with the AI assistant
- 📎 Attach screenshots (JPEG/PNG, max 5MB)
- 📚 Get documentation links
- 👍 Provide feedback
- 🎫 Escalate to human support

## 📋 API Demo (Optional)

To run the API demo script:

```bash
python demo.py
```

## 🔍 API Documentation

While the service is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🛠️ Manual API Testing

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

## 📖 More Information

- **Full Documentation:** README.md
- **Setup Guide:** SETUP.md
- **Implementation Details:** IMPLEMENTATION_SUMMARY.md
- **Test Plan:** test_plan.md

---

**Ready to go?** Run `python run.py` and open http://localhost:8000 🎉
