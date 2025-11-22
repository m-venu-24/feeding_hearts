# AI Prediction Integration Settings for Feeding Hearts
# Add these settings to your Django settings.py file

import os
from pathlib import Path

# ============================================================================
# AI PREDICTION & ERROR RECOVERY INTEGRATION SETTINGS
# ============================================================================

# Error Logging Configuration
ERROR_LOGGING_ENABLED = True
ERROR_LOG_TO_DATABASE = True
ERROR_ALERT_RECIPIENTS = os.getenv('ERROR_ALERT_RECIPIENTS', 'ops@feedinghearts.com').split(',')
SLACK_ERROR_ALERTS = os.getenv('SLACK_ERROR_ALERTS', 'False') == 'True'
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')

# Auto Error Recovery Settings
AUTO_RECOVERY_ENABLED = True
RECOVERY_TIMEOUT_SECONDS = int(os.getenv('RECOVERY_TIMEOUT', '5'))
MAX_RECOVERY_ATTEMPTS = int(os.getenv('MAX_RECOVERY_ATTEMPTS', '3'))
RECOVERY_BACKOFF_FACTOR = 1.5  # Exponential backoff multiplier

# Recovery Strategies Configuration
ENABLED_RECOVERY_STRATEGIES = [
    'automatic_retry',           # Retry failed operations
    'timeout_increase',          # Increase operation timeout
    'cache_clear',               # Clear caches
    'connection_pool_increase',  # Increase database connections
    'resource_scaling',          # Scale up resources
    'circuit_breaker',           # Activate circuit breaker
    'service_fallback',          # Use fallback service
    'queue_priority',            # Boost queue priority
    'request_throttling',        # Rate limiting
    'service_restart',           # Graceful restart
]

# Circuit Breaker Settings
CIRCUIT_BREAKER_THRESHOLD = 5  # Failures before opening circuit
CIRCUIT_BREAKER_TIMEOUT = 60   # Seconds before half-open
CIRCUIT_BREAKER_RESET_TIMEOUT = 300  # Seconds before reset

# ML Prediction & AI Settings
ML_PREDICTION_ENABLED = True
ERROR_PREDICTION_ENABLED = True
ANOMALY_DETECTION_ENABLED = True
AUTOML_ENABLED = True

# Prediction Thresholds
PREDICTION_CONFIDENCE_THRESHOLD = float(os.getenv('PREDICTION_CONFIDENCE_THRESHOLD', '0.75'))
ANOMALY_SENSITIVITY = float(os.getenv('ANOMALY_SENSITIVITY', '0.8'))
ANOMALY_DETECTION_WINDOW = 24  # Hours of historical data to analyze

# ML Model Settings
ML_MODEL_TYPE = 'ensemble'  # 'ensemble', 'neural_network', 'random_forest', 'gradient_boosting'
ML_MODEL_UPDATE_FREQUENCY = 3600  # Seconds between model retraining
ML_MODEL_EVALUATION_FREQUENCY = 1800  # Seconds between model evaluation
ML_DATA_RETENTION_DAYS = 90  # Days to keep training data

# Monitoring & Health Check
ENABLE_HEALTH_MONITORING = True
HEALTH_CHECK_INTERVAL = 30  # Seconds
HEALTH_CHECK_TIMEOUT = 5    # Seconds
HEALTH_CHECK_ENDPOINTS = [
    'http://localhost:8000/api/health/',
    'http://localhost:5432/',  # PostgreSQL
    'http://localhost:27017/',  # MongoDB
    'http://localhost:6379/',   # Redis
]

# Metrics & Analytics
COLLECT_METRICS = True
METRICS_RETENTION_DAYS = 30
METRICS_AGGREGATION_INTERVAL = 300  # Seconds
METRICS_INCLUDE_RECOVERY_STATS = True
METRICS_INCLUDE_PREDICTION_STATS = True

# Logging Configuration for AI System
AI_LOGGING_ENABLED = True
AI_LOGGING_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
AI_LOGGING_FORMAT = 'json'  # 'json' or 'text'
AI_LOGGING_FILE = 'logs/ai_prediction.log'
AI_LOG_ERROR_DETAILS = True
AI_LOG_RECOVERY_ACTIONS = True
AI_LOG_PREDICTIONS = True

