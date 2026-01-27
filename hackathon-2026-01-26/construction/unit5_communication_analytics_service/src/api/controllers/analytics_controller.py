from fastapi import APIRouter, Depends
from ...application.dtos import (
    RecordEventRequest, EventRecordedResponse,
    GetDashboardRequest, DashboardDataResponse
)
from ...application.services import (
    RecordAnalyticsEventApplicationService,
    GetDashboardDataApplicationService
)


router = APIRouter(prefix="/api/v1/communication/analytics", tags=["analytics"])


def get_record_event_service() -> RecordAnalyticsEventApplicationService:
    """Dependency injection for record event service."""
    from ...infrastructure.repositories import InMemoryAnalyticsEventRepository
    from ...infrastructure.events import InMemoryEventPublisher
    
    event_repository = InMemoryAnalyticsEventRepository()
    event_publisher = InMemoryEventPublisher()
    
    return RecordAnalyticsEventApplicationService(
        event_repository=event_repository,
        event_publisher=event_publisher
    )


def get_dashboard_service() -> GetDashboardDataApplicationService:
    """Dependency injection for dashboard service."""
    from ...infrastructure.repositories import (
        InMemoryMetricRepository,
        InMemoryAnalyticsEventRepository
    )
    from ...domain.services import DashboardDataService, MetricsCalculationService
    from ...application.clients import AccessControlClient
    
    metric_repository = InMemoryMetricRepository()
    event_repository = InMemoryAnalyticsEventRepository()
    
    dashboard_data_service = DashboardDataService(metric_repository)
    access_control_client = AccessControlClient()
    
    return GetDashboardDataApplicationService(
        dashboard_data_service=dashboard_data_service,
        access_control_client=access_control_client
    )


@router.post("/record-event", response_model=EventRecordedResponse)
async def record_event(
    request: RecordEventRequest,
    service: RecordAnalyticsEventApplicationService = Depends(get_record_event_service)
) -> EventRecordedResponse:
    """Record an analytics event."""
    return service.execute(request)


@router.post("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard(
    request: GetDashboardRequest,
    service: GetDashboardDataApplicationService = Depends(get_dashboard_service)
) -> DashboardDataResponse:
    """Get dashboard data (admin only)."""
    return service.execute(request)
