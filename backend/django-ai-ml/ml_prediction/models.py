"""
AI ERROR PREDICTION MODELS
===========================
Django models for ML-based error prediction, anomaly detection, and
automatic error prevention system for Feeding Hearts platform.

This module defines the ORM models for storing:
- ML model definitions and versions
- Anomaly detection results
- Error predictions with confidence scores
- Time series forecasts
- Training history and metrics
- Feedback for model improvement
- Root cause analysis results
- Preventive action recommendations
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================================
# BASE ABSTRACT MODELS
# ============================================================================

class TimestampedModel(models.Model):
    """Abstract base model with timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(TimestampedModel):
    """Abstract model with audit trail."""
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


# ============================================================================
# ML MODEL DEFINITIONS
# ============================================================================

class MLModel(AuditedModel):
    """
    Registry of all ML models with metadata and performance metrics.
    Tracks different model versions, algorithms, and their performance.
    """

    MODEL_TYPES = [
        ('anomaly_detection', 'Anomaly Detection'),
        ('time_series_forecast', 'Time Series Forecasting'),
        ('error_classifier', 'Error Classifier'),
        ('severity_predictor', 'Severity Predictor'),
        ('pattern_detector', 'Pattern Detector'),
        ('root_cause_analyzer', 'Root Cause Analyzer'),
    ]

    STATUSES = [
        ('training', 'Training'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    SERVICES = [
        ('django', 'Django'),
        ('laravel', 'Laravel'),
        ('java', 'Java'),
        ('react', 'React'),
        ('angular', 'Angular'),
        ('vue', 'Vue'),
        ('flutter', 'Flutter'),
        ('system', 'System-wide'),
    ]

    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=255, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    service = models.CharField(max_length=50, choices=SERVICES)
    framework = models.CharField(max_length=255, blank=True)
    model_algorithm = models.CharField(max_length=100)
    version = models.CharField(max_length=20, default='1.0.0')
    
    status = models.CharField(max_length=20, choices=STATUSES, default='training')
    
    # Performance metrics (0.0 to 1.0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(1)])
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                   validators=[MinValueValidator(0), MaxValueValidator(1)])
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                validators=[MinValueValidator(0), MaxValueValidator(1)])
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                  validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Forecast-specific metrics
    mape = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)  # Mean Absolute Percentage Error
    rmse = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Root Mean Squared Error
    
    model_path = models.CharField(max_length=500, blank=True)  # Path to serialized model
    config = JSONField(default=dict, blank=True)  # Hyperparameters
    
    training_samples_count = models.IntegerField(null=True, blank=True)
    features_count = models.IntegerField(null=True, blank=True)
    
    last_trained_at = models.DateTimeField(null=True, blank=True)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_models.ml_models'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['service', 'model_type']),
            models.Index(fields=['status']),
            models.Index(fields=['service', 'status']),
        ]

    def __str__(self):
        return f"{self.model_name} v{self.version} ({self.status})"

    def is_active(self):
        return self.status == 'active'

    def get_performance_summary(self):
        return {
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'precision': float(self.precision) if self.precision else None,
            'recall': float(self.recall) if self.recall else None,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'last_trained': self.last_trained_at.isoformat() if self.last_trained_at else None,
        }


class ModelFeature(TimestampedModel):
    """
    Features used in ML models with importance scores.
    Tracks feature engineering and importance for interpretability.
    """

    FEATURE_TYPES = [
        ('numeric', 'Numeric'),
        ('categorical', 'Categorical'),
        ('boolean', 'Boolean'),
        ('timestamp', 'Timestamp'),
        ('text', 'Text'),
    ]

    feature_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='features')
    
    feature_name = models.CharField(max_length=255)
    feature_type = models.CharField(max_length=50, choices=FEATURE_TYPES)
    importance_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                          validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    description = models.TextField(blank=True)
    extraction_method = models.CharField(max_length=255, blank=True)
    scaling_type = models.CharField(max_length=50, blank=True)  # normalization, standardization, etc
    
    # Statistics
    min_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    mean_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    std_deviation = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'ai_models.model_features'
        ordering = ['-importance_score', 'feature_name']
        unique_together = ['model', 'feature_name']
        indexes = [
            models.Index(fields=['model', '-importance_score']),
        ]

    def __str__(self):
        return f"{self.model.model_name} - {self.feature_name}"


