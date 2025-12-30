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

