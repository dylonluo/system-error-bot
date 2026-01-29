"""AWS SES Email Provider for sending escalation emails."""
import os
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .email_provider import IEmailProvider, EmailResult


# Support team email addresses
SUPPORT_TEAM_EMAILS = [
    "dylon.luo@castlery.com",
    "chunwoon.wong@castlery.com",
    "mai.nguyen@castlery.com",
    "weeming.ong@castlery.com",
    "fengyun.li@castlery.com",
]

# Default sender email (must be verified in SES)
DEFAULT_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@castlery.com")


class SESEmailProvider(IEmailProvider):
    """AWS SES email provider for production use."""
    
    def __init__(
        self, 
        region: str = "ap-southeast-1",
        sender_email: Optional[str] = None,
        support_emails: Optional[List[str]] = None
    ):
        """
        Initialize SES email provider.
        
        Args:
            region: AWS region for SES
            sender_email: Verified sender email address
            support_emails: List of support team email addresses
        """
        self._region = region
        self._sender_email = sender_email or DEFAULT_SENDER_EMAIL
        self._support_emails = support_emails or SUPPORT_TEAM_EMAILS
        self._client = None
        self._available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize SES client."""
        try:
            self._client = boto3.client('ses', region_name=self._region)
            # Test connection by getting send quota
            self._client.get_send_quota()
            self._available = True
            print(f"[SES Email] ✓ Connected to AWS SES in {self._region}")
            print(f"[SES Email] Sender: {self._sender_email}")
            print(f"[SES Email] Support team: {len(self._support_emails)} recipients")
        except NoCredentialsError:
            print("[SES Email] AWS credentials not found, falling back to mock")
            self._available = False
        except ClientError as e:
            print(f"[SES Email] Error connecting to SES: {e}")
            self._available = False
        except Exception as e:
            print(f"[SES Email] Unexpected error: {e}")
            self._available = False
    
    def send(self, to: str, subject: str, body: str) -> EmailResult:
        """
        Send an email via AWS SES.
        
        Note: 'to' parameter is ignored - emails go to support team.
        """
        if not self._available:
            return EmailResult(
                success=False,
                message="SES not available",
                error="AWS SES is not configured or unavailable"
            )
        
        try:
            # Send to all support team members
            response = self._client.send_email(
                Source=self._sender_email,
                Destination={
                    'ToAddresses': self._support_emails,
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': self._format_html_body(body),
                            'Charset': 'UTF-8'
                        },
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                },
                ReplyToAddresses=[self._sender_email],
            )
            
            message_id = response.get('MessageId', 'unknown')
            print(f"[SES Email] ✓ Email sent successfully (MessageId: {message_id})")
            print(f"[SES Email] Recipients: {', '.join(self._support_emails)}")
            
            return EmailResult(
                success=True,
                message=f"Email sent to {len(self._support_emails)} support team members (MessageId: {message_id})"
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            print(f"[SES Email] ✗ Failed to send: {error_code} - {error_msg}")
            
            return EmailResult(
                success=False,
                message="Failed to send email",
                error=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            print(f"[SES Email] ✗ Unexpected error: {e}")
            return EmailResult(
                success=False,
                message="Failed to send email",
                error=str(e)
            )
    
    def _format_html_body(self, text_body: str) -> str:
        """Convert plain text body to HTML format."""
        # Escape HTML characters
        html_body = text_body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Convert newlines to <br>
        html_body = html_body.replace('\n', '<br>\n')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #1a1a2e;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #f8f9fa;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        .conversation {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #e9ecef;
        }}
        .user-message {{
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .assistant-message {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Support Escalation Request</h1>
    </div>
    <div class="content">
        <div class="conversation">
            {html_body}
        </div>
        <div class="footer">
            <p>This is an automated escalation from the Castlery AI Support System.</p>
            <p>Please respond to the user within 24-48 business hours.</p>
        </div>
    </div>
</body>
</html>
"""
    
    def is_available(self) -> bool:
        """Check if SES is available."""
        return self._available
    
    def get_support_emails(self) -> List[str]:
        """Get list of support team emails."""
        return self._support_emails.copy()
