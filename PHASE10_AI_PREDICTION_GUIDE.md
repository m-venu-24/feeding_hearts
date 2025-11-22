# AI ERROR PREDICTION SYSTEM - COMPLETE GUIDE

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [Models & Algorithms](#models--algorithms)
7. [Integration Guide](#integration-guide)
8. [Configuration](#configuration)
9. [Monitoring & Operations](#monitoring--operations)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

### Purpose
The AI Error Prediction System provides automatic detection and prevention of errors before they occur in the Feeding Hearts platform. Using machine learning models, it:

- **Predicts** future errors with confidence scores and time estimates
- **Detects** anomalies in error patterns and system behavior
- **Analyzes** root causes of errors automatically
- **Recommends** preventive actions to prevent issues
- **Forecasts** system metrics and capacity requirements
- **Generates** actionable AI insights for development teams

### Key Features
- ✅ Real-time error prediction with 70-90% accuracy
- ✅ Multi-service support (Django, Laravel, Java, React, Angular, Vue, Flutter)
- ✅ Automatic anomaly detection (statistical + pattern-based)
- ✅ Time series forecasting for capacity planning
- ✅ Root cause analysis with confidence scoring
- ✅ Automated preventive action recommendations
- ✅ Feedback loop for continuous model improvement
- ✅ Enterprise-grade security and compliance
- ✅ Asynchronous processing via Celery
- ✅ Comprehensive REST API

### Benefits
1. **Proactive Error Prevention** - Catch issues before they impact users
2. **Reduced Mean Time to Resolution (MTTR)** - Root cause analysis cuts debugging time
3. **Improved System Reliability** - Preventive actions reduce downtime
4. **Cost Savings** - Prevent expensive failures and SLA violations
5. **Developer Efficiency** - Automated insights reduce manual analysis
6. **Compliance** - Complete audit trail of all predictions and actions

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREDICTION ORCHESTRATOR                       │
│          Central coordinator for all ML operations               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        ↓            ↓            ↓            ↓   ↓
    ┌────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
    │ Anomaly│  │  Error    │  │ Forecast │  │Root Cause│
    │Detector│  │ Predictor │  │   Model  │  │ Analyzer │
    └────────┘  └───────────┘  └──────────┘  └──────────┘
        ↓            ↓            ↓              ↓
        └──────────────────────────┬──────────────┘
                                  ↓
                    ┌──────────────────────────┐
                    │  ML PREDICTION DATABASE  │
                    │  (PostgreSQL - Separate) │
                    └──────────────────────────┘
                                  ↓
        ┌─────────────────────────────────────────┐
        ↓            ↓            ↓            ↓   ↓
    ┌────────┐  ┌────────┐  ┌────────┐  ┌──────┐
    │ Alerts │  │ Actions│  │Insights│  │Feedback
    │ (Email)│  │(Auto)  │  │(Trends)│  │(Loop) │
    └────────┘  └────────┘  └────────┘  └──────┘
```

### Data Flow

```
ERROR LOGS (error_logging app)
         ↓
    FEATURE EXTRACTION
    (Temporal, Error Type, System)
         ↓
    PREDICTION MODELS
    (Anomaly, Classification, Forecast)
         ↓
    PREDICTIONS & ANOMALIES
    (Stored in ml_prediction database)
         ↓
    REAL-TIME ALERTING
    (Email, Slack, API)
         ↓
    PREVENTIVE ACTIONS
    (Automated or Manual)
         ↓
    FEEDBACK COLLECTION
    (True/False Positive)
         ↓
    MODEL RETRAINING
    (Daily/Weekly)
```

### Service Integration Points

Each service (Django, Laravel, Java, etc.) connects through:

1. **Error Log Ingestion** - Errors captured by error_logging middleware
2. **Feature Extraction** - Temporal, error type, and system features
3. **Real-time Prediction** - ML models analyze features
4. **Action Execution** - Preventive actions applied
5. **Feedback Loop** - Prediction accuracy tracked

---

## Installation & Setup

### Prerequisites
- Django 4.2+
- PostgreSQL 13+ (for ML database)
- Python 3.8+
- Celery 5.0+
- scikit-learn 1.0+
- TensorFlow 2.8+ (optional, for neural networks)
- pandas 1.3+

### Step 1: Create ML Database

```bash
# Create separate database for ML models
createdb feeding_hearts_ml

# Apply migrations
python manage.py migrate --database=ml_prediction
```

### Step 2: Install Dependencies

```bash
pip install \
    scikit-learn==1.3.0 \
    tensorflow==2.13.0 \
    pandas==2.0.0 \
    numpy==1.24.0 \
    scipy==1.11.0 \
    statsmodels==0.14.0 \
    prophet==1.1.4 \
    xgboost==2.0.0
```

### Step 3: Initialize ML Database Schema

```bash
# Load the schema
psql feeding_hearts_ml < database/postgres/ai-error-prediction-schema.sql

# Verify tables created
psql feeding_hearts_ml -c "\dt ai_models.*"
```

### Step 4: Configure Django Settings

```python
# settings.py

DATABASES = {
    'default': {
        # Existing database config
    },
    'ml_prediction': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'feeding_hearts_ml',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = ['ml_prediction.routers.MLPredictionRouter']

# ML Configuration
ML_PREDICTION_CONFIG = {
    'ANOMALY_THRESHOLD': 0.7,
    'PREDICTION_THRESHOLD': 0.6,
    'ALERT_PROBABILITY': 0.75,
    'LOOKBACK_HOURS': 24,
    'FORECAST_HORIZON': 24,
    'MODEL_RETRAINING_INTERVAL': 'daily',
}

# Celery beat schedule
CELERY_BEAT_SCHEDULE = {
    # ... add schedules from tasks.py CELERY_BEAT_SCHEDULE
}

# Installed apps
INSTALLED_APPS = [
    # ...
    'ml_prediction',
]
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations ml_prediction
python manage.py migrate ml_prediction
```

### Step 6: Initialize Models

```bash
python manage.py shell
```

```python
from ml_prediction.models import MLModel

# Create initial models
MLModel.objects.create(
    model_name='django-anomaly-detector-v1',
    model_type='anomaly_detection',
    service='django',
    framework='Django/Python',
    model_algorithm='IsolationForest',
    status='training',
    config={'n_estimators': 100, 'contamination': 0.05},
    created_by='system'
)
# ... create other models
```

### Step 7: Start Celery Worker

```bash
celery -A your_project.celery worker --loglevel=info
celery -A your_project.celery beat  # For periodic tasks
```

---

## Database Schema

### Core Tables

#### ml_models
Main registry of all ML models with metadata and performance metrics.

```sql
SELECT * FROM ai_models.ml_models;
```

Key fields:
- `model_id` (UUID) - Unique identifier
- `model_name` (VARCHAR) - Human-readable name
- `model_type` - anomaly_detection, time_series_forecast, error_classifier, etc.
- `service` - Django, Laravel, Java, React, Angular, Vue, Flutter
- `status` - training, active, inactive, archived
- `accuracy`, `precision`, `recall`, `f1_score` - Performance metrics

#### anomaly_detections
Results from anomaly detection algorithms.

```sql
SELECT * FROM ai_models.anomaly_detections;
```

Key fields:
- `anomaly_id` (UUID) - Unique anomaly identifier
- `anomaly_score` (0.0-1.0) - How anomalous (higher = more anomalous)
- `is_anomaly` (BOOLEAN) - Threshold-based classification
- `severity_level` - low, medium, high, critical
- `anomaly_type` - spike, drop, trend_change, pattern_deviation
- `root_cause_hypothesis` - AI's guess at root cause

#### error_predictions
Predictions of future errors.

```sql
SELECT * FROM ai_models.error_predictions;
```

Key fields:
- `prediction_id` (UUID) - Unique prediction identifier
- `probability` (0.0-1.0) - Likelihood of error occurring
- `predicted_timestamp` - When error is predicted to occur
- `time_horizon_minutes` - Minutes until predicted event
- `predicted_error_type` - Type of error expected
- `recommended_actions` - JSONB array of suggested actions

#### time_series_forecasts
System metrics forecasts (error rates, response times, etc).

```sql
SELECT * FROM ai_models.time_series_forecasts;
```

#### model_training_history
Complete history of all model training runs.

```sql
SELECT * FROM ai_models.model_training_history;
```

Key fields:
- `training_id` (UUID)
- `model_id` (FK)
- `status` - running, completed, failed, skipped
- `training_samples_count` - Number of samples used
- `final_accuracy`, `final_precision`, `final_recall` - Final metrics
- `failure_reason` - If training failed

#### preventive_actions
Recommended and executed preventive actions.

```sql
SELECT * FROM ai_models.preventive_actions;
```

Key fields:
- `action_id` (UUID)
- `action_type` - scale_up, restart, increase_pool, clear_cache, etc.
- `priority` - low, medium, high, critical
- `status` - recommended, scheduled, executed, skipped
- `can_be_automated` (BOOLEAN)

#### ai_insights
High-level AI insights and recommendations.

```sql
SELECT * FROM ai_models.ai_insights;
```

### Materialized Views

```sql
-- Active models summary
SELECT * FROM ai_models.v_active_models_summary;

-- Critical anomalies
SELECT * FROM ai_models.v_recent_critical_anomalies;

-- High-risk predictions
SELECT * FROM ai_models.v_high_risk_predictions;

-- Model accuracy trends
SELECT * FROM ai_models.v_model_accuracy_trend;
```

---

## API Reference

### Base URL
```
http://api.feedinghearts.local/api/ml/
```

### Authentication
All endpoints require JWT token:
```
Authorization: Bearer <jwt_token>
```

### 1. ML Models Endpoints

#### List Models
```
GET /api/ml/models/
```

Query parameters:
- `service` - Filter by service (django, laravel, etc.)
- `model_type` - Filter by type
- `status` - Filter by status
- `page` - Page number
- `page_size` - Results per page (default: 20)

Response:
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "model_id": "uuid-string",
      "model_name": "django-anomaly-detector-v1",
      "service": "django",
      "model_type": "anomaly_detection",
      "status": "active",
      "accuracy": 0.85,
      "precision": 0.82,
      "recall": 0.88,
      "f1_score": 0.85,
      "last_trained_at": "2024-01-15T10:30:00Z",
      "features_count": 24,
      "performance_summary": { ... }
    }
  ]
}
```

#### Get Model Details
```
GET /api/ml/models/{model_id}/
```

#### Get Model Performance
```
GET /api/ml/models/{model_id}/performance/
```

Response:
```json
{
  "model_id": "uuid",
  "model_name": "django-anomaly-detector-v1",
  "current_metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.88,
    "f1_score": 0.85
  },
  "recent_trend": [
    {
      "date": "2024-01-15",
      "accuracy": 0.85,
      "predictions_made": 245,
      "predictions_correct": 208
    }
  ]
}
```

#### Get Model Features
```
GET /api/ml/models/{model_id}/features/
```

### 2. Error Predictions Endpoints

#### List Predictions
```
GET /api/ml/predictions/
```

Query parameters:
- `service` - Filter by service
- `hours` - Time horizon (default: 24)
- `high_probability_only` - true/false

Response:
```json
{
  "count": 45,
  "results": [
    {
      "prediction_id": "uuid",
      "service": "django",
      "predicted_error_type": "DatabaseConnectionTimeout",
      "predicted_severity": "high",
      "probability": 0.82,
      "time_horizon_minutes": 45,
      "predicted_timestamp": "2024-01-15T11:45:00Z",
      "affected_users_count": 523,
      "recommended_actions": [ ... ],
      "alert_triggered": true,
      "alert_sent_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

#### Get High-Risk Predictions
```
GET /api/ml/predictions/high_risk/
```

#### Trigger Alert
```
POST /api/ml/predictions/{prediction_id}/trigger_alert/
```

#### Mark Prediction as Occurred
```
POST /api/ml/predictions/{prediction_id}/mark_occurred/
```

Request body:
```json
{
  "error_id": "error-uuid",
  "timestamp": "2024-01-15T11:45:30Z"
}
```

### 3. Anomaly Detection Endpoints

#### List Anomalies
```
GET /api/ml/anomalies/
```

Query parameters:
- `service` - Filter by service
- `severity_level` - Filter by severity
- `is_anomaly` - true/false
- `acknowledged` - true/false

Response:
```json
{
  "count": 12,
  "results": [
    {
      "anomaly_id": "uuid",
      "service": "laravel",
      "anomaly_score": 0.92,
      "is_anomaly": true,
      "severity_level": "critical",
      "anomaly_type": "spike",
      "detected_at": "2024-01-15T10:30:00Z",
      "root_cause_hypothesis": "Database connection pool exhaustion",
      "recommended_action": "Increase connection pool size",
      "acknowledged": false
    }
  ]
}
```

#### Get Unacknowledged Anomalies
```
GET /api/ml/anomalies/unacknowledged/
```

#### Get Critical Anomalies
```
GET /api/ml/anomalies/critical/
```

#### Acknowledge Anomaly
```
POST /api/ml/anomalies/{anomaly_id}/acknowledge/
```

### 4. Time Series Forecasts

#### List Forecasts
```
GET /api/ml/forecasts/
```

#### Get Forecast by Service
```
GET /api/ml/forecasts/by-service/{service}/
```

Example:
```
GET /api/ml/forecasts/by-service/django/
```

#### Get At-Risk Forecasts
```
GET /api/ml/forecasts/at_risk/
```

### 5. Preventive Actions

#### List Actions
```
GET /api/ml/actions/
```

Query parameters:
- `status` - recommended, scheduled, executed, skipped
- `priority` - low, medium, high, critical
- `action_type` - Filter by action type

#### Get Pending Actions
```
GET /api/ml/actions/pending/
```

#### Execute Action
```
POST /api/ml/actions/{action_id}/execute/
```

Request body:
```json
{
  "result": {
    "success": true,
    "duration": 120,
    "impact_observed": "Database connections restored to normal"
  }
}
```

#### Get Actions by Priority
```
GET /api/ml/actions/by_priority/
```

### 6. AI Insights

#### List Insights
```
GET /api/ml/insights/
```

Query parameters:
- `service` - Filter by service
- `insight_type` - Filter by type
- `severity` - Filter by severity
- `status` - Filter by status
- `active_only` - true/false

#### Get Active Insights
```
GET /api/ml/insights/active/
```

#### Get Insights by Service
```
GET /api/ml/insights/by_service/
```

Response:
```json
{
  "summary": [
    {
      "service": "django",
      "total": 5,
      "critical": 1,
      "warning": 2,
      "unresolved": 3
    }
  ]
}
```

### 7. Analysis Trigger

#### Trigger ML Analysis
```
POST /api/ml/trigger-analysis/
```

Request body:
```json
{
  "service": "django",
  "analysis_type": "full"
}
```

Analysis types:
- `full` - Complete analysis (predictions, anomalies, forecasts, insights)
- `quick` - Fast analysis (anomalies only)
- `deep` - Detailed root cause analysis

#### Trigger Analysis for All Services
```
POST /api/ml/trigger-all-services-analysis/
```

### 8. Dashboard Summary

#### Get Dashboard Summary
```
GET /api/ml/dashboard/summary/
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "health_score": 82,
  "predictions": {
    "total": 245,
    "high_probability": 12,
    "alerts_triggered": 10,
    "accurate": 203
  },
  "anomalies": {
    "total": 8,
    "critical": 1,
    "unacknowledged": 2
  },
  "models": {
    "active": 8,
    "by_service": [ ... ]
  },
  "recent_activity": {
    "predictions_24h": 45,
    "anomalies_24h": 3,
    "actions_executed_24h": 2
  }
}
```

---

## Models & Algorithms

### 1. Anomaly Detection

#### Isolation Forest
**Purpose:** Detect unusual error patterns  
**Input Features:**
- Error count by hour
- Error count variance
- Error type distribution
- Response time percentiles

**Output:**
- Anomaly score (0.0-1.0)
- Anomaly type (spike, drop, trend_change, pattern_deviation)
- Severity level (low, medium, high, critical)

#### Local Outlier Factor (LOF)
**Purpose:** Detect local density-based outliers  
**Parameters:**
- n_neighbors: 20
- contamination: 0.05

#### Statistical Z-Score
**Purpose:** Detect statistical outliers  
**Formula:** z = (x - mean) / std_dev  
**Threshold:** z > 2.5 (more than 2.5 standard deviations)

### 2. Error Prediction

#### Random Forest Classifier
**Purpose:** Classify probability of error occurrence  
**Features:**
- Temporal features (hour, day, trend)
- Error type history
- System metrics
- Service state

**Output:**
- Error probability (0.0-1.0)
- Predicted error type
- Predicted severity
- Contributing factors

#### Gradient Boosting (XGBoost)
**Purpose:** Boost prediction accuracy  
**Parameters:**
- n_estimators: 100
- max_depth: 5
- learning_rate: 0.1

### 3. Time Series Forecasting

#### Prophet
**Purpose:** Forecast error rates and metrics  
**Features:**
- Trend component
- Seasonality (daily, weekly)
- Holiday effects
- Change points

**Output:**
- Forecast values with confidence intervals
- Trend direction
- Peak predictions
- Capacity warnings

#### LSTM Neural Network
**Purpose:** Long-term dependency learning  
**Architecture:**
- Input: 24 hours historical data
- LSTM layers: 2 (64 units each)
- Output: 24 hour forecast
- Sequence length: 72 (3 days)

### 4. Root Cause Analysis

#### Decision Tree
**Purpose:** Find most likely root cause  
**Decision paths:**
1. Error type → error_type_specific_causes
2. Service → service_specific_issues
3. System state → environmental_factors
4. Historical patterns → similar_past_issues

#### Pattern Matching
**Purpose:** Match against historical error patterns  
**Methods:**
- Similarity scoring
- Cosine distance
- Pattern signature matching

### 5. Feature Engineering

#### Temporal Features
```python
features = {
    'hour_of_day': 0-23,
    'day_of_week': 0-6,
    'is_peak_hours': boolean,
    'error_trend_slope': float,
    'error_trend_intercept': float,
    'current_error_rate': float,
}
```

#### Error Type Features
```python
features = {
    'error_type_timeout_ratio': percentage,
    'error_type_connection_ratio': percentage,
    'error_type_auth_ratio': percentage,
    'severity_critical_ratio': percentage,
    'severity_high_ratio': percentage,
    'critical_error_count': integer,
}
```

#### System Features
```python
features = {
    'response_time_mean': milliseconds,
    'response_time_p95': milliseconds,
    'response_time_p99': milliseconds,
    'response_time_max': milliseconds,
    'database_error_ratio': percentage,
    'api_error_ratio': percentage,
}
```

---

## Integration Guide

### Django Integration

```python
# ml_prediction/django_integration.py

from ml_prediction.services import PredictionOrchestrator
from error_logging.models import ErrorLog

class DjangoMLIntegration:
    """Integrate ML prediction with Django error logging."""
    
    @classmethod
    def on_error_logged(cls, error_log: ErrorLog):
        """Called when error is logged."""
        # Extract service and analyze
        if error_log.service == 'django':
            orchestrator = PredictionOrchestrator()
            results = orchestrator.run_full_analysis('django')
            
            # Take preventive actions if needed
            cls.execute_preventive_actions(results)
    
    @staticmethod
    def execute_preventive_actions(results):
        """Execute recommended preventive actions."""
        # Automatically execute recommended actions
        from ml_prediction.models import PreventiveAction
        
        for action in PreventiveAction.objects.filter(status='recommended'):
            if action.can_be_automated:
                action.execute('django_automation')
```

### Error Logging Integration

```python
# error_logging/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ErrorLog

@receiver(post_save, sender=ErrorLog)
def on_error_logged(sender, instance, created, **kwargs):
    """Trigger ML analysis when error is logged."""
    if created:
        try:
            from ml_prediction.django_integration import DjangoMLIntegration
            DjangoMLIntegration.on_error_logged(instance)
        except Exception as e:
            logger.error(f"Error in ML integration: {e}")
```

### Webhook Integration

```python
# ml_prediction/webhooks.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import PredictionOrchestrator

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_for_error(request):
    """
    Receive error from error_logging and run immediate prediction.
    
    Request body:
    {
        "error_id": "uuid",
        "error_type": "DatabaseTimeoutError",
        "service": "django",
        "severity": "high"
    }
    """
    error_id = request.data.get('error_id')
    service = request.data.get('service')
    
    orchestrator = PredictionOrchestrator()
    results = orchestrator.run_full_analysis(service)
    
    return Response({
        'success': True,
        'analysis_results': results,
    })
```

### Notification Integration

```python
# ml_prediction/notifications.py

from django.core.mail import send_mail
from django.template.loader import render_to_string

def notify_prediction(prediction):
    """Send notification about high-risk prediction."""
    if float(prediction.probability) >= 0.75:
        context = {
            'error_type': prediction.predicted_error_type,
            'probability': float(prediction.probability),
            'service': prediction.service,
            'time_estimate': prediction.time_horizon_minutes,
        }
        
        html_message = render_to_string('prediction_alert.html', context)
        
        send_mail(
            f'HIGH RISK: {prediction.predicted_error_type}',
            '',
            'noreply@feedinghearts.local',
            ['ops-team@feedinghearts.local'],
            html_message=html_message,
        )
```

---

## Configuration

### Environment Variables

```bash
# ML Database
ML_DB_NAME=feeding_hearts_ml
ML_DB_USER=postgres
ML_DB_PASSWORD=secure_password
ML_DB_HOST=localhost
ML_DB_PORT=5432

# ML Configuration
ML_ANOMALY_THRESHOLD=0.7
ML_PREDICTION_THRESHOLD=0.6
ML_ALERT_PROBABILITY=0.75
ML_LOOKBACK_HOURS=24
ML_FORECAST_HORIZON=24

# Model Training
ML_TRAINING_SAMPLES_MIN=1000
ML_TRAINING_INTERVAL=daily
ML_MODEL_RETRAINING_ENABLED=true

# Notifications
ML_ALERT_EMAIL=ops-team@feedinghearts.local
ML_TEAM_EMAIL=ml-team@feedinghearts.local
ALERT_SEVERITY_CRITICAL=true
```

### Settings.py Configuration

```python
# Django ML Prediction Settings

ML_PREDICTION_CONFIG = {
    # Thresholds
    'ANOMALY_SCORE_THRESHOLD': 0.7,
    'ANOMALY_CRITICAL_THRESHOLD': 0.85,
    'ANOMALY_WARNING_THRESHOLD': 0.5,
    
    'HIGH_PROBABILITY_THRESHOLD': 0.75,
    'MEDIUM_PROBABILITY_THRESHOLD': 0.60,
    'LOW_PROBABILITY_THRESHOLD': 0.40,
    
    'ALERT_PROBABILITY_THRESHOLD': 0.70,
    
    # Time horizons (minutes)
    'SHORT_TERM_HORIZON': 30,
    'MEDIUM_TERM_HORIZON': 120,
    'LONG_TERM_HORIZON': 1440,
    
    # Feature caching (seconds)
    'FEATURE_CACHE_TTL': 300,
    'PREDICTION_CACHE_TTL': 60,
    
    # Model training
    'TRAINING_SCHEDULE': 'daily',
    'MIN_TRAINING_SAMPLES': 1000,
    'MAX_TRAINING_TIME': 3600,  # seconds
    
    # Cleanup
    'CLEANUP_OLD_PREDICTIONS_DAYS': 90,
}

# Celery Configuration
CELERY_BEAT_SCHEDULE = {
    'train-models': {
        'task': 'ml_prediction.tasks.train_error_prediction_models',
        'schedule': crontab(hour=2, minute=0),
    },
    'batch-predictions': {
        'task': 'ml_prediction.tasks.predict_errors_batch',
        'schedule': crontab(minute=0),
    },
    'anomaly-detection': {
        'task': 'ml_prediction.tasks.detect_anomalies_background',
        'schedule': crontab(minute='*/15'),
    },
    'insights-generation': {
        'task': 'ml_prediction.tasks.generate_ai_insights',
        'schedule': crontab(minute='*/30'),
    },
}
```

---

## Monitoring & Operations

### Health Check

```python
# ml_prediction/health_check.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MLModel, ErrorPrediction, AnomalyDetection
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
def health_check(request):
    """Check ML system health."""
    now = timezone.now()
    
    # Check active models
    active_models = MLModel.objects.filter(status='active').count()
    
    # Check recent predictions
    recent_predictions = ErrorPrediction.objects.filter(
        created_at__gte=now - timedelta(hours=1)
    ).count()
    
    # Check recent anomalies
    recent_anomalies = AnomalyDetection.objects.filter(
        detected_at__gte=now - timedelta(hours=1)
    ).count()
    
    # Calculate health score
    health_score = 100
    if active_models == 0:
        health_score -= 50
    if recent_predictions == 0:
        health_score -= 25
    
    status = 'healthy' if health_score >= 80 else 'degraded' if health_score >= 50 else 'critical'
    
    return Response({
        'status': status,
        'health_score': health_score,
        'active_models': active_models,
        'recent_predictions_1h': recent_predictions,
        'recent_anomalies_1h': recent_anomalies,
        'timestamp': now.isoformat(),
    })
```

### Metrics & Logging

```python
# ml_prediction/logging_config.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'ml_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/ml_prediction.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
        'ml_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/ml_prediction_errors.log',
            'maxBytes': 10485760,
            'backupCount': 10,
        },
    },
    'loggers': {
        'ml_prediction': {
            'handlers': ['ml_file', 'ml_errors'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Performance Metrics

```sql
-- Daily accuracy check
SELECT 
    model_id,
    tracking_date,
    accuracy_today,
    predictions_made,
    predictions_correct,
    errors_prevented
FROM ai_models.model_performance_tracking
WHERE tracking_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY tracking_date DESC;

-- Model performance trend
SELECT 
    m.model_name,
    DATE(pt.tracking_date) as date,
    AVG(pt.accuracy_today) as avg_accuracy,
    SUM(pt.predictions_made) as total_predictions,
    SUM(pt.errors_prevented) as errors_prevented
FROM ai_models.model_performance_tracking pt
JOIN ai_models.ml_models m ON pt.model_id = m.model_id
WHERE pt.tracking_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY m.model_name, DATE(pt.tracking_date)
ORDER BY m.model_name, date DESC;

-- Alert effectiveness
SELECT 
    service,
    COUNT(*) as total_alerts,
    COUNT(CASE WHEN actual_error_occurred = true THEN 1 END) as true_alerts,
    ROUND(100.0 * COUNT(CASE WHEN actual_error_occurred = true THEN 1 END) 
        / COUNT(*), 2) as accuracy_percent
FROM ai_models.error_predictions
WHERE alert_triggered = true
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY service
ORDER BY accuracy_percent DESC;
```

---

## Troubleshooting

### Common Issues

#### 1. Models Not Training

**Symptom:** last_trained_at stays NULL

**Causes:**
- Celery worker not running
- Insufficient error data
- Database connection issue
- Memory constraints

**Solutions:**
```bash
# Check Celery worker
celery -A your_project.celery inspect active

# Manually trigger training
python manage.py shell
from ml_prediction.tasks import train_error_prediction_models
train_error_prediction_models()

# Check logs
tail -f logs/ml_prediction.log
```

#### 2. Predictions Not Generating

**Symptom:** No predictions in database

**Causes:**
- Error logs not being ingested
- Feature extraction failing
- Models not active

**Solutions:**
```bash
# Check error logs
python manage.py shell
from error_logging.models import ErrorLog
ErrorLog.objects.filter(service='django').count()

# Check active models
from ml_prediction.models import MLModel
MLModel.objects.filter(status='active')

# Test prediction directly
from ml_prediction.services import ErrorPredictor
predictor = ErrorPredictor()
predictions = predictor.predict_errors('django')
```

#### 3. High False Positive Rate

**Symptom:** Too many false anomalies/predictions

**Solutions:**
- Increase anomaly threshold
- Retrain models with more data
- Adjust feature scaling
- Reduce anomaly_type sensitivity

```python
# In settings.py
ML_PREDICTION_CONFIG['ANOMALY_SCORE_THRESHOLD'] = 0.75  # Increase from 0.7
```

#### 4. Database Performance Issues

**Symptom:** Slow queries on ml_prediction database

**Solutions:**
```sql
-- Analyze tables
ANALYZE ai_models.error_predictions;
ANALYZE ai_models.anomaly_detections;

-- Reindex
REINDEX TABLE ai_models.error_predictions;
REINDEX TABLE ai_models.anomaly_detections;

-- Check index usage
SELECT schemaname, tablename, indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename;
```

#### 5. Alert Email Not Sending

**Symptom:** Predictions generated but no email

**Solutions:**
```bash
# Check email configuration
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])

# Check Celery tasks
celery -A your_project.celery inspect scheduled

# Enable email logging
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Debug Mode

```python
# ml_prediction/debug.py

from .services import PredictionOrchestrator
from .models import MLModel

def debug_full_analysis(service='django'):
    """Run full analysis with detailed logging."""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    logger = logging.getLogger('ml_prediction.debug')
    
    logger.info(f"Starting debug analysis for {service}")
    
    # Check active models
    models = MLModel.objects.filter(service=service, status='active')
    logger.info(f"Found {models.count()} active models")
    
    # Run analysis
    orchestrator = PredictionOrchestrator()
    results = orchestrator.run_full_analysis(service)
    
    logger.info(f"Analysis results: {results}")
    return results
```

---

## Performance Benchmarks

### Expected Performance

| Metric | Expected Value | Notes |
|--------|---|---|
| Anomaly Detection Accuracy | 75-85% | Improves with data |
| Error Prediction Accuracy | 70-80% | Service-dependent |
| Forecast MAPE | < 20% | Error rates are volatile |
| API Response Time | < 100ms | With caching |
| Prediction Latency | < 1 second | Real-time |
| Model Training Time | 10-30 minutes | Daily |

### Capacity Planning

- **100 requests/min:** Single worker
- **1,000 requests/min:** 5-10 workers
- **10,000+ requests/min:** Distributed cluster

---

## Next Steps

1. **Monitor Dashboard** - Access `/api/ml/dashboard/summary/`
2. **Configure Alerts** - Set up email notifications
3. **Review Insights** - Check `/api/ml/insights/`
4. **Tune Models** - Adjust thresholds based on feedback
5. **Integrate Services** - Connect to all 7 services
6. **Collect Feedback** - Use prediction feedback endpoint
7. **Retrain Models** - Weekly retraining with feedback

---

**Last Updated:** January 2024  
**Version:** 1.0.0  
**Status:** Production Ready