# ============================================================================
# ANOMALY DETECTION RESULTS
# ============================================================================

class AnomalyDetection(TimestampedModel):
    """
    Results from anomaly detection models identifying unusual error patterns.
    Identifies deviations from normal behavior and severity assessment.
    """

    ANOMALY_TYPES = [
        ('spike', 'Error Rate Spike'),
        ('drop', 'Unexpected Drop'),
        ('trend_change', 'Trend Change'),
        ('pattern_deviation', 'Pattern Deviation'),
        ('correlation_break', 'Correlation Break'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    anomaly_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    error_id = models.CharField(max_length=255, blank=True, null=True)  # Link to error_logging
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    service = models.CharField(max_length=50)
    anomaly_score = models.DecimalField(max_digits=10, decimal_places=4,
                                       validators=[MinValueValidator(0), MaxValueValidator(1)])
    is_anomaly = models.BooleanField(default=False)
    
    anomaly_type = models.CharField(max_length=100, choices=ANOMALY_TYPES, blank=True)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    expected_behavior = JSONField(default=dict, blank=True)
    actual_behavior = JSONField(default=dict, blank=True)
    deviation_percentage = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    
    confidence = models.DecimalField(max_digits=5, decimal_places=4,
                                    validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    context_data = JSONField(default=dict, blank=True)
    root_cause_hypothesis = models.TextField(blank=True)
    recommended_action = models.CharField(max_length=500, blank=True)
    
    detected_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Acknowledgment
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.CharField(max_length=255, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Feedback
    false_positive = models.BooleanField(null=True, blank=True)
    false_positive_reported_by = models.CharField(max_length=255, blank=True)
    false_positive_reported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_models.anomaly_detections'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['service', 'severity_level']),
            models.Index(fields=['-detected_at']),
            models.Index(fields=['is_anomaly']),
            models.Index(fields=['-anomaly_score']),
        ]

    def __str__(self):
        return f"Anomaly {self.anomaly_id} - {self.service} ({self.severity_level})"

    def acknowledge(self, user_id):
        """Mark anomaly as acknowledged."""
        self.acknowledged = True
        self.acknowledged_by = user_id
        self.acknowledged_at = timezone.now()
        self.save()


# ============================================================================
# ERROR PREDICTIONS
# ============================================================================

class ErrorPrediction(TimestampedModel):
    """
    Predictions of future errors with probability and recommendations.
    Proactively identifies errors before they occur with time estimates.
    """

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    prediction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    service = models.CharField(max_length=50, db_index=True)
    predicted_error_type = models.CharField(max_length=255)
    predicted_severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    # Probability and confidence
    probability = models.DecimalField(max_digits=5, decimal_places=4,
                                     validators=[MinValueValidator(0), MaxValueValidator(1)],
                                     db_index=True)
    probability_threshold = models.DecimalField(max_digits=5, decimal_places=4,
                                               validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Timeframe
    time_horizon_minutes = models.IntegerField()  # Minutes until predicted error
    predicted_timestamp = models.DateTimeField(db_index=True)
    
    # Analysis
    contributing_factors = JSONField(default=dict)  # Top factors in prediction
    affected_endpoints = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    affected_users_count = models.IntegerField(null=True, blank=True)
    business_impact = models.TextField(blank=True)
    recommended_actions = JSONField(default=list)  # Array of recommended actions
    
    # Alerting
    alert_triggered = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Validation
    actual_error_occurred = models.BooleanField(null=True, blank=True)
    actual_error_id = models.CharField(max_length=255, blank=True)
    actual_error_timestamp = models.DateTimeField(null=True, blank=True)
    prediction_accuracy = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'ai_models.error_predictions'
        ordering = ['-probability', 'predicted_timestamp']
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['-probability']),
            models.Index(fields=['predicted_timestamp']),
        ]

    def __str__(self):
        return f"Prediction: {self.predicted_error_type} ({self.probability})"

    def trigger_alert(self):
        """Mark prediction alert as triggered."""
        self.alert_triggered = True
        self.alert_sent_at = timezone.now()
        self.save()

    def mark_occurred(self, error_id, timestamp=None):
        """Record that the predicted error actually occurred."""
        self.actual_error_occurred = True
        self.actual_error_id = error_id
        self.actual_error_timestamp = timestamp or timezone.now()
        self.prediction_accuracy = True
        self.save()


# ============================================================================
# TIME SERIES FORECASTS
# ============================================================================

class TimeSeriesForecast(AuditedModel):
    """
    Time-series forecasts for system metrics (error rates, response times, etc).
    Predicts trends and capacity requirements.
    """

    forecast_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    service = models.CharField(max_length=50, db_index=True)
    metric_name = models.CharField(max_length=255)  # errors_per_minute, response_time, etc
    
    forecast_horizon_hours = models.IntegerField(default=24)
    forecast_period_minutes = models.IntegerField()  # Granularity: 15min, 1hour, etc
    
    # Forecast values
    forecast_values = JSONField(default=dict)  # {timestamp, value, confidence_lower, confidence_upper}
    forecast_trend = models.CharField(max_length=50, blank=True)  # increasing, decreasing, stable
    trend_confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Performance metrics
    mae = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)  # Mean Absolute Error
    rmse = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)  # Root Mean Squared Error
    mape = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)  # Mean Absolute Percentage Error
    
    # Risk assessment
    peak_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    peak_at_timestamp = models.DateTimeField(null=True, blank=True)
    min_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    min_at_timestamp = models.DateTimeField(null=True, blank=True)
    
    exceeds_threshold = models.BooleanField(default=False)
    threshold_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'ai_models.time_series_forecasts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service', 'metric_name']),
            models.Index(fields=['peak_at_timestamp']),
        ]

    def __str__(self):
        return f"{self.service} - {self.metric_name} forecast"


