"""
Django Error Logging and Notification System
Handles error capture, storage, and developer notifications
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
import uuid
import logging

logger = logging.getLogger(__name__)


class ErrorLog(TimeStampedModel):
    """Model for storing application errors"""
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]
    
    SERVICE_CHOICES = [
        ('django', 'Django'),
        ('laravel', 'Laravel'),
        ('java', 'Java'),
        ('react', 'React'),
        ('angular', 'Angular'),
        ('vue', 'Vue'),
        ('flutter', 'Flutter'),
        ('nginx', 'Nginx'),
    ]
    
    ENVIRONMENT_CHOICES = [
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ]
    
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('sms', 'SMS'),
        ('dashboard', 'Dashboard'),
        ('webhook', 'Webhook'),
    ]
    
    error_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    error_type = models.CharField(max_length=100)
    message = models.TextField()
    code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Request context
    user_id = models.UUIDField(null=True, blank=True)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    request_id = models.UUIDField(null=True, blank=True)
    
    # Stack trace and context
    stack_trace = models.TextField(null=True, blank=True)
    context = models.JSONField(default=dict, blank=True)
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES)
    
    # Resolution tracking
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    # Notification tracking
    notification_sent = models.BooleanField(default=False)
    notification_channels = ArrayField(
        models.CharField(max_length=20, choices=NOTIFICATION_CHANNELS),
        default=list,
        blank=True
    )
    
    # Assignment
    assigned_to = models.CharField(max_length=100, null=True, blank=True)
    
    # Frequency tracking
    frequency = models.IntegerField(default=1)
    last_occurrence = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'error_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['severity']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['resolved']),
            models.Index(fields=['service', '-timestamp']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.error_type} - {self.service}"
    
    def mark_resolved(self, resolved_by, notes=""):
        """Mark error as resolved"""
        self.resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        self.notes = notes
        self.save()
    
    def assign_to_developer(self, developer_id):
        """Assign error to developer"""
        self.assigned_to = developer_id
        self.save()


class ErrorNotification(TimeStampedModel):
    """Model for tracking error notifications"""
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('read', 'Read'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    
    notification_id = models.UUIDField(unique=True, default=uuid.uuid4)
    error = models.ForeignKey(ErrorLog, on_delete=models.CASCADE, related_name='notifications')
    
    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField(null=True, blank=True)
    recipient_phone = models.CharField(max_length=20, null=True, blank=True)
    recipient_slack_id = models.CharField(max_length=100, null=True, blank=True)
    
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'error_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['error']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Notification {self.notification_id} - {self.channel} ({self.status})"


class ErrorPattern(TimeStampedModel):
    """Model for tracking error patterns and root causes"""
    
    pattern_id = models.UUIDField(unique=True, default=uuid.uuid4)
    error_type = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    description = models.TextField()
    
    occurrence_count = models.IntegerField(default=0)
    last_occurrence = models.DateTimeField(null=True, blank=True)
    
    root_cause = models.TextField(null=True, blank=True)
    resolution = models.TextField(null=True, blank=True)
    prevention_tips = ArrayField(models.TextField(), default=list, blank=True)
    related_errors = ArrayField(models.UUIDField(), default=list, blank=True)
    
    class Meta:
        db_table = 'error_patterns'
        unique_together = ['error_type', 'service']
        ordering = ['-occurrence_count']
    
    def __str__(self):
        return f"{self.service} - {self.error_type}"


class DeveloperAssignment(models.Model):
    """Model for managing developer assignments"""
    
    developer_id = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    slack_id = models.CharField(max_length=100, null=True, blank=True)
    
    services = ArrayField(models.CharField(max_length=50), default=list)
    severity_levels = ArrayField(
        models.CharField(max_length=20),
        default=list,
        help_text="Severity levels: critical, high, medium, low"
    )
    
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification preferences
    email_enabled = models.BooleanField(default=True)
    slack_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    on_call = models.BooleanField(default=False)
    current_load = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'developer_assignments'
        ordering = ['on_call', 'current_load']
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def can_receive_notification(self, severity, notification_type='email'):
        """Check if developer can receive notification"""
        # Check if developer handles this severity
        if severity not in self.severity_levels:
            return False
        
        # Check if notification type is enabled
        if notification_type == 'email' and not self.email_enabled:
            return False
        if notification_type == 'slack' and not self.slack_enabled:
            return False
        if notification_type == 'sms' and not self.sms_enabled:
            return False
        
        return True


class ErrorEscalation(models.Model):
    """Model for error escalation tracking"""
    
    escalation_id = models.UUIDField(unique=True, default=uuid.uuid4)
    error = models.ForeignKey(ErrorLog, on_delete=models.CASCADE, related_name='escalations')
    
    escalated_from = models.CharField(max_length=100, null=True, blank=True)
    escalated_to = models.CharField(max_length=100)
    escalation_level = models.IntegerField(default=1)
    
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'error_escalation'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Escalation {self.escalation_id} - Level {self.escalation_level}"


# ============== SERIALIZERS ==============

from rest_framework import serializers


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = [
            'error_id', 'service', 'severity', 'error_type', 'message',
            'code', 'timestamp', 'user_id', 'endpoint', 'request_id',
            'stack_trace', 'context', 'environment', 'resolved',
            'resolved_at', 'resolved_by', 'notes', 'notification_sent',
            'notification_channels', 'assigned_to', 'frequency'
        ]
        read_only_fields = ['error_id', 'timestamp', 'created_at', 'updated_at']


class ErrorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorNotification
        fields = [
            'notification_id', 'error', 'recipient_name', 'recipient_email',
            'recipient_phone', 'recipient_slack_id', 'channel', 'status',
            'delivered_at', 'read_at', 'retry_count', 'error_message'
        ]
        read_only_fields = ['notification_id', 'created_at']


class DeveloperAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeveloperAssignment
        fields = [
            'developer_id', 'name', 'email', 'phone', 'slack_id',
            'services', 'severity_levels', 'timezone', 'email_enabled',
            'slack_enabled', 'sms_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'on_call', 'current_load'
        ]


class ErrorPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorPattern
        fields = [
            'pattern_id', 'error_type', 'service', 'description',
            'occurrence_count', 'last_occurrence', 'root_cause',
            'resolution', 'prevention_tips', 'related_errors'
        ]
