"""
ML PREDICTION SERIALIZERS
==========================
DRF serializers for converting between Python objects and JSON
for ML prediction API endpoints.
"""

from rest_framework import serializers
from django.utils import timezone

from .models import (
    MLModel, ModelFeature, ErrorPrediction, AnomalyDetection,
    TimeSeriesForecast, RootCauseAnalysis, PreventiveAction,
    AIInsight, PredictionFeedback, ModelTrainingHistory,
    ModelEvaluationMetrics, MLPipelineLog, ModelPerformanceTracking
)


# ============================================================================
# ML MODEL SERIALIZERS
# ============================================================================

class ModelFeatureSerializer(serializers.ModelSerializer):
    """Serializer for model features."""
    
    class Meta:
        model = ModelFeature
        fields = [
            'feature_id', 'feature_name', 'feature_type', 'importance_score',
            'description', 'extraction_method', 'scaling_type',
            'min_value', 'max_value', 'mean_value', 'std_deviation'
        ]
        read_only_fields = ['feature_id', 'created_at']


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for ML models."""
    
    features = ModelFeatureSerializer(many=True, read_only=True)
    performance_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = MLModel
        fields = [
            'model_id', 'model_name', 'model_type', 'service', 'framework',
            'model_algorithm', 'version', 'status', 'accuracy', 'precision',
            'recall', 'f1_score', 'mape', 'rmse', 'model_path', 'config',
            'training_samples_count', 'features_count', 'last_trained_at',
            'last_evaluated_at', 'created_at', 'updated_at', 'created_by',
            'updated_by', 'features', 'performance_summary'
        ]
        read_only_fields = ['model_id', 'created_at', 'updated_at']
    
    def get_performance_summary(self, obj):
        """Get performance summary for the model."""
        return obj.get_performance_summary()


class ModelTrainingHistorySerializer(serializers.ModelSerializer):
    """Serializer for model training history."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelTrainingHistory
        fields = [
            'training_id', 'model', 'model_name', 'training_start_time',
            'training_end_time', 'training_duration_seconds', 'duration_formatted',
            'training_samples_count', 'training_data_source', 'data_period_from',
            'data_period_to', 'train_loss', 'val_loss', 'train_accuracy',
            'val_accuracy', 'final_accuracy', 'final_precision', 'final_recall',
            'final_f1', 'hyperparameters', 'training_config', 'issues_encountered',
            'notes', 'status', 'failure_reason', 'trained_by', 'created_at'
        ]
        read_only_fields = ['training_id', 'created_at']
    
    def get_duration_formatted(self, obj):
        """Format training duration as human-readable string."""
        if obj.training_duration_seconds:
            hours = obj.training_duration_seconds // 3600
            minutes = (obj.training_duration_seconds % 3600) // 60
            seconds = obj.training_duration_seconds % 60
            return f"{hours}h {minutes}m {seconds}s"
        return None


class ModelEvaluationMetricsSerializer(serializers.ModelSerializer):
    """Serializer for model evaluation metrics."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    
    class Meta:
        model = ModelEvaluationMetrics
        fields = [
            'metric_id', 'model', 'model_name', 'accuracy', 'precision', 'recall',
            'f1_score', 'roc_auc', 'pr_auc', 'mse', 'rmse', 'mae', 'mape',
            'r2_score', 'per_category_metrics', 'confusion_matrix',
            'evaluation_dataset', 'evaluation_period_from', 'evaluation_period_to',
            'evaluation_samples_count', 'evaluated_at', 'created_at'
        ]
        read_only_fields = ['metric_id', 'created_at']


# ============================================================================
# PREDICTION & ANOMALY SERIALIZERS
# ============================================================================

class ErrorPredictionSerializer(serializers.ModelSerializer):
    """Serializer for error predictions."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    time_until_predicted = serializers.SerializerMethodField()
    is_urgent = serializers.SerializerMethodField()
    
    class Meta:
        model = ErrorPrediction
        fields = [
            'prediction_id', 'model', 'model_name', 'service',
            'predicted_error_type', 'predicted_severity', 'probability',
            'probability_threshold', 'time_horizon_minutes', 'predicted_timestamp',
            'time_until_predicted', 'is_urgent', 'contributing_factors',
            'affected_endpoints', 'affected_users_count', 'business_impact',
            'recommended_actions', 'alert_triggered', 'alert_sent_at',
            'actual_error_occurred', 'actual_error_id', 'actual_error_timestamp',
            'prediction_accuracy', 'created_at', 'updated_at'
        ]
        read_only_fields = ['prediction_id', 'created_at', 'updated_at']
    
    def get_time_until_predicted(self, obj):
        """Calculate time until predicted error."""
        delta = obj.predicted_timestamp - timezone.now()
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        return "< 1m"
    
    def get_is_urgent(self, obj):
        """Check if prediction is urgent."""
        return (
            float(obj.probability) >= 0.8 and
            obj.time_horizon_minutes <= 60
        )


