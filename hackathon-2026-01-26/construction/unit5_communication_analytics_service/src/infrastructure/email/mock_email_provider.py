import random
from .email_provider import IEmailProvider, EmailResult


class MockEmailProvider(IEmailProvider):
    """Mock email provider for testing and demo purposes."""
    
    def __init__(self, simulate_failures: bool = False, failure_rate: float = 0.2):
        """
        Initialize mock email provider.
        
        Args:
            simulate_failures: Whether to simulate random failures
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        self.simulate_failures = simulate_failures
        self.failure_rate = failure_rate
        self.sent_emails = []
    
    def send(self, to: str, subject: str, body: str) -> EmailResult:
        """Send an email (mock implementation)."""
        # Simulate random failures if enabled
        if self.simulate_failures and random.random() < self.failure_rate:
            return EmailResult(
                success=False,
                message="Failed to send email",
                error="SMTP connection timeout (simulated)"
            )
        
        # Store sent email for verification
        self.sent_emails.append({
            'to': to,
            'subject': subject,
            'body': body
        })
        
        return EmailResult(
            success=True,
            message=f"Email sent successfully to {to}"
        )
    
    def is_available(self) -> bool:
        """Check if email provider is available."""
        return True
    
    def get_sent_emails(self):
        """Get list of sent emails (for testing)."""
        return self.sent_emails
    
    def clear_sent_emails(self):
        """Clear sent emails list (for testing)."""
        self.sent_emails.clear()
