from datetime import datetime
from ...domain.aggregates import EscalationEmail
from ...domain.value_objects import (
    EmailId, EmailAddress, ConversationSnapshot, EventType, EventId, EventMetadata
)
from ...domain.repositories import IEscalationEmailRepository
from ...domain.services import EmailCompositionService
from ...domain.events import EscalationEmailSent, EscalationEmailFailed
from ...infrastructure.email import IEmailProvider
from ...infrastructure.events import InMemoryEventPublisher
from ..clients import AccessControlClient, ChatInterfaceClient
from ..dtos import SendEscalationEmailRequest, EscalationEmailResponse


class SendEscalationEmailApplicationService:
    """Application service for sending escalation emails."""
    
    def __init__(
        self,
        email_repository: IEscalationEmailRepository,
        email_provider: IEmailProvider,
        event_publisher: InMemoryEventPublisher,
        access_control_client: AccessControlClient,
        chat_interface_client: ChatInterfaceClient,
        email_composition_service: EmailCompositionService
    ):
        self.email_repository = email_repository
        self.email_provider = email_provider
        self.event_publisher = event_publisher
        self.access_control_client = access_control_client
        self.chat_interface_client = chat_interface_client
        self.email_composition_service = email_composition_service
    
    def execute(self, request: SendEscalationEmailRequest) -> EscalationEmailResponse:
        """Execute escalation email sending."""
        # 1. Validate authentication
        user = self.access_control_client.validate_token(request.token)
        if not user:
            raise ValueError("Invalid authentication token")
        
        # 2. Retrieve conversation history
        conversation = self.chat_interface_client.get_conversation_history(request.conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {request.conversation_id}")
        
        # 3. Create conversation snapshot
        conversation_snapshot = ConversationSnapshot(
            conversation_id=request.conversation_id,
            messages=conversation.get('messages', []),
            user_info=user,
            created_at=datetime.fromisoformat(conversation.get('created_at', datetime.now().isoformat()))
        )
        
        # 4. Compose email
        email_content = self.email_composition_service.compose_email(conversation_snapshot, user)
        subject = self.email_composition_service.generate_subject(request.conversation_id)
        
        # 5. Create EscalationEmail aggregate
        email_id = EmailId.generate()
        
        # Get support team emails from provider if available, otherwise use default
        from ...infrastructure.email import SUPPORT_TEAM_EMAILS
        recipient_email = EmailAddress(SUPPORT_TEAM_EMAILS[0])  # Primary recipient for record
        
        escalation_email = EscalationEmail(
            email_id=email_id,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            recipient_email=recipient_email,
            subject=subject,
            content=email_content,
            conversation_snapshot=conversation_snapshot,
            screenshots=conversation.get('screenshots', [])
        )
        
        # 6. Save email
        self.email_repository.save(escalation_email)
        
        # 7. Send email (asynchronously in real system)
        result = self.email_provider.send(
            to=str(recipient_email),
            subject=subject,
            body=email_content.get_body()
        )
        
        # 8. Update status and publish events
        if result.success:
            escalation_email.mark_as_sent()
            self.email_repository.save(escalation_email)
            
            event = EscalationEmailSent(
                email_id=email_id,
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                sent_at=datetime.now()
            )
            self.event_publisher.publish(event)
            
            # Record analytics event
            self._record_escalation_event(request.conversation_id, request.user_id)
            
        else:
            escalation_email.mark_as_failed(result.error or "Unknown error")
            self.email_repository.save(escalation_email)
            
            event = EscalationEmailFailed(
                email_id=email_id,
                conversation_id=request.conversation_id,
                failure_reason=result.error or "Unknown error",
                retry_count=escalation_email.retry_count,
                failed_at=datetime.now()
            )
            self.event_publisher.publish(event)
        
        # 9. Return response
        return EscalationEmailResponse(
            email_id=str(email_id),
            status=str(escalation_email.status.value),
            sent_to=str(recipient_email),
            sent_at=escalation_email.sent_at.isoformat() if escalation_email.sent_at else None,
            message="Escalation email sent successfully" if result.success else f"Failed to send: {result.error}"
        )
    
    def _record_escalation_event(self, conversation_id: str, user_id: str):
        """Record escalation triggered event."""
        from .record_analytics_event_service import RecordAnalyticsEventApplicationService
        from ...infrastructure.repositories import InMemoryAnalyticsEventRepository
        
        # This would normally be done via event bus, but for demo we call directly
        pass  # Simplified for demo