# ============================================================================
# MODEL TRAINING HISTORY
# ============================================================================

class ModelTrainingHistory(AuditedModel):
    """
    Complete training history for model reproducibility and auditing.
    Tracks all model training runs with metrics and logs.
    """

    STATUSES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    training_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_history')
    
    training_start_time = models.DateTimeField(default=timezone.now)
    training_end_time = models.DateTimeField(null=True, blank=True)
    training_duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Training data info
    training_samples_count = models.IntegerField()
    training_data_source = models.CharField(max_length=255)  # error_logs, metrics_db, etc
    data_period_from = models.DateTimeField()
    data_period_to = models.DateTimeField()
    
    # Model performance
    train_loss = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    val_loss = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    train_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    val_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    final_accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    final_precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    final_recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    final_f1 = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Training details
    hyperparameters = JSONField(default=dict)
    training_config = JSONField(default=dict)
    issues_encountered = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUSES, db_index=True)
    failure_reason = models.TextField(blank=True)
    trained_by = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'ai_models.model_training_history'
        ordering = ['-training_end_time']
        indexes = [
            models.Index(fields=['model', '-training_end_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.model.model_name} - Training {self.training_start_time.date()}"

    def mark_complete(self, duration_seconds, final_metrics=None):
        """Mark training as completed."""
        self.training_end_time = timezone.now()
        self.training_duration_seconds = duration_seconds
        self.status = 'completed'
        
        if final_metrics:
            self.final_accuracy = final_metrics.get('accuracy')
            self.final_precision = final_metrics.get('precision')
            self.final_recall = final_metrics.get('recall')
            self.final_f1 = final_metrics.get('f1_score')
        
        self.save()


# ============================================================================
# MODEL EVALUATION METRICS
# ============================================================================

class ModelEvaluationMetrics(TimestampedModel):
    """
    Performance metrics for model evaluation and validation.
    Tracks accuracy, precision, recall, and other statistical measures.
    """

    metric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='evaluation_metrics')
    training = models.ForeignKey(ModelTrainingHistory, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='metrics')
    
    # Classification metrics
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    roc_auc = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    pr_auc = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Regression metrics
    mse = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    rmse = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    mae = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    mape = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    r2_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Per-category metrics
    per_category_metrics = JSONField(default=dict)
    confusion_matrix = JSONField(default=dict)
    
    evaluation_dataset = models.CharField(max_length=255, blank=True)
    evaluation_period_from = models.DateTimeField(null=True, blank=True)
    evaluation_period_to = models.DateTimeField(null=True, blank=True)
    evaluation_samples_count = models.IntegerField(null=True, blank=True)
    
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_models.model_evaluation_metrics'
        ordering = ['-evaluated_at']

    def __str__(self):
        return f"Metrics for {self.model.model_name}"


# ============================================================================
# PREDICTION FEEDBACK
# ============================================================================

class PredictionFeedback(TimestampedModel):
    """
    Feedback on predictions for continuous model improvement.
    Implements feedback loop for model refinement.
    """

    FEEDBACK_TYPES = [
        ('true_positive', 'True Positive'),
        ('false_positive', 'False Positive'),
        ('false_negative', 'False Negative'),
        ('early_warning_correct', 'Early Warning Correct'),
        ('severity_mismatch', 'Severity Mismatch'),
        ('useful', 'Useful Prediction'),
        ('actionable', 'Actionable'),
        ('irrelevant', 'Irrelevant'),
    ]

    feedback_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.ForeignKey(ErrorPrediction, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='feedback')
    anomaly = models.ForeignKey(AnomalyDetection, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='feedback')
    
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    feedback_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_text = models.TextField(blank=True)
    provided_by = models.CharField(max_length=255)
    provided_at = models.DateTimeField(default=timezone.now)
    
    # Impact
    model_retrained = models.BooleanField(default=False)
    retrain_recommended = models.BooleanField(default=False)

    class Meta:
        db_table = 'ai_models.prediction_feedback'
        ordering = ['-provided_at']
        indexes = [
            models.Index(fields=['feedback_type']),
        ]

    def __str__(self):
        return f"Feedback: {self.feedback_type} ({self.feedback_score}/5)"


# ============================================================================
# ROOT CAUSE ANALYSIS
# ============================================================================

class RootCauseAnalysis(AuditedModel):
    """
    Root cause analysis results identifying probable causes of errors.
    Provides actionable insights and similar pattern matching.
    """

    analysis_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    error_id = models.CharField(max_length=255, blank=True)  # Link to error_logging
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL,
                             null=True, blank=True)
    
    error_type = models.CharField(max_length=255)
    error_service = models.CharField(max_length=50)
    
    # Root cause detection
    probable_causes = JSONField(default=list)  # [{cause, probability, confidence}]
    most_likely_cause = models.CharField(max_length=500, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4)
    
    # Contributing factors
    contributing_factors = JSONField(default=dict)  # {factor_name, impact_score, evidence}
    environmental_factors = models.TextField(blank=True)
    code_factors = models.TextField(blank=True)
    infrastructure_factors = models.TextField(blank=True)
    
    # Similar errors
    similar_error_ids = ArrayField(models.CharField(max_length=255), default=list)
    pattern_match_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Recommendations
    recommended_actions = JSONField(default=list)
    resolution_steps = models.TextField(blank=True)
    
    # Historical
    similar_patterns_found = models.BooleanField(default=False)
    previous_occurrence_count = models.IntegerField(default=0)
    resolution_success_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    analysis_created_at = models.DateTimeField(default=timezone.now)
    analysis_updated_at = models.DateTimeField(auto_now=True)
    analyzed_by = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'ai_models.root_cause_analysis'
        ordering = ['-analysis_created_at']
        indexes = [
            models.Index(fields=['error_service']),
            models.Index(fields=['-confidence_score']),
        ]

    def __str__(self):
        return f"RCA: {self.error_type} - {self.most_likely_cause}"


# ============================================================================
# PREVENTIVE ACTIONS
# ============================================================================

class PreventiveAction(TimestampedModel):
    """
    Recommended and executed preventive actions triggered by AI insights.
    Tracks automation capability and execution results.
    """

    ACTION_TYPES = [
        ('scale_up_resources', 'Scale Up Resources'),
        ('preemptive_restart', 'Preemptive Restart'),
        ('connection_pool_increase', 'Increase Connection Pool'),
        ('cache_clear', 'Clear Cache'),
        ('database_optimization', 'Database Optimization'),
        ('code_patch', 'Apply Code Patch'),
        ('traffic_reroute', 'Reroute Traffic'),
        ('health_check_increase', 'Increase Health Checks'),
        ('monitoring_alert', 'Send Monitoring Alert'),
        ('notify_team', 'Notify Team'),
        ('rollback_deployment', 'Rollback Deployment'),
        ('circuit_breaker_enable', 'Enable Circuit Breaker'),
        ('request_throttling', 'Request Throttling'),
        ('graceful_degradation', 'Graceful Degradation'),
        ('manual_review', 'Manual Review Required'),
    ]

    PRIORITIES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    DIFFICULTIES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    STATUSES = [
        ('recommended', 'Recommended'),
        ('manual_review', 'Manual Review'),
        ('scheduled', 'Scheduled'),
        ('executed', 'Executed'),
        ('skipped', 'Skipped'),
    ]

    action_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.ForeignKey(ErrorPrediction, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='preventive_actions')
    anomaly = models.ForeignKey(AnomalyDetection, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='preventive_actions')
    
    action_type = models.CharField(max_length=100, choices=ACTION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITIES)
    estimated_impact = models.CharField(max_length=500, blank=True)
    implementation_difficulty = models.CharField(max_length=20, choices=DIFFICULTIES)
    implementation_time_seconds = models.IntegerField(null=True, blank=True)
    
    # Automation
    can_be_automated = models.BooleanField(default=False)
    automation_script_available = models.BooleanField(default=False)
    automation_script_path = models.CharField(max_length=500, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUSES, default='recommended')
    executed_at = models.DateTimeField(null=True, blank=True)
    executed_by = models.CharField(max_length=255, blank=True)
    execution_result = JSONField(default=dict)  # {success, duration, impact_observed}

    class Meta:
        db_table = 'ai_models.preventive_actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.action_type} ({self.status})"

    def execute(self, executor_id, result_data=None):
        """Mark action as executed."""
        self.status = 'executed'
        self.executed_by = executor_id
        self.executed_at = timezone.now()
        if result_data:
            self.execution_result = result_data
        self.save()


# ============================================================================
# AI INSIGHTS & RECOMMENDATIONS
# ============================================================================

class AIInsight(AuditedModel):
    """
    High-level insights and recommendations from AI analysis.
    Provides actionable intelligence to development and operations teams.
    """

    INSIGHT_TYPES = [
        ('trend_detection', 'Trend Detection'),
        ('anomaly_pattern', 'Anomaly Pattern'),
        ('performance_degradation', 'Performance Degradation'),
        ('capacity_planning', 'Capacity Planning'),
        ('reliability_trend', 'Reliability Trend'),
        ('cost_optimization', 'Cost Optimization'),
        ('security_concern', 'Security Concern'),
        ('infrastructure_issue', 'Infrastructure Issue'),
    ]

    SEVERITIES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    STATUSES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('wont_fix', "Won't Fix"),
    ]

    insight_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.CharField(max_length=50, db_index=True)
    
    insight_type = models.CharField(max_length=100, choices=INSIGHT_TYPES, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITIES, db_index=True)
    
    # Supporting data
    supporting_data = JSONField(default=dict)
    evidence = models.TextField(blank=True)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=4)
    
    # Recommendations
    recommended_actions = JSONField(default=list)
    estimated_impact = models.TextField(blank=True)
    effort_to_fix = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUSES, db_index=True, default='new')
    assigned_to = models.CharField(max_length=255, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_models.ai_insights'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service', 'insight_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.severity})"


# ============================================================================
# ML PIPELINE EXECUTION LOG
# ============================================================================

class MLPipelineLog(TimestampedModel):
    """
    Execution logs for ML pipeline stages (training, prediction, etc).
    Enables monitoring and debugging of ML operations.
    """

    STAGES = [
        ('data_preparation', 'Data Preparation'),
        ('feature_engineering', 'Feature Engineering'),
        ('model_training', 'Model Training'),
        ('model_evaluation', 'Model Evaluation'),
        ('anomaly_detection', 'Anomaly Detection'),
        ('prediction', 'Prediction'),
        ('forecast', 'Forecast'),
        ('root_cause_analysis', 'Root Cause Analysis'),
    ]

    STATUSES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('warning', 'Warning'),
    ]

    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline_name = models.CharField(max_length=255)
    pipeline_stage = models.CharField(max_length=100, choices=STAGES, blank=True)
    model = models.ForeignKey(MLModel, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='pipeline_logs')
    
    status = models.CharField(max_length=20, choices=STATUSES)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    input_data_size_mb = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    samples_processed = models.IntegerField(null=True, blank=True)
    output_records = models.IntegerField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    warning_messages = ArrayField(models.TextField(), default=list)
    
    metrics = JSONField(default=dict)
    logs = models.TextField(blank=True)

    class Meta:
        db_table = 'ai_models.ml_pipeline_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['pipeline_stage']),
        ]

    def __str__(self):
        return f"{self.pipeline_name} - {self.status}"


