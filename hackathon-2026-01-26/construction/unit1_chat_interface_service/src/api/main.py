"""FastAPI application entry point"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .controllers import conversation_controller, message_controller
from .middleware.error_handler import error_handler_middleware
from ..domain.services.screenshot_validation_service import ScreenshotValidationService
from ..domain.services.conversation_history_service import ConversationHistoryService
from ..infrastructure.repositories.in_memory_conversation_repository import InMemoryConversationRepository
from ..infrastructure.storage.in_memory_screenshot_storage import InMemoryScreenshotStorage
from ..infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from ..application.clients.access_control_client import AccessControlClient
from ..application.clients.ai_orchestration_client import AIOrchestrationClient
from ..application.clients.communication_analytics_client import CommunicationAnalyticsClient
from ..application.services.submit_query_service import SubmitQueryApplicationService
from ..application.services.submit_feedback_service import SubmitFeedbackApplicationService
from ..application.services.escalate_conversation_service import EscalateConversationApplicationService
from ..application.services.get_conversation_service import GetConversationApplicationService
from ..application.services.list_conversations_service import ListConversationsApplicationService


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Chat Interface Service",
        description="Unit 1 - Chat Interface Context API",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For demo purposes
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add error handler middleware
    app.middleware("http")(error_handler_middleware)

    # Initialize infrastructure
    repository = InMemoryConversationRepository()
    screenshot_storage = InMemoryScreenshotStorage()
    event_publisher = InMemoryEventPublisher()

    # Initialize clients
    access_control_client = AccessControlClient()
    ai_client = AIOrchestrationClient()
    analytics_client = CommunicationAnalyticsClient()

    # Initialize domain services
    screenshot_validation_service = ScreenshotValidationService()
    conversation_history_service = ConversationHistoryService(repository)

    # Initialize application services
    submit_query_service = SubmitQueryApplicationService(
        repository=repository,
        screenshot_storage=screenshot_storage,
        event_publisher=event_publisher,
        access_control_client=access_control_client,
        ai_client=ai_client,
        analytics_client=analytics_client,
        screenshot_validation_service=screenshot_validation_service
    )

    submit_feedback_service = SubmitFeedbackApplicationService(
        repository=repository,
        event_publisher=event_publisher,
        access_control_client=access_control_client,
        analytics_client=analytics_client
    )

    escalate_service = EscalateConversationApplicationService(
        repository=repository,
        event_publisher=event_publisher,
        access_control_client=access_control_client,
        analytics_client=analytics_client
    )

    get_service = GetConversationApplicationService(
        repository=repository,
        access_control_client=access_control_client
    )

    list_service = ListConversationsApplicationService(
        repository=repository,
        access_control_client=access_control_client
    )

    # Initialize controllers
    conversation_controller.init_conversation_controller(
        list_service=list_service,
        get_service=get_service,
        escalate_service=escalate_service
    )

    message_controller.init_message_controller(
        submit_query_service=submit_query_service,
        submit_feedback_service=submit_feedback_service
    )

    # Register routers
    app.include_router(conversation_controller.router)
    app.include_router(message_controller.router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "chat-interface-service"}

    # Serve frontend
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        
        @app.get("/")
        async def serve_frontend():
            return FileResponse(str(frontend_path / "index.html"))

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
