from ...domain.value_objects import TimePeriod
from ...domain.services import DashboardDataService
from ..clients import AccessControlClient
from ..dtos import GetDashboardRequest, DashboardDataResponse


class GetDashboardDataApplicationService:
    """Application service for retrieving dashboard data."""
    
    def __init__(
        self,
        dashboard_data_service: DashboardDataService,
        access_control_client: AccessControlClient
    ):
        self.dashboard_data_service = dashboard_data_service
        self.access_control_client = access_control_client
    
    def execute(self, request: GetDashboardRequest) -> DashboardDataResponse:
        """Execute dashboard data retrieval."""
        # 1. Validate authentication
        user = self.access_control_client.validate_token(request.token)
        if not user:
            raise ValueError("Invalid authentication token")
        
        # 2. Verify user is administrator
        if not self.access_control_client.is_admin(user):
            raise PermissionError("Only administrators can access dashboard data")
        
        # 3. Get dashboard data
        time_period = TimePeriod.last_n_days(request.time_period_days or 30)
        dashboard_data = self.dashboard_data_service.get_dashboard_data(time_period)
        
        # 4. Return response
        return DashboardDataResponse(
            period=dashboard_data['period'],
            metrics=dashboard_data['metrics']
        )