# ============================================================================
# MODEL PERFORMANCE TRACKING
# ============================================================================

class ModelPerformanceTracking(TimestampedModel):
    """
    Daily performance metrics for models to track accuracy and effectiveness.
    Enables trend analysis and performance degradation detection.
    """

    tracking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='performance_tracking')
    
    tracking_date = models.DateField(db_index=True)
    
    # Prediction accuracy
    predictions_made = models.IntegerField(default=0)
    predictions_correct = models.IntegerField(default=0)
    accuracy_today = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Anomaly detection
    anomalies_detected = models.IntegerField(default=0)
    true_positives = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    true_negative_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    false_positive_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Forecast accuracy
    forecast_errors = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    forecast_mae = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    forecast_mape = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    
    # Business impact
    errors_prevented = models.IntegerField(default=0)
    cost_savings_estimated = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    user_impact_prevented = models.IntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'ai_models.model_performance_tracking'
        ordering = ['-tracking_date']
        unique_together = ['model', 'tracking_date']
        indexes = [
            models.Index(fields=['model', '-tracking_date']),
        ]

    def __str__(self):
        return f"{self.model.model_name} - {self.tracking_date}"


# ============================================================================
# SIGNAL DEFINITIONS FOR DJANGO SIGNALS
# ============================================================================

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ModelTrainingHistory)
def on_training_completed(sender, instance, created, **kwargs):
    """Signal when model training is completed."""
    if instance.status == 'completed' and instance.model:
        instance.model.last_trained_at = instance.training_end_time
        instance.model.training_samples_count = instance.training_samples_count
        instance.model.save()


@receiver(post_save, sender=ErrorPrediction)
def on_high_probability_prediction(sender, instance, created, **kwargs):
    """Signal when high-probability error prediction is created."""
    if created and instance.probability > 0.75:
        # Trigger alert for high-probability predictions
        instance.trigger_alert()
