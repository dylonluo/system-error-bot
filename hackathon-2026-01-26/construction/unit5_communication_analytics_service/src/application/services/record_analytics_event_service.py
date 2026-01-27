from datetime import datetime
from ...domain.aggregates import AnalyticsEvent
from ...domain.value_objects import EventId, EventType, EventMetadata
from ...domain.repositories import IAnalyticsEventRepository
from ...domain.events import AnalyticsEventRecorded
from ...infrastructure.events import InMemoryEventPublisher
from ..dtos import RecordEventRequest, EventRecordedResponse


class RecordAnalyticsEventApplicationService:
    """Application service for recording analytics events."""
    
    def __init__(
        self,
        event_repository: IAnalyticsEventRepository,
        event_publisher: InMemoryEventPublisher
    ):
        self.event_repository = event_repository
        self.event_publisher = event_publisher
    
    def execute(self, request: RecordEventRequest) -> EventRecordedResponse:
        """Execute analytics event recording."""
        # 1. Validate event data
        try:
            event_type = EventType(request.event_type)
        except ValueError:
            raise ValueError(f"Invalid event type: {request.event_type}")
        
        # 2. Create AnalyticsEvent aggregate
        event_id = EventId.generate()
        metadata = EventMetadata(request.metadata)
        
        analytics_event = AnalyticsEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            metadata=metadata,
            occurred_at=datetime.now()
        )
        
        # 3. Save event
        self.event_repository.save(analytics_event)
        
        # 4. Publish domain event
        domain_event = AnalyticsEventRecorded(
            event_id=event_id,
            event_type=str(event_type.value),
            occurred_at=analytics_event.occurred_at
        )
        self.event_publisher.publish(domain_event)
        
        # 5. Return response
        return EventRecordedResponse(
            event_id=str(event_id),
            recorded=True,
            message="Analytics event recorded successfully"
        )
