"""
Error Notification Service
Handles sending notifications via email, Slack, SMS, and webhooks
"""

import logging
import smtplib
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str, error_data: Dict) -> bool:
        """Send notification"""
        pass


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 sender_email: str = None, sender_password: str = None):
        self.smtp_server = smtp_server or getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or getattr(settings, 'EMAIL_PORT', 587)
        self.sender_email = sender_email or getattr(settings, 'EMAIL_HOST_USER', 'noreply@feedinghearts.com')
        self.sender_password = sender_password or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    
    def send(self, recipient: str, subject: str, message: str, error_data: Dict) -> bool:
        """Send email notification"""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient
            
            # Create HTML version
            html = self._create_html_email(message, error_data)
            
            # Attach plain text and HTML versions
            part1 = MIMEText(message, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient} for error {error_data.get('error_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False
    
    @staticmethod
    def _create_html_email(message: str, error_data: Dict) -> str:
        """Create HTML version of email"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>🚨 Error Notification from Feeding Hearts</h2>
                <p><strong>Service:</strong> {error_data.get('service', 'Unknown')}</p>
                <p><strong>Severity:</strong> <span style="color: {'red' if error_data.get('severity') == 'critical' else 'orange'}; font-weight: bold;">{error_data.get('severity', 'Unknown').upper()}</span></p>
                <p><strong>Error Type:</strong> {error_data.get('error_type', 'Unknown')}</p>
                <p><strong>Time:</strong> {error_data.get('timestamp', 'Unknown')}</p>
                <hr>
                <p><strong>Message:</strong></p>
                <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">{message}</pre>
                <hr>
                <p><strong>Endpoint:</strong> {error_data.get('endpoint', 'N/A')}</p>
                <p><strong>Error ID:</strong> <code>{error_data.get('error_id', 'N/A')}</code></p>
                <hr>
                <p><a href="{getattr(settings, 'DASHBOARD_URL', 'https://feedinghearts.local')}/errors/{error_data.get('error_id', '')}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Error Details</a></p>
                <p style="color: #999; font-size: 12px; margin-top: 20px;">This is an automated message from Feeding Hearts Error Tracking System</p>
            </body>
        </html>
        """


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or getattr(settings, 'SLACK_WEBHOOK_URL', '')
    
    def send(self, recipient: str, subject: str, message: str, error_data: Dict) -> bool:
        """Send Slack notification"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            severity_color = {
                'critical': '#FF0000',
                'high': '#FF6600',
                'medium': '#FFCC00',
                'low': '#0066CC',
                'info': '#00CC00',
            }
            
            payload = {
                'text': f"🚨 {subject}",
                'attachments': [
                    {
                        'color': severity_color.get(error_data.get('severity', 'info'), '#999'),
                        'fields': [
                            {
                                'title': 'Service',
                                'value': error_data.get('service', 'Unknown'),
                                'short': True
                            },
                            {
                                'title': 'Severity',
                                'value': error_data.get('severity', 'Unknown').upper(),
                                'short': True
                            },
                            {
                                'title': 'Error Type',
                                'value': error_data.get('error_type', 'Unknown'),
                                'short': True
                            },
                            {
                                'title': 'Endpoint',
                                'value': error_data.get('endpoint', 'N/A'),
                                'short': True
                            },
                            {
                                'title': 'Message',
                                'value': message,
                                'short': False
                            },
                            {
                                'title': 'Error ID',
                                'value': error_data.get('error_id', 'N/A'),
                                'short': True
                            },
                            {
                                'title': 'Timestamp',
                                'value': str(error_data.get('timestamp', '')),
                                'short': True
                            }
                        ],
                        'actions': [
                            {
                                'type': 'button',
                                'text': 'View Details',
                                'url': f"{getattr(settings, 'DASHBOARD_URL', 'https://feedinghearts.local')}/errors/{error_data.get('error_id', '')}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent to {recipient}")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return False


class SMSNotificationChannel(NotificationChannel):
    """SMS notification channel (Twilio)"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, 
                 from_number: str = None):
        self.account_sid = account_sid or getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = auth_token or getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.from_number = from_number or getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    
    def send(self, recipient: str, subject: str, message: str, error_data: Dict) -> bool:
        """Send SMS notification"""
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # Shorten message for SMS
            sms_message = f"🚨 {error_data.get('severity', 'Error').upper()}: {error_data.get('error_type', 'Unknown')} in {error_data.get('service', 'Unknown')} - {message[:80]}..."
            
            message_obj = client.messages.create(
                body=sms_message,
                from_=self.from_number,
                to=recipient
            )
            
            logger.info(f"SMS sent to {recipient}: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook notification channel"""
    
    def __init__(self, webhook_urls: List[str] = None):
        self.webhook_urls = webhook_urls or getattr(settings, 'ERROR_WEBHOOK_URLS', [])
    
    def send(self, recipient: str, subject: str, message: str, error_data: Dict) -> bool:
        """Send webhook notification"""
        if not self.webhook_urls:
            logger.warning("Webhook URLs not configured")
            return False
        
        try:
            payload = {
                'timestamp': datetime.utcnow().isoformat(),
                'subject': subject,
                'message': message,
                'error_data': error_data,
            }
            
            success = True
            for webhook_url in self.webhook_urls:
                try:
                    response = requests.post(webhook_url, json=payload, timeout=10)
                    if response.status_code >= 400:
                        success = False
                        logger.error(f"Webhook failed: {webhook_url} - {response.status_code}")
                    else:
                        logger.info(f"Webhook sent to {webhook_url}")
                except Exception as e:
                    success = False
                    logger.error(f"Failed to send webhook to {webhook_url}: {str(e)}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to process webhook notification: {str(e)}")
            return False


class NotificationService:
    """Service for managing error notifications"""
    
    def __init__(self):
        self.channels = {
            'email': EmailNotificationChannel(),
            'slack': SlackNotificationChannel(),
            'sms': SMSNotificationChannel(),
            'webhook': WebhookNotificationChannel(),
        }
    
    def send_notification(self, error_id: str, recipient: str, channels: List[str] = None) -> Dict[str, bool]:
        """Send notification to specified channels"""
        from .models import ErrorLog, ErrorNotification
        
        try:
            error = ErrorLog.objects.get(error_id=error_id)
        except ErrorLog.DoesNotExist:
            logger.error(f"Error not found: {error_id}")
            return {'error': 'Error not found'}
        
        if channels is None:
            channels = ['email', 'slack']
        
        results = {}
        
        for channel_name in channels:
            if channel_name not in self.channels:
                logger.warning(f"Unknown channel: {channel_name}")
                continue
            
            channel = self.channels[channel_name]
            
            subject = f"[{error.severity.upper()}] {error.error_type} in {error.service}"
            message = error.message
            
            error_data = {
                'error_id': str(error.error_id),
                'service': error.service,
                'severity': error.severity,
                'error_type': error.error_type,
                'timestamp': error.timestamp.isoformat(),
                'endpoint': error.endpoint,
            }
            
            success = channel.send(recipient, subject, message, error_data)
            results[channel_name] = success
            
            # Log notification
            if success:
                ErrorNotification.objects.create(
                    error=error,
                    recipient=recipient,
                    channel=channel_name,
                    status='sent',
                    message_subject=subject,
                    message_body=message,
                )
            else:
                ErrorNotification.objects.create(
                    error=error,
                    recipient=recipient,
                    channel=channel_name,
                    status='failed',
                    message_subject=subject,
                    message_body=message,
                    failure_reason=f"Failed to send via {channel_name}",
                )
        
        return results
    
    def notify_developers(self, error_id: str) -> Dict[str, bool]:
        """Notify all assigned developers about error"""
        from .models import ErrorLog, DeveloperAssignment
        
        try:
            error = ErrorLog.objects.get(error_id=error_id)
        except ErrorLog.DoesNotExist:
            logger.error(f"Error not found: {error_id}")
            return {'error': 'Error not found'}
        
        # Get developers assigned to this error's service
        developers = DeveloperAssignment.objects.filter(
            services__contains=error.service,
            on_call=True
        )
        
        results = {}
        preferred_channels = {
            'critical': ['email', 'slack', 'sms'],
            'high': ['email', 'slack'],
            'medium': ['email'],
            'low': ['email'],
            'info': ['email'],
        }
        
        channels = preferred_channels.get(error.severity, ['email'])
        
        for dev in developers:
            if dev.can_receive_notification():
                dev_results = self.send_notification(
                    error_id,
                    dev.email,
                    channels
                )
                results[str(dev.developer_id)] = dev_results
                logger.info(f"Notifications sent to developer {dev.name}")
        
        return results
    
    def retry_failed_notifications(self) -> Dict[str, int]:
        """Retry failed notifications"""
        from .models import ErrorNotification
        
        failed_notifications = ErrorNotification.objects.filter(
            status='failed',
            retry_count__lt=3
        )
        
        results = {'retried': 0, 'succeeded': 0, 'failed': 0}
        
        for notification in failed_notifications:
            channels = [notification.channel]
            dev_results = self.send_notification(
                str(notification.error.error_id),
                notification.recipient,
                channels
            )
            
            if dev_results.get(notification.channel, False):
                notification.status = 'sent'
                results['succeeded'] += 1
                logger.info(f"Notification {notification.notification_id} retry succeeded")
            else:
                notification.retry_count += 1
                results['failed'] += 1
                logger.error(f"Notification {notification.notification_id} retry failed")
            
            notification.save()
            results['retried'] += 1
        
        return results
