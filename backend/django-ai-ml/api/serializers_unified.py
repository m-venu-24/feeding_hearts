"""
Django REST Serializers for Unified Phase Integration
Serialization for all unified models
"""

from rest_framework import serializers
from api.models_unified import (
    UnifiedPhase, UnifiedEvent, PhaseConnection, 
    UnifiedSystemState, PhaseDataTransform
)


# ============================================================================
# UNIFIED PHASE SERIALIZERS
# ============================================================================

class UnifiedPhaseSerializer(serializers.ModelSerializer):
    """Serializer for UnifiedPhase model"""
    
    class Meta:
        model = UnifiedPhase
        fields = [
            'phase_id',
            'name',
            'description',
            'status',
            'api_endpoint',
            'database_name',
            'created_at',
            'updated_at',
            'last_event_processed',
        ]
        read_only_fields = ['phase_id', 'created_at', 'updated_at']


class UnifiedPhaseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for UnifiedPhase with relationships"""
    
    outgoing_connections = serializers.SerializerMethodField()
    incoming_connections = serializers.SerializerMethodField()
    recent_events = serializers.SerializerMethodField()
    
    class Meta:
        model = UnifiedPhase
        fields = [
            'phase_id',
            'name',
            'description',
            'status',
            'api_endpoint',
            'database_name',
            'created_at',
            'updated_at',
            'last_event_processed',
            'outgoing_connections',
            'incoming_connections',
            'recent_events',
        ]
        read_only_fields = ['phase_id', 'created_at', 'updated_at']
    
    def get_outgoing_connections(self, obj):
        """Get outgoing phase connections"""
        connections = obj.outgoing_connections.filter(is_active=True)
        return [
            {
                'to_phase_id': c.to_phase.phase_id,
                'to_phase_name': c.to_phase.name,
                'flow_type': c.flow_type,
                'trigger_type': c.trigger_type,
            }
            for c in connections
        ]
    
    def get_incoming_connections(self, obj):
        """Get incoming phase connections"""
        connections = obj.incoming_connections.filter(is_active=True)
        return [
            {
                'from_phase_id': c.from_phase.phase_id,
                'from_phase_name': c.from_phase.name,
                'flow_type': c.flow_type,
                'trigger_type': c.trigger_type,
            }
            for c in connections
        ]
    
    def get_recent_events(self, obj):
        """Get recent events from this phase"""
        events = UnifiedEvent.objects.filter(
            source_phase=obj
        ).order_by('-created_at')[:5]
        
        return [
            {
                'event_type': e.event_type,
                'status': e.status,
                'created_at': e.created_at.isoformat(),
            }
            for e in events
        ]


# ============================================================================
# UNIFIED EVENT SERIALIZERS
# ============================================================================

class UnifiedEventSerializer(serializers.ModelSerializer):
    """Serializer for UnifiedEvent model"""
    
    source_phase_name = serializers.CharField(
        source='source_phase.name',
        read_only=True
    )
    target_phase_names = serializers.SerializerMethodField()
    
    class Meta:
        model = UnifiedEvent
        fields = [
            'event_id',
            'event_type',
            'source_phase',
            'source_phase_name',
            'target_phases',
            'target_phase_names',
            'status',
            'data',
            'created_at',
            'processed_at',
        ]
        read_only_fields = ['event_id', 'created_at', 'processed_at']
    
    def get_target_phase_names(self, obj):
        """Get names of target phases"""
        return [phase.name for phase in obj.target_phases.all()]


class UnifiedEventCreateSerializer(serializers.Serializer):
    """Serializer for creating events"""
    
    event_type = serializers.CharField(max_length=100)
    data = serializers.JSONField(required=False, default=dict)
    target_phases = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate_event_type(self, value):
        """Validate event type"""
        valid_types = [
            'low_stock_alert',
            'donation_received',
            'distribution_scheduled',
            'error_detected',
            'recovery_action',
            'prediction_available',
        ]
        if value not in valid_types:
            raise serializers.ValidationError(
                f'Event type must be one of: {", ".join(valid_types)}'
            )
        return value


class UnifiedEventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for UnifiedEvent"""
    
    source_phase_details = UnifiedPhaseSerializer(
        source='source_phase',
        read_only=True
    )
    target_phase_details = UnifiedPhaseSerializer(
        source='target_phases',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = UnifiedEvent
        fields = [
            'event_id',
            'event_type',
            'source_phase',
            'source_phase_details',
            'target_phases',
            'target_phase_details',
            'status',
            'data',
            'created_at',
            'processed_at',
        ]
        read_only_fields = ['event_id', 'created_at', 'processed_at']


# ============================================================================
# PHASE CONNECTION SERIALIZERS
# ============================================================================

class PhaseConnectionSerializer(serializers.ModelSerializer):
    """Serializer for PhaseConnection model"""
    
    from_phase_name = serializers.CharField(
        source='from_phase.name',
        read_only=True
    )
    to_phase_name = serializers.CharField(
        source='to_phase.name',
        read_only=True
    )
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = PhaseConnection
        fields = [
            'connection_id',
            'from_phase',
            'from_phase_name',
            'to_phase',
            'to_phase_name',
            'flow_type',
            'trigger_type',
            'is_active',
            'success_count',
            'failure_count',
            'success_rate',
            'created_at',
        ]
        read_only_fields = [
            'connection_id',
            'success_count',
            'failure_count',
            'created_at',
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        total = obj.success_count + obj.failure_count
        if total == 0:
            return 100.0
        return (obj.success_count / total) * 100


class PhaseConnectionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PhaseConnection"""
    
    from_phase = UnifiedPhaseSerializer(read_only=True)
    to_phase = UnifiedPhaseSerializer(read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = PhaseConnection
        fields = [
            'connection_id',
            'from_phase',
            'to_phase',
            'flow_type',
            'trigger_type',
            'is_active',
            'success_count',
            'failure_count',
            'success_rate',
            'max_retries',
            'timeout_seconds',
            'created_at',
        ]
        read_only_fields = [
            'connection_id',
            'success_count',
            'failure_count',
            'created_at',
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        total = obj.success_count + obj.failure_count
        if total == 0:
            return 100.0
        return (obj.success_count / total) * 100


# ============================================================================
# UNIFIED SYSTEM SERIALIZERS
# ============================================================================

class UnifiedSystemStateSerializer(serializers.ModelSerializer):
    """Serializer for UnifiedSystemState model"""
    
    class Meta:
        model = UnifiedSystemState
        fields = [
            'system_state_id',
            'total_events_processed',
            'total_events_failed',
            'active_phases',
            'average_event_processing_time_ms',
            'is_healthy',
            'last_health_check',
            'updated_at',
        ]
        read_only_fields = [
            'system_state_id',
            'total_events_processed',
            'total_events_failed',
            'active_phases',
            'average_event_processing_time_ms',
            'last_health_check',
            'updated_at',
        ]


class PhaseDataTransformSerializer(serializers.ModelSerializer):
    """Serializer for PhaseDataTransform model"""
    
    class Meta:
        model = PhaseDataTransform
        fields = [
            'transform_id',
            'from_phase',
            'to_phase',
            'source_field',
            'target_field',
            'transformation_logic',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['transform_id', 'created_at']


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class BulkEventEmitSerializer(serializers.Serializer):
    """Serializer for bulk event emission"""
    
    events = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate_events(self, value):
        """Validate events list"""
        if not value:
            raise serializers.ValidationError('Events list cannot be empty')
        if len(value) > 100:
            raise serializers.ValidationError('Maximum 100 events per request')
        return value


class PhaseConnectionNetworkSerializer(serializers.Serializer):
    """Serializer for phase connection network visualization"""
    
    phases = serializers.ListField(
        child=serializers.DictField()
    )
    connections = serializers.ListField(
        child=serializers.DictField()
    )


# ============================================================================
# STATUS AND HEALTH SERIALIZERS
# ============================================================================

class PhaseHealthStatusSerializer(serializers.Serializer):
    """Serializer for phase health status"""
    
    phase_id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    uptime_percentage = serializers.FloatField()
    error_rate = serializers.FloatField()
    response_time_ms = serializers.FloatField()
    total_events_processed = serializers.IntegerField()
    total_events_failed = serializers.IntegerField()


class SystemHealthReportSerializer(serializers.Serializer):
    """Serializer for complete system health report"""
    
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    overall_uptime = serializers.FloatField()
    overall_error_rate = serializers.FloatField()
    active_phases = serializers.IntegerField()
    total_phases = serializers.IntegerField()
    total_events = serializers.IntegerField()
    failed_events = serializers.IntegerField()
    total_connections = serializers.IntegerField()
    phase_statuses = PhaseHealthStatusSerializer(many=True)


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for unified dashboard data"""
    
    timestamp = serializers.DateTimeField()
    title = serializers.CharField()
    phases = serializers.DictField()
    recent_events = serializers.ListField()
    system_metrics = serializers.DictField()
