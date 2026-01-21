"""
Email notification service for contact form submissions
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import asyncio
from functools import partial

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_username = os.environ.get("SMTP_USERNAME", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.from_email = os.environ.get("FROM_EMAIL", self.smtp_username)
        self.admin_email = os.environ.get("ADMIN_EMAIL", "contact@byoncocare.com")
        self.enabled = bool(self.smtp_username and self.smtp_password)
        
        if not self.enabled:
            logger.warning("Email service is disabled. Set SMTP_USERNAME and SMTP_PASSWORD environment variables to enable.")
    
    def _send_email_sync(self, msg: MIMEMultipart):
        """Synchronous email sending (runs in thread pool)"""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
    
    async def send_contact_notification(
        self,
        name: str,
        email: str,
        phone: str,
        message: str,
        contact_id: str
    ) -> bool:
        """
        Send email notification to admin about new contact form submission
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email service disabled. Would have sent notification for contact ID: {contact_id}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.admin_email
            msg['Subject'] = f"New Contact Form Submission - {name}"
            msg['Reply-To'] = email
            
            # Email body
            body = f"""
New Contact Form Submission Received

Contact ID: {contact_id}
Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}

---
This is an automated notification from ByOnco Contact Form.
You can reply directly to this email to contact the user.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_email_sync,
                msg
            )
            
            logger.info(f"Contact notification email sent successfully for contact ID: {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact notification email: {str(e)}")
            return False
    
    async def send_get_started_notification(
        self,
        submission_data: dict
    ) -> bool:
        """
        Send email notification to admin about new Get Started form submission
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email service disabled. Would have sent notification for submission ID: {submission_data.get('id')}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.admin_email
            msg['Subject'] = f"New Get Started Submission - {submission_data.get('full_name', 'Unknown')}"
            msg['Reply-To'] = submission_data.get('email', '')
            
            # Email body
            body = f"""
New Get Started Form Submission Received

Submission ID: {submission_data.get('id')}
Name: {submission_data.get('full_name')}
Email: {submission_data.get('email')}
Phone: {submission_data.get('phone')}
City: {submission_data.get('city')}
Country: {submission_data.get('country')}

Medical Information:
Cancer Type: {submission_data.get('cancer_type')}
Cancer Stage: {submission_data.get('cancer_stage')}

Insurance: {'Yes' if submission_data.get('has_insurance') else 'No'}
{f"Provider: {submission_data.get('insurance_provider')}" if submission_data.get('has_insurance') else ''}

Journey Planning:
Budget Range: {submission_data.get('budget_range_label', 'N/A')}
Preferred Cities: {', '.join(submission_data.get('preferred_cities', []))}
Urgency: {submission_data.get('urgency', 'N/A')}

Contact Preferences:
Preferred Method: {submission_data.get('preferred_contact_method', 'N/A')}
Preferred Time: {submission_data.get('preferred_time', 'N/A')}

Additional Notes:
{submission_data.get('additional_notes', 'None')}

Status: {submission_data.get('status', 'pending_review')}
Created At: {submission_data.get('created_at', 'N/A')}

---
This is an automated notification from ByOnco Get Started Form.
You can reply directly to this email to contact the user.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_email_sync,
                msg
            )
            
            logger.info(f"Get Started notification email sent successfully for submission ID: {submission_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Get Started notification email: {str(e)}")
            return False
    
    async def send_password_reset_email(
        self,
        email: str,
        reset_token: str,
        frontend_url: str = "https://www.byoncocare.com"
    ) -> bool:
        """
        Send password reset email to user
        
        Args:
            email: User's email address
            reset_token: Password reset token
            frontend_url: Frontend URL for reset link
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email service disabled. Would have sent password reset email to: {email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            msg['Subject'] = "Reset Your ByOnco Password"
            
            # Create reset link
            reset_link = f"{frontend_url}/authentication?token={reset_token}"
            
            # Email body (HTML for better formatting)
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reset Your Password</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>We received a request to reset your password for your ByOnco account. Click the button below to reset your password:</p>
            
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
            
            <div class="warning">
                <strong>⚠️ Important:</strong>
                <ul>
                    <li>This link will expire in 1 hour</li>
                    <li>If you didn't request this, please ignore this email</li>
                    <li>For security, never share this link with anyone</li>
                </ul>
            </div>
            
            <p>If you have any questions, please contact us at <a href="mailto:contact@byoncocare.com">contact@byoncocare.com</a></p>
        </div>
        <div class="footer">
            <p>© 2026 ByOnco by PraesidioCare Private Limited. All rights reserved.</p>
            <p>This is an automated email. Please do not reply to this message.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Plain text version for email clients that don't support HTML
            text_body = f"""
Reset Your ByOnco Password

Hello,

We received a request to reset your password for your ByOnco account.

Click this link to reset your password:
{reset_link}

Important:
- This link will expire in 1 hour
- If you didn't request this, please ignore this email
- For security, never share this link with anyone

If you have any questions, please contact us at contact@byoncocare.com

---
© 2026 ByOnco by PraesidioCare Private Limited. All rights reserved.
This is an automated email. Please do not reply to this message.
"""
            
            # Attach both HTML and plain text versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_email_sync,
                msg
            )
            
            logger.info(f"Password reset email sent successfully to: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False

