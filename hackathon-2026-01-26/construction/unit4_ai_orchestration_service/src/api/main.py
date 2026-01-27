from fastapi import FastAPI
from .controllers import ai_query_router
from .middleware import setup_error_handlers

app = FastAPI(
    title="AI Orchestration Service",
    description="AI-powered query processing for NetSuite and TMS support",
    version="1.0.0",
)

setup_error_handlers(app)
app.include_router(ai_query_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-orchestration"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