# Cache Configuration for ML Models
ML_MODEL_CACHE_BACKEND = 'default'  # Uses CACHES['default']
ML_MODEL_CACHE_TIMEOUT = 3600  # Seconds
ML_PREDICTION_CACHE_TIMEOUT = 1800  # Seconds

# Database Configuration for ML Data
ML_DATABASE_BACKEND = 'mongodb'  # 'mongodb' or 'postgresql'
ML_MONGODB_NAME = os.getenv('ML_MONGODB_NAME', 'feeding_hearts_ml')
ML_MONGODB_HOST = os.getenv('ML_MONGODB_HOST', 'mongodb://localhost:27017')

# Celery Configuration for Async Tasks
CELERY_TASK_ALWAYS_EAGER = False  # Set to True for testing
CELERY_TASK_TIME_LIMIT = 600  # Task timeout in seconds
CELERY_TASK_SOFT_TIME_LIMIT = 300  # Soft timeout for graceful shutdown
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Async Task Settings
ASYNC_ERROR_LOGGING = True
ASYNC_PREDICTION = True
ASYNC_RECOVERY = False  # Keep synchronous for immediate response
ASYNC_ALERTING = True
ASYNC_MODEL_TRAINING = True

# Service Fallback Configuration
SERVICE_FALLBACK_TIMEOUT = 2  # Seconds before trying fallback
SERVICE_FALLBACK_ENABLED = True
SERVICE_FALLBACK_MAPPING = {
    'django_service': 'laravel_service',
    'laravel_service': 'django_service',
    'java_service': 'django_service',
}

# API Rate Limiting (for throttling recovery)
RATE_LIMIT_ENABLED = True
RATE_LIMIT_PER_MINUTE = 100
RATE_LIMIT_PER_HOUR = 10000
RATE_LIMIT_BURST_SIZE = 10

# Request/Response Compression
ENABLE_REQUEST_COMPRESSION = True
COMPRESSION_THRESHOLD = 1024  # Bytes
COMPRESSION_LEVEL = 6  # 1-9

# Timeout Configuration
DEFAULT_REQUEST_TIMEOUT = 30  # Seconds
DATABASE_QUERY_TIMEOUT = 10  # Seconds
API_CALL_TIMEOUT = 15  # Seconds
EXTERNAL_SERVICE_TIMEOUT = 20  # Seconds

# Resource Limits
MAX_MEMORY_USAGE_PERCENT = 85
MAX_CPU_USAGE_PERCENT = 90
MIN_AVAILABLE_CONNECTIONS = 5
MIN_CACHE_SIZE_MB = 100

# Email Configuration for Alerts
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@feedinghearts.com')

# Error Recovery Alert Settings
SEND_RECOVERY_ALERTS = True
RECOVERY_SUCCESS_NOTIFICATION = False  # Only notify on failures
RECOVERY_FAILURE_NOTIFICATION = True

# Prediction Alert Settings
SEND_PREDICTION_ALERTS = True
PREDICTION_ALERT_THRESHOLD = 0.85  # Alert if prediction confidence > 85%
ANOMALY_ALERT_ENABLED = True

# Dashboard & UI Settings
ENABLE_AI_DASHBOARD = True
DASHBOARD_REFRESH_INTERVAL = 10  # Seconds
DASHBOARD_CHARTS_ENABLED = True
DASHBOARD_EXPORT_ENABLED = True

# Testing & Development
ENABLE_ERROR_SIMULATION = os.getenv('ENABLE_ERROR_SIMULATION', 'False') == 'True'
ENABLE_DEBUG_RECOVERY = os.getenv('ENABLE_DEBUG_RECOVERY', 'False') == 'True'
ENABLE_TEST_ALERTS = os.getenv('ENABLE_TEST_ALERTS', 'False') == 'True'

# Installed Apps (ensure these are included)
# Add to INSTALLED_APPS in settings.py if not already present:
REQUIRED_INSTALLED_APPS = [
    'error_logging',      # Phase 9: Error Logging
    'ml_prediction',      # Phase 10: AI Prediction
    'ml_models',          # ML Models storage
    'predictions',        # Prediction records
    'analytics',          # Analytics & metrics
]

# Middleware (ensure this is included)
# Add to MIDDLEWARE in settings.py if not already present:
REQUIRED_MIDDLEWARE = [
    'error_logging.ai_recovery_middleware.AIErrorRecoveryMiddleware',
]

# ============================================================================
# END OF AI PREDICTION INTEGRATION SETTINGS
# ============================================================================
