"""
Demo script for Unit 5: Communication & Analytics Service

This script demonstrates the key functionality of the service:
1. Sending escalation emails
2. Recording analytics events
3. Calculating metrics
4. Retrieving dashboard data
"""

from datetime import datetime, timedelta
from src.domain.aggregates import Metric
from src.domain.value_objects import (
    EventType, EventMetadata, TimePeriod, MetricId, MetricType, MetricValue
)
from src.domain.services import (
    EmailCompositionService, MetricsCalculationService, DashboardDataService
)
from src.infrastructure.repositories import (
    InMemoryEscalationEmailRepository,
    InMemoryAnalyticsEventRepository,
    InMemoryMetricRepository
)
from src.infrastructure.email import MockEmailProvider
from src.infrastructure.events import InMemoryEventPublisher
from src.application.clients import AccessControlClient, ChatInterfaceClient
from src.application.services import (
    SendEscalationEmailApplicationService,
    RecordAnalyticsEventApplicationService,
    GetDashboardDataApplicationService
)
from src.application.dtos import (
    SendEscalationEmailRequest,
    RecordEventRequest,
    GetDashboardRequest
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_escalation_email():
    """Demonstrate escalation email functionality."""
    print_section("1. ESCALATION EMAIL DEMO")
    
    # Setup dependencies
    email_repository = InMemoryEscalationEmailRepository()
    email_provider = MockEmailProvider()
    event_publisher = InMemoryEventPublisher()
    access_control_client = AccessControlClient()
    chat_interface_client = ChatInterfaceClient()
    email_composition_service = EmailCompositionService()
    
    # Create service
    service = SendEscalationEmailApplicationService(
        email_repository=email_repository,
        email_provider=email_provider,
        event_publisher=event_publisher,
        access_control_client=access_control_client,
        chat_interface_client=chat_interface_client,
        email_composition_service=email_composition_service
    )
    
    # Send escalation email
    request = SendEscalationEmailRequest(
        conversation_id="conv-001",
        user_id="user-123",
        reason="User unable to reset password after multiple attempts",
        token="token-user-123"
    )
    
    print(f"Sending escalation email for conversation: {request.conversation_id}")
    print(f"User: {request.user_id}")
    print(f"Reason: {request.reason}\n")
    
    response = service.execute(request)
    
    print(f"✓ Email ID: {response.email_id}")
    print(f"✓ Status: {response.status}")
    print(f"✓ Sent to: {response.sent_to}")
    print(f"✓ Message: {response.message}")
    
    # Show sent email content
    print("\n--- Email Content Preview ---")
    sent_emails = email_provider.get_sent_emails()
    if sent_emails:
        email = sent_emails[0]
        print(f"Subject: {email['subject']}")
        print(f"Body (first 300 chars):\n{email['body'][:300]}...")
    
    return email_repository, event_publisher


def demo_analytics_events(event_repository: InMemoryAnalyticsEventRepository):
    """Demonstrate analytics event recording."""
    print_section("2. ANALYTICS EVENTS DEMO")
    
    event_publisher = InMemoryEventPublisher()
    
    service = RecordAnalyticsEventApplicationService(
        event_repository=event_repository,
        event_publisher=event_publisher
    )
    
    # Record various events
    events_to_record = [
        {
            "event_type": "query_submitted",
            "user_id": "user-123",
            "conversation_id": "conv-001",
            "metadata": {"query": "How do I reset my password?"}
        },
        {
            "event_type": "query_submitted",
            "user_id": "user-123",
            "conversation_id": "conv-002",
            "metadata": {"query": "What are the system requirements?"}
        },
        {
            "event_type": "feedback_submitted",
            "user_id": "user-123",
            "conversation_id": "conv-002",
            "metadata": {"problem_solved": True, "rating": 5}
        },
        {
            "event_type": "feedback_submitted",
            "user_id": "user-123",
            "conversation_id": "conv-001",
            "metadata": {"problem_solved": False, "rating": 2}
        },
        {
            "event_type": "escalation_triggered",
            "user_id": "user-123",
            "conversation_id": "conv-001",
            "metadata": {"reason": "Unable to resolve password reset issue"}
        },
        {
            "event_type": "user_authenticated",
            "user_id": "user-123",
            "conversation_id": None,
            "metadata": {"method": "password"}
        }
    ]
    
    print(f"Recording {len(events_to_record)} analytics events...\n")
    
    for event_data in events_to_record:
        request = RecordEventRequest(**event_data)
        response = service.execute(request)
        print(f"✓ Recorded {event_data['event_type']}: {response.event_id}")
    
    print(f"\nTotal events in repository: {len(event_repository._events)}")
    
    return event_repository


def demo_metrics_calculation(event_repository: InMemoryAnalyticsEventRepository):
    """Demonstrate metrics calculation."""
    print_section("3. METRICS CALCULATION DEMO")
    
    metric_repository = InMemoryMetricRepository()
    metrics_service = MetricsCalculationService(event_repository)
    
    # Calculate metrics for last 30 days
    time_period = TimePeriod.last_30_days()
    
    print(f"Calculating metrics for period: {time_period}\n")
    
    # Calculate each metric
    total_queries = metrics_service.calculate_total_queries(time_period)
    print(f"✓ Total Queries: {total_queries}")
    
    resolution_rate = metrics_service.calculate_resolution_rate(time_period)
    print(f"✓ Resolution Rate: {resolution_rate:.2f}%")
    
    escalation_count = metrics_service.calculate_escalation_count(time_period)
    print(f"✓ Escalation Count: {escalation_count}")
    
    active_users = metrics_service.calculate_active_users(time_period)
    print(f"✓ Active Users: {active_users}")
    
    top_queries = metrics_service.calculate_top_queries(time_period, 5)
    print(f"✓ Top Queries:")
    for i, (query, count) in enumerate(top_queries, 1):
        print(f"   {i}. \"{query}\" ({count} times)")
    
    # Save metrics to repository
    print("\nSaving metrics to repository...")
    
    metrics_to_save = [
        Metric(
            metric_id=MetricId.generate(),
            metric_type=MetricType.TOTAL_QUERIES,
            value=MetricValue(total_queries, "count"),
            time_period=time_period
        ),
        Metric(
            metric_id=MetricId.generate(),
            metric_type=MetricType.RESOLUTION_RATE,
            value=MetricValue(resolution_rate, "percentage"),
            time_period=time_period
        ),
        Metric(
            metric_id=MetricId.generate(),
            metric_type=MetricType.ESCALATION_COUNT,
            value=MetricValue(escalation_count, "count"),
            time_period=time_period
        ),
        Metric(
            metric_id=MetricId.generate(),
            metric_type=MetricType.ACTIVE_USERS,
            value=MetricValue(active_users, "count"),
            time_period=time_period
        ),
        Metric(
            metric_id=MetricId.generate(),
            metric_type=MetricType.TOP_QUERIES,
            value=MetricValue([{"query": q, "count": c} for q, c in top_queries], "list"),
            time_period=time_period
        )
    ]
    
    for metric in metrics_to_save:
        metric_repository.save(metric)
    
    print(f"✓ Saved {len(metrics_to_save)} metrics")
    
    return metric_repository


def demo_dashboard_data(metric_repository: InMemoryMetricRepository):
    """Demonstrate dashboard data retrieval."""
    print_section("4. DASHBOARD DATA DEMO")
    
    dashboard_service = DashboardDataService(metric_repository)
    access_control_client = AccessControlClient()
    
    service = GetDashboardDataApplicationService(
        dashboard_data_service=dashboard_service,
        access_control_client=access_control_client
    )
    
    # Get dashboard data (as admin)
    request = GetDashboardRequest(
        token="token-admin-456",
        time_period_days=30
    )
    
    print("Retrieving dashboard data (as administrator)...\n")
    
    response = service.execute(request)
    
    print(f"Dashboard Period: {response.period['days']} days")
    print(f"From: {response.period['start_date']}")
    print(f"To: {response.period['end_date']}\n")
    
    print("Metrics:")
    for metric_name, metric_data in response.metrics.items():
        print(f"\n  {metric_name.upper()}:")
        print(f"    Value: {metric_data['value']}")
        print(f"    Trend: {metric_data['trend']}")
        print(f"    Calculated: {metric_data['calculated_at']}")
    
    # Try with non-admin user (should fail)
    print("\n\nAttempting to access dashboard as non-admin user...")
    try:
        non_admin_request = GetDashboardRequest(
            token="token-user-123",
            time_period_days=30
        )
        service.execute(non_admin_request)
    except PermissionError as e:
        print(f"✓ Access denied (as expected): {e}")


def demo_domain_events(event_publisher: InMemoryEventPublisher):
    """Show published domain events."""
    print_section("5. DOMAIN EVENTS SUMMARY")
    
    published_events = event_publisher.get_published_events()
    
    print(f"Total domain events published: {len(published_events)}\n")
    
    event_types = {}
    for event_record in published_events:
        event_type = event_record['event_type']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("Events by type:")
    for event_type, count in event_types.items():
        print(f"  • {event_type}: {count}")


def main():
    """Run the complete demo."""
    print("\n" + "=" * 70)
    print("  UNIT 5: COMMUNICATION & ANALYTICS SERVICE - DEMO")
    print("=" * 70)
    print("\nThis demo showcases the Domain-Driven Design implementation")
    print("of the Communication & Analytics Service.\n")
    
    # Run demos
    email_repo, event_publisher = demo_escalation_email()
    event_repo = demo_analytics_events(InMemoryAnalyticsEventRepository())
    metric_repo = demo_metrics_calculation(event_repo)
    demo_dashboard_data(metric_repo)
    demo_domain_events(event_publisher)
    
    # Final summary
    print_section("DEMO COMPLETE")
    print("✓ Escalation email sent successfully")
    print("✓ Analytics events recorded")
    print("✓ Metrics calculated")
    print("✓ Dashboard data retrieved")
    print("✓ Domain events published")
    print("\nAll DDD principles demonstrated:")
    print("  • Aggregates (EscalationEmail, AnalyticsEvent, Metric)")
    print("  • Value Objects (EmailId, EventType, MetricValue, etc.)")
    print("  • Domain Services (EmailCompositionService, MetricsCalculationService)")
    print("  • Repositories (In-memory implementations)")
    print("  • Domain Events (EscalationEmailSent, AnalyticsEventRecorded, etc.)")
    print("  • Application Services (Orchestration layer)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