class AnomalyDetectionSerializer(serializers.ModelSerializer):
    """Serializer for anomaly detection results."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    hours_since_detection = serializers.SerializerMethodField()
    requires_attention = serializers.SerializerMethodField()
    
    class Meta:
        model = AnomalyDetection
        fields = [
            'anomaly_id', 'error_id', 'model', 'model_name', 'service',
            'anomaly_score', 'is_anomaly', 'anomaly_type', 'severity_level',
            'expected_behavior', 'actual_behavior', 'deviation_percentage',
            'confidence', 'context_data', 'root_cause_hypothesis',
            'recommended_action', 'detected_at', 'hours_since_detection',
            'acknowledged', 'acknowledged_by', 'acknowledged_at',
            'false_positive', 'false_positive_reported_by',
            'false_positive_reported_at', 'requires_attention',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['anomaly_id', 'created_at', 'updated_at']
    
    def get_hours_since_detection(self, obj):
        """Calculate hours since detection."""
        delta = timezone.now() - obj.detected_at
        hours = int(delta.total_seconds() // 3600)
        return hours
    
    def get_requires_attention(self, obj):
        """Check if anomaly requires immediate attention."""
        return (
            not obj.acknowledged and
            obj.severity_level in ['high', 'critical']
        )


# ============================================================================
# FORECAST & ANALYSIS SERIALIZERS
# ============================================================================

class TimeSeriesForecastSerializer(serializers.ModelSerializer):
    """Serializer for time series forecasts."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    forecast_accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSeriesForecast
        fields = [
            'forecast_id', 'model', 'model_name', 'service', 'metric_name',
            'forecast_horizon_hours', 'forecast_period_minutes', 'forecast_values',
            'forecast_trend', 'trend_confidence', 'mae', 'rmse', 'mape',
            'peak_value', 'peak_at_timestamp', 'min_value', 'min_at_timestamp',
            'exceeds_threshold', 'threshold_value', 'forecast_accuracy',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['forecast_id', 'created_at', 'updated_at']
    
    def get_forecast_accuracy(self, obj):
        """Get forecast accuracy assessment."""
        if obj.mape:
            mape_float = float(obj.mape)
            if mape_float < 5:
                return 'excellent'
            elif mape_float < 15:
                return 'good'
            elif mape_float < 30:
                return 'fair'
            else:
                return 'poor'
        return 'unknown'


class RootCauseAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for root cause analysis."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    
    class Meta:
        model = RootCauseAnalysis
        fields = [
            'analysis_id', 'error_id', 'model', 'model_name', 'error_type',
            'error_service', 'probable_causes', 'most_likely_cause',
            'confidence_score', 'contributing_factors', 'environmental_factors',
            'code_factors', 'infrastructure_factors', 'similar_error_ids',
            'pattern_match_score', 'recommended_actions', 'resolution_steps',
            'similar_patterns_found', 'previous_occurrence_count',
            'resolution_success_rate', 'analysis_created_at', 'analysis_updated_at',
            'analyzed_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['analysis_id', 'created_at', 'updated_at']


# ============================================================================
# ACTION & INSIGHT SERIALIZERS
# ============================================================================

class PreventiveActionSerializer(serializers.ModelSerializer):
    """Serializer for preventive actions."""
    
    prediction_error_type = serializers.CharField(
        source='prediction.predicted_error_type',
        read_only=True
    )
    execution_result_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = PreventiveAction
        fields = [
            'action_id', 'prediction', 'anomaly', 'action_type', 'priority',
            'estimated_impact', 'implementation_difficulty', 'implementation_time_seconds',
            'can_be_automated', 'automation_script_available', 'automation_script_path',
            'status', 'executed_at', 'executed_by', 'execution_result',
            'execution_result_formatted', 'prediction_error_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['action_id', 'created_at', 'updated_at']
    
    def get_execution_result_formatted(self, obj):
        """Format execution result for display."""
        if obj.execution_result:
            success = obj.execution_result.get('success', False)
            return {
                'success': success,
                'duration_seconds': obj.execution_result.get('duration'),
                'impact_observed': obj.execution_result.get('impact_observed'),
            }
        return None


class AIInsightSerializer(serializers.ModelSerializer):
    """Serializer for AI insights."""
    
    days_active = serializers.SerializerMethodField()
    
    class Meta:
        model = AIInsight
        fields = [
            'insight_id', 'service', 'insight_type', 'title', 'description',
            'severity', 'supporting_data', 'evidence', 'confidence_level',
            'recommended_actions', 'estimated_impact', 'effort_to_fix', 'status',
            'assigned_to', 'resolved_at', 'resolution_notes', 'expires_at',
            'days_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['insight_id', 'created_at', 'updated_at']
    
    def get_days_active(self, obj):
        """Calculate days active."""
        delta = timezone.now() - obj.created_at
        return delta.days


class PredictionFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for prediction feedback."""
    
    prediction_details = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionFeedback
        fields = [
            'feedback_id', 'prediction', 'anomaly', 'feedback_type',
            'feedback_score', 'feedback_text', 'provided_by', 'provided_at',
            'model_retrained', 'retrain_recommended', 'prediction_details',
            'created_at'
        ]
        read_only_fields = ['feedback_id', 'created_at']
    
    def get_prediction_details(self, obj):
        """Get prediction details if available."""
        if obj.prediction:
            return {
                'error_type': obj.prediction.predicted_error_type,
                'probability': float(obj.prediction.probability),
                'service': obj.prediction.service,
            }
        return None


# ============================================================================
# LOGGING & TRACKING SERIALIZERS
# ============================================================================

class MLPipelineLogSerializer(serializers.ModelSerializer):
    """Serializer for ML pipeline logs."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = MLPipelineLog
        fields = [
            'log_id', 'pipeline_name', 'pipeline_stage', 'model', 'model_name',
            'status', 'start_time', 'end_time', 'duration_seconds',
            'duration_formatted', 'input_data_size_mb', 'samples_processed',
            'output_records', 'error_message', 'warning_messages', 'metrics',
            'logs', 'created_at'
        ]
        read_only_fields = ['log_id', 'created_at']
    
    def get_duration_formatted(self, obj):
        """Format duration as readable string."""
        if obj.duration_seconds:
            return f"{obj.duration_seconds}s"
        return None


class ModelPerformanceTrackingSerializer(serializers.ModelSerializer):
    """Serializer for model performance tracking."""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    
    class Meta:
        model = ModelPerformanceTracking
        fields = [
            'tracking_id', 'model', 'model_name', 'tracking_date',
            'predictions_made', 'predictions_correct', 'accuracy_today',
            'anomalies_detected', 'true_positives', 'false_positives',
            'true_negative_rate', 'false_positive_rate', 'forecast_errors',
            'forecast_mae', 'forecast_mape', 'errors_prevented',
            'cost_savings_estimated', 'user_impact_prevented', 'notes',
            'created_at'
        ]
        read_only_fields = ['tracking_id', 'created_at']


# ============================================================================
# SUMMARY SERIALIZERS
# ============================================================================

class ModelPerformanceSummarySerializer(serializers.Serializer):
    """Serializer for model performance summary."""
    
    model_id = serializers.UUIDField()
    model_name = serializers.CharField()
    service = serializers.CharField()
    current_metrics = serializers.DictField()
    latest_evaluation = serializers.DictField()
    recent_trend = serializers.ListField()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary."""
    
    timestamp = serializers.DateTimeField()
    health_score = serializers.IntegerField()
    predictions = serializers.DictField()
    anomalies = serializers.DictField()
    models = serializers.DictField()
    recent_activity = serializers.DictField()


# ============================================================================
# NESTED SERIALIZERS FOR COMPLEX RESPONSES
# ============================================================================

class PredictionWithActionsSerializer(ErrorPredictionSerializer):
    """Extended serializer including recommended preventive actions."""
    
    recommended_actions = PreventiveActionSerializer(
        source='preventive_actions',
        many=True,
        read_only=True
    )
    
    class Meta(ErrorPredictionSerializer.Meta):
        fields = ErrorPredictionSerializer.Meta.fields + ['recommended_actions']


class AnomalyWithAnalysisSerializer(AnomalyDetectionSerializer):
    """Extended serializer including root cause analysis."""
    
    root_cause_analysis = serializers.SerializerMethodField()
    
    class Meta(AnomalyDetectionSerializer.Meta):
        fields = AnomalyDetectionSerializer.Meta.fields + ['root_cause_analysis']
    
    def get_root_cause_analysis(self, obj):
        """Get related root cause analysis."""
        analysis = RootCauseAnalysis.objects.filter(
            error_id=obj.error_id
        ).first()
        
        if analysis:
            return RootCauseAnalysisSerializer(analysis).data
        return None
