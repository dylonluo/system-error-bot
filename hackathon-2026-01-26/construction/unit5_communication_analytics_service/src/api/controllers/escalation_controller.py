from fastapi import APIRouter, Depends
from ...application.dtos import SendEscalationEmailRequest, EscalationEmailResponse
from ...application.services import SendEscalationEmailApplicationService


router = APIRouter(prefix="/api/v1/communication", tags=["escalation"])


def get_email_provider():
    """Get email provider - tries SES first, falls back to mock."""
    from ...infrastructure.email import SESEmailProvider, MockEmailProvider
    
    # Try SES first
    ses_provider = SESEmailProvider(region="ap-southeast-1")
    if ses_provider.is_available():
        print("[Escalation] Using AWS SES for email delivery")
        return ses_provider
    
    # Fallback to mock
    print("[Escalation] SES not available, using mock email provider")
    return MockEmailProvider()


def get_escalation_service() -> SendEscalationEmailApplicationService:
    """Dependency injection for escalation service."""
    from ...infrastructure.repositories import (
        InMemoryEscalationEmailRepository
    )
    from ...infrastructure.events import InMemoryEventPublisher
    from ...application.clients import AccessControlClient, ChatInterfaceClient
    from ...domain.services import EmailCompositionService
    
    # Create dependencies (in real app, use DI container)
    email_repository = InMemoryEscalationEmailRepository()
    email_provider = get_email_provider()
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
