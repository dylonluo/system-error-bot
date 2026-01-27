from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from .controllers import escalation_router, analytics_router
from .middleware import (
    validation_exception_handler,
    value_error_handler,
    permission_error_handler,
    general_exception_handler
)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Communication & Analytics Service",
        description="Service for handling escalation emails and analytics",
        version="1.0.0"
    )
    
    # Register exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(PermissionError, permission_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Register routers
    app.include_router(escalation_router)
    app.include_router(analytics_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "communication-analytics"}
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
