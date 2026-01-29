"""SMTP Email Provider for sending escalation emails via Gmail/Outlook."""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from .email_provider import IEmailProvider, EmailResult


# Support team email addresses
SUPPORT_TEAM_EMAILS = [
    "dylon.luo@castlery.com",
    "chunwoon.wong@castlery.com",
    "mai.nguyen@castlery.com",
    "weeming.ong@castlery.com",
    "fengyun.li@castlery.com",
]

# SMTP Configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")  # or smtp.office365.com
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # Your email address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # App password (not regular password!)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Castlery AI Support")


class SMTPEmailProvider(IEmailProvider):
    """SMTP email provider for Gmail, Outlook, or any SMTP server."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_name: Optional[str] = None,
        support_emails: Optional[List[str]] = None,
        use_tls: bool = True
    ):
        """
        Initialize SMTP email provider.
        
        Args:
            host: SMTP server host (default: smtp.gmail.com)
            port: SMTP server port (default: 587 for TLS)
            username: SMTP username (email address)
            password: SMTP password (use App Password for Gmail!)
            from_name: Display name for sender
            support_emails: List of support team email addresses
            use_tls: Whether to use TLS (default: True)
        """
        self._host = host or SMTP_HOST
        self._port = port or SMTP_PORT
        self._username = username or SMTP_USER
        self._password = password or SMTP_PASSWORD
        self._from_name = from_name or SMTP_FROM_NAME
        self._support_emails = support_emails or SUPPORT_TEAM_EMAILS
        self._use_tls = use_tls
        self._available = self._check_config()
        
        if self._available:
            print(f"[SMTP Email] ✓ Configured with {self._host}:{self._port}")
            print(f"[SMTP Email] Sender: {self._username}")
            print(f"[SMTP Email] Support team: {len(self._support_emails)} recipients")
        else:
            print("[SMTP Email] ✗ Not configured (missing SMTP_USER or SMTP_PASSWORD)")
    
    def _check_config(self) -> bool:
        """Check if SMTP is properly configured."""
        return bool(self._username and self._password)
    
    def send(self, to: str, subject: str, body: str) -> EmailResult:
        """
        Send an email via SMTP.
        
        Note: 'to' parameter is ignored - emails go to support team.
        """
        if not self._available:
            return EmailResult(
                success=False,
                message="SMTP not configured",
                error="Set SMTP_USER and SMTP_PASSWORD environment variables"
            )
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self._from_name} <{self._username}>"
            msg["To"] = ", ".join(self._support_emails)
            
            # Attach plain text and HTML versions
            text_part = MIMEText(body, "plain", "utf-8")
            html_part = MIMEText(self._format_html_body(body), "html", "utf-8")
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self._host, self._port) as server:
                if self._use_tls:
                    server.starttls(context=context)
                server.login(self._username, self._password)
                server.sendmail(
                    self._username,
                    self._support_emails,
                    msg.as_string()
                )
            
            print(f"[SMTP Email] ✓ Email sent successfully")
            print(f"[SMTP Email] Recipients: {', '.join(self._support_emails)}")
            
            return EmailResult(
                success=True,
                message=f"Email sent to {len(self._support_emails)} support team members"
            )
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[SMTP Email] ✗ Authentication failed: {e}")
            return EmailResult(
                success=False,
                message="SMTP authentication failed",
                error="Check SMTP_USER and SMTP_PASSWORD. For Gmail, use an App Password."
            )
        except smtplib.SMTPException as e:
            print(f"[SMTP Email] ✗ SMTP error: {e}")
            return EmailResult(
                success=False,
                message="Failed to send email",
                error=str(e)
            )
        except Exception as e:
            print(f"[SMTP Email] ✗ Unexpected error: {e}")
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
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 25px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header .subtitle {{
            margin-top: 8px;
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            background: #ffffff;
            padding: 25px;
            border: 1px solid #e0e0e0;
            border-top: none;
            border-radius: 0 0 12px 12px;
        }}
        .alert-badge {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        .conversation {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #1a1a2e;
        }}
        .message {{
            margin: 12px 0;
            padding: 12px 15px;
            border-radius: 8px;
        }}
        .user-message {{
            background: #e3f2fd;
            border-left: 3px solid #2196f3;
        }}
        .assistant-message {{
            background: #f5f5f5;
            border-left: 3px solid #9e9e9e;
        }}
        .footer {{
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 13px;
            color: #666;
            text-align: center;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .action-needed {{
            background: #fff3e0;
            border: 1px solid #ffb74d;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
        }}
        .action-needed strong {{
            color: #e65100;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Support Escalation Request</h1>
        <div class="subtitle">Castlery AI Support System</div>
    </div>
    <div class="content">
        <span class="alert-badge">ACTION REQUIRED</span>
        
        <div class="conversation">
            {html_body}
        </div>
        
        <div class="action-needed">
            <strong>⏰ Please respond within 24-48 business hours</strong>
        </div>
        
        <div class="footer">
            <p>This is an automated escalation from the Castlery AI Support System.</p>
            <p>The user was unable to resolve their issue with AI assistance.</p>
        </div>
    </div>
</body>
</html>
"""
    
    def is_available(self) -> bool:
        """Check if SMTP is available."""
        return self._available
    
    def get_support_emails(self) -> List[str]:
        """Get list of support team emails."""
        return self._support_emails.copy()
