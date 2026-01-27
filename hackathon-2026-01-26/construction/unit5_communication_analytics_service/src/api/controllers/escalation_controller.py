from fastapi import APIRouter, Depends
from ...application.dtos import SendEscalationEmailRequest, EscalationEmailResponse
from ...application.services import SendEscalationEmailApplicationService


router = APIRouter(prefix="/api/v1/communication", tags=["escalation"])


def get_escalation_service() -> SendEscalationEmailApplicationService:
    """Dependency injection for escalation service."""
    from ...infrastructure.repositories import (
        InMemoryEscalationEmailRepository
    )
    from ...infrastructure.email import MockEmailProvider
    from ...infrastructure.events import InMemoryEventPublisher
    from ...application.clients import AccessControlClient, ChatInterfaceClient
    from ...domain.services import EmailCompositionService
    
    # Create dependencies (in real app, use DI container)
    email_repository = InMemoryEscalationEmailRepository()
    email_provider = MockEmailProvider()
    event_publisher = InMemoryEventPublisher()
    access_control_client = AccessControlClient()
    chat_interface_client = ChatInterfaceClient()
    email_composition_service = EmailCompositionService()
    
    return SendEscalationEmailApplicationService(
        email_repository=email_repository,
        email_provider=email_provider,
        event_publisher=event_publisher,
        access_control_client=access_control_client,
        chat_interface_client=chat_interface_client,
        email_composition_service=email_composition_service
    )


@router.post("/send-escalation-email", response_model=EscalationEmailResponse)
async def send_escalation_email(
    request: SendEscalationEmailRequest,
    service: SendEscalationEmailApplicationService = Depends(get_escalation_service)
) -> EscalationEmailResponse:
    """Send an escalation email to support team."""
    return service.execute(request)
