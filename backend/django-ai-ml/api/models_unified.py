"""
Django Models for Unified Phase Integration
All phases 1-10 share these unified models
"""

from django.db import models
from django.contrib.postgres.fields import JSONField
from mongoengine import Document, fields as mongo_fields
import uuid


# ============================================================================
# UNIFIED DJANGO MODELS (PostgreSQL)
# ============================================================================

class UnifiedPhase(models.Model):
    """Represents each phase in the system"""
    
    PHASE_CHOICES = [
        (1, "Core Infrastructure"),
        (2, "Food Inventory Management"),
        (3, "Distribution Logistics"),
        (4, "Recipient Management"),
        (5, "Donation Management"),
        (6, "Analytics & Reporting"),
        (7, "Mobile App Integration"),
        (8, "Advanced Analytics"),
        (9, "Error Logging & Monitoring"),
        (10, "AI Prediction & Recovery"),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    phase_id = models.IntegerField(unique=True, choices=PHASE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    api_endpoint = models.CharField(max_length=100)
    database_name = models.CharField(max_length=100)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_event_processed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Unified Phase"
        verbose_name_plural = "Unified Phases"
        ordering = ['phase_id']
    
    def __str__(self):
        return f"Phase {self.phase_id}: {self.name}"


class UnifiedEvent(models.Model):
    """Events flowing between phases"""
    
    EVENT_TYPES = [
        ('inventory_update', 'Inventory Update'),
        ('donation_received', 'Donation Received'),
        ('low_stock_alert', 'Low Stock Alert'),
        ('delivery_completed', 'Delivery Completed'),
        ('prediction_alert', 'Prediction Alert'),
        ('error_detected', 'Error Detected'),
        ('recovery_executed', 'Recovery Executed'),
        ('custom', 'Custom Event'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True)
    event_type = models.CharField(max_length=100, choices=EVENT_TYPES)
    
    # Source and routing
    source_phase = models.ForeignKey(
        UnifiedPhase, 
        on_delete=models.CASCADE, 
        related_name='emitted_events'
    )
    target_phases = models.ManyToManyField(
        UnifiedPhase,
        related_name='received_events'
    )
    
    # Event data
    data = JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Unified Event"
        verbose_name_plural = "Unified Events"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_phase', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} from Phase {self.source_phase.phase_id}"


class PhaseConnection(models.Model):
    """Defines how phases communicate"""
    
    FLOW_TYPES = [
        ('upstream', 'Upstream (sends to)'),
        ('downstream', 'Downstream (receives from)'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    TRIGGER_TYPES = [
        ('event', 'Event-triggered'),
        ('schedule', 'Scheduled'),
        ('manual', 'Manual'),
        ('api', 'API call'),
    ]
    
    from_phase = models.ForeignKey(
        UnifiedPhase,
        on_delete=models.CASCADE,
        related_name='outgoing_connections'
    )
    to_phase = models.ForeignKey(
        UnifiedPhase,
        on_delete=models.CASCADE,
        related_name='incoming_connections'
    )
    
    flow_type = models.CharField(max_length=20, choices=FLOW_TYPES)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    retry_count = models.IntegerField(default=3)
    timeout_seconds = models.IntegerField(default=30)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Phase Connection"
        verbose_name_plural = "Phase Connections"
        unique_together = ('from_phase', 'to_phase')
    
    def __str__(self):
        return f"Phase {self.from_phase.phase_id} → Phase {self.to_phase.phase_id}"


class UnifiedSystemState(models.Model):
    """Tracks overall system state"""
    
    # System metrics
    total_events_processed = models.BigIntegerField(default=0)
    total_events_failed = models.BigIntegerField(default=0)
    active_phases = models.IntegerField(default=10)
    
    # Performance
    average_event_processing_time_ms = models.FloatField(default=0.0)
    last_sync_timestamp = models.DateTimeField(auto_now=True)
    
    # Status
    is_healthy = models.BooleanField(default=True)
    last_health_check = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unified System State"
        verbose_name_plural = "Unified System States"
    
    def __str__(self):
        return f"System State - {self.active_phases} phases active"


class PhaseDataTransform(models.Model):
    """Transformation rules for data flowing between phases"""
    
    source_phase = models.ForeignKey(
        UnifiedPhase,
        on_delete=models.CASCADE,
        related_name='source_transforms'
    )
    target_phase = models.ForeignKey(
        UnifiedPhase,
        on_delete=models.CASCADE,
        related_name='target_transforms'
    )
    
    # Transformation logic
    source_field = models.CharField(max_length=255)
    target_field = models.CharField(max_length=255)
    transformation_logic = models.TextField(help_text="Python code for transformation")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Phase Data Transform"
        verbose_name_plural = "Phase Data Transforms"
    
    def __str__(self):
        return f"{self.source_phase.name}.{self.source_field} → {self.target_phase.name}.{self.target_field}"


# ============================================================================
# MONGOENGINE MODELS (NoSQL for ML & Logs)
# ============================================================================

class UnifiedEventLog(Document):
    """MongoDB collection for all events (for analytics & ML)"""
    
    event_id = mongo_fields.StringField(unique=True)
    event_type = mongo_fields.StringField()
    source_phase_id = mongo_fields.IntField()
    target_phase_ids = mongo_fields.ListField(mongo_fields.IntField())
    
    # Event data
    data = mongo_fields.DynamicField()
    metadata = mongo_fields.DictField()
    
    # Timestamps
    created_at = mongo_fields.DateTimeField()
    processed_at = mongo_fields.DateTimeField()
    processing_time_ms = mongo_fields.FloatField()
    
    # Status
    status = mongo_fields.StringField()
    error_log = mongo_fields.StringField()
    
    class Meta:
        collection = 'unified_event_logs'
        indexes = [
            'event_type',
            'source_phase_id',
            'created_at',
            'status',
        ]


class PhasePrediction(Document):
    """MongoDB collection for predictions about phase behavior"""
    
    phase_id = mongo_fields.IntField()
    prediction_type = mongo_fields.StringField()  # "error", "bottleneck", "anomaly"
    
    # Prediction data
    predicted_event = mongo_fields.StringField()
    confidence_score = mongo_fields.FloatField()
    predicted_time = mongo_fields.DateTimeField()
    
    # Context
    based_on_events = mongo_fields.ListField(mongo_fields.StringField())
    historical_patterns = mongo_fields.DictField()
    
    # Tracking
    created_at = mongo_fields.DateTimeField()
    was_accurate = mongo_fields.BooleanField()
    actual_event = mongo_fields.StringField()
    
    class Meta:
        collection = 'phase_predictions'
        indexes = ['phase_id', 'prediction_type', 'created_at']


class PhaseHealthMetrics(Document):
    """MongoDB collection for phase health metrics"""
    
    phase_id = mongo_fields.IntField()
    
    # Health metrics
    uptime_percentage = mongo_fields.FloatField()
    error_rate = mongo_fields.FloatField()
    average_response_time_ms = mongo_fields.FloatField()
    
    # Event statistics
    events_processed = mongo_fields.IntField()
    events_failed = mongo_fields.IntField()
    events_pending = mongo_fields.IntField()
    
    # Dependencies
    dependent_phases = mongo_fields.ListField(mongo_fields.IntField())
    dependent_on_phases = mongo_fields.ListField(mongo_fields.IntField())
    
    # Timestamp
    measured_at = mongo_fields.DateTimeField()
    
    class Meta:
        collection = 'phase_health_metrics'
        indexes = ['phase_id', '-measured_at']
