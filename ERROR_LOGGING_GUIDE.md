# Error Logging and Developer Notification System

## Overview

The Error Logging system is a comprehensive solution for tracking, analyzing, and notifying developers about errors across the entire Feeding Hearts platform. It captures errors from:

- **Django Backend** - AI/ML service
- **Laravel Backend** - Web API service
- **Java Backend** - Geolocation service
- **React Frontend** - Web application
- **Angular Frontend** - Admin dashboard
- **Vue Frontend** - Integration dashboard
- **Flutter Mobile** - Mobile application

## Architecture

### Database Layer

#### MongoDB (Flexible Document Store)
- **error_logs** - Main error tracking collection
- **error_notifications** - Notification delivery audit trail
- **error_patterns** - Recurring error detection
- **developer_assignments** - Developer routing and preferences

#### PostgreSQL (Relational Analytics)
- **error_logs** - Normalized error tracking table
- **error_notifications** - Notification tracking with retry logic
- **error_patterns** - Pattern recognition and trending
- **developer_assignments** - Developer management
- **error_stats** - Daily aggregation statistics
- **error_escalation** - Escalation tracking

### API Layer

**Base URL:** `/api/error-logging/`

#### Error Log Endpoints

```
GET    /errors/                  # List errors with filtering/pagination
POST   /errors/                  # Log new error
GET    /errors/{id}/             # Get error details
PATCH  /errors/{id}/             # Update error status
DELETE /errors/{id}/             # Delete error (soft delete)

POST   /errors/{id}/resolve/     # Mark error as resolved
POST   /errors/{id}/assign/      # Assign to developer
POST   /errors/{id}/escalate/    # Escalate error

GET    /errors/stats/            # Get error statistics
GET    /errors/recent/           # Get recent errors (24h)
GET    /errors/critical/         # Get critical unresolved errors
GET    /errors/by-service/       # Get errors by service
```

#### Developer Management Endpoints

```
GET    /developers/              # List developers
POST   /developers/              # Create developer assignment
GET    /developers/{id}/         # Get developer details
PATCH  /developers/{id}/         # Update developer
DELETE /developers/{id}/         # Remove developer

GET    /developers/workload/     # Get developer workload
POST   /developers/{id}/on-call/ # Set on-call status
```

#### Pattern Analysis Endpoints

```
GET    /patterns/                # List error patterns
GET    /patterns/{id}/           # Get pattern details
```

#### Notification Endpoints

```
GET    /notifications/           # List notifications
GET    /notifications/{id}/      # Get notification details
POST   /notifications/{id}/mark-read/ # Mark as read
```

### Webhook Endpoints

**Base URL:** `/api/error-logging/webhook/`

```
POST   /laravel/                 # Log errors from Laravel
POST   /java/                    # Log errors from Java
POST   /frontend/                # Log errors from React/Angular/Vue
POST   /mobile/                  # Log errors from Flutter
POST   /generic/                 # Log errors from any service
GET    /health/                  # Health check
```

## Setup and Configuration

### 1. Django Settings Configuration

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
    'error_logging',
    'celery',
    'corsheaders',
]

MIDDLEWARE = [
    # ...
    'error_logging.middleware.ErrorLoggingMiddleware',
]

# Error Logging Configuration
ERROR_LOGGING = {
    'RETENTION_DAYS': 90,
    'NOTIFICATION_CHANNELS': ['email', 'slack'],
    'EMAIL_NOTIFICATIONS': True,
    'SLACK_NOTIFICATIONS': True,
    'SMS_NOTIFICATIONS': False,
    'WEBHOOK_NOTIFICATIONS': False,
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@feedinghearts.com'

# Slack Configuration
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID = 'your-account-sid'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_PHONE_NUMBER = '+1234567890'

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Dashboard URL
DASHBOARD_URL = 'https://feedinghearts.local'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'feeding_hearts_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# MongoDB Configuration (optional for dual storage)
MONGODB = {
    'HOST': 'localhost',
    'PORT': 27017,
    'DB': 'feeding_hearts_errors'
}
```

### 2. Database Migrations

```bash
python manage.py makemigrations error_logging
python manage.py migrate error_logging
```

### 3. Register URLs

In main `urls.py`:

```python
urlpatterns = [
    # ...
    path('api/error-logging/', include('error_logging.urls')),
    path('api/error-logging/webhook/', include([
        path('laravel/', error_logging.webhooks.laravel_error_webhook),
        path('java/', error_logging.webhooks.java_error_webhook),
        path('frontend/', error_logging.webhooks.frontend_error_webhook),
        path('mobile/', error_logging.webhooks.mobile_error_webhook),
        path('generic/', error_logging.webhooks.generic_error_webhook),
        path('health/', error_logging.webhooks.webhook_health),
    ])),
]
```

### 4. Configure Celery Tasks

In Celery beat schedule configuration:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'retry-failed-notifications': {
        'task': 'error_logging.tasks.retry_failed_notifications',
        'schedule': crontab(minute=0),  # Every hour
    },
    'analyze-error-patterns': {
        'task': 'error_logging.tasks.analyze_error_patterns',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'escalate-unresolved-errors': {
        'task': 'error_logging.tasks.escalate_unresolved_errors',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'clean-old-error-logs': {
        'task': 'error_logging.tasks.clean_old_error_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-daily-summary': {
        'task': 'error_logging.tasks.generate_daily_error_summary',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    'check-error-thresholds': {
        'task': 'error_logging.tasks.check_error_thresholds',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

## Usage Examples

### 1. Log Error from Django View

```python
from error_logging.models import ErrorLog

# Manual logging
ErrorLog.objects.create(
    service='django',
    severity='high',
    error_type='ValidationError',
    message='Invalid donation amount',
    endpoint='/api/donations/',
    context={'amount': -10, 'user_id': 123},
)

# Or using decorator
from error_logging.middleware import error_capture_decorator

@error_capture_decorator
def my_view(request):
    # Errors are automatically captured and logged
    pass
```

### 2. Log Error from Frontend (React/Angular/Vue)

```javascript
// Client-side error handler
window.addEventListener('error', function(event) {
    fetch('/api/error-logging/webhook/frontend/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            service: 'react',  // or 'angular', 'vue'
            errorType: event.error?.name || 'Error',
            message: event.message,
            severity: 'high',
            endpoint: window.location.pathname,
            userAgent: navigator.userAgent,
            url: window.location.href,
            source: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            user_id: getCurrentUserId(),
            environment: 'production'
        })
    });
});
```

### 3. Log Error from Flutter Mobile App

```dart
import 'package:http/http.dart' as http;

Future<void> logError(String errorType, String message) async {
    try {
        await http.post(
            Uri.parse('https://api.feedinghearts.com/api/error-logging/webhook/mobile/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
                'error_type': errorType,
                'message': message,
                'severity': 'high',
                'screen': currentScreen,
                'device': deviceInfo.model,
                'os': deviceInfo.systemName,
                'app_version': appVersion,
                'user_id': userId,
                'session_id': sessionId,
                'environment': 'production'
            }),
        );
    } catch (e) {
        print('Failed to log error: $e');
    }
}
```

### 4. Log Error from Laravel

```php
// In Laravel controller or service
$errorData = [
    'error_type' => 'DatabaseError',
    'message' => 'Connection failed',
    'severity' => 'critical',
    'endpoint' => '/api/users',
    'code' => 500,
    'stack_trace' => $exception->getTraceAsString(),
    'context' => ['database' => 'mysql'],
    'environment' => 'production'
];

Http::post('http://django:8000/api/error-logging/webhook/laravel/', $errorData);
```

### 5. Query Errors via API

```bash
# Get recent errors
curl 'http://localhost:8000/api/error-logging/errors/recent/' \
  -H 'Authorization: Bearer TOKEN'

# Get critical errors
curl 'http://localhost:8000/api/error-logging/errors/critical/' \
  -H 'Authorization: Bearer TOKEN'

# Filter by service and severity
curl 'http://localhost:8000/api/error-logging/errors/?service=django&severity=high' \
  -H 'Authorization: Bearer TOKEN'

# Get error statistics
curl 'http://localhost:8000/api/error-logging/errors/stats/?days=7' \
  -H 'Authorization: Bearer TOKEN'

# Get developer workload
curl 'http://localhost:8000/api/error-logging/developers/workload/' \
  -H 'Authorization: Bearer TOKEN'
```

## Error Severity Levels

- **critical** - System down, data loss risk, immediate action required
- **high** - Major functionality broken, significant impact
- **medium** - Feature degraded, workaround available
- **low** - Minor issue, cosmetic problem
- **info** - Informational, no action required

## Notification Channels

### Email
- Automatically enabled for critical/high severity errors
- Configurable recipient list
- HTML formatted templates
- Retry mechanism (3 attempts)

### Slack
- Rich message formatting with color-coded severity
- Direct links to error details
- Thread replies for discussions
- Integration with on-call schedules

### SMS
- Twilio integration for critical alerts
- Phone number configuration per developer
- Character limited message format

### Webhooks
- Custom webhook URLs for external systems
- Customizable payload format
- Automatic retry with exponential backoff

## Developer Assignment

### Manual Assignment
```python
error.assign_to_developer(developer_id)
```

### Automatic Assignment
- Based on service expertise
- Round-robin load balancing
- On-call schedule consideration
- Escalation chain configuration

### Workload Monitoring
```bash
curl 'http://localhost:8000/api/error-logging/developers/workload/' \
  -H 'Authorization: Bearer TOKEN'
```

## Error Pattern Detection

The system automatically:
- Groups similar errors
- Tracks occurrence frequency
- Identifies trends
- Suggests root causes
- Triggers threshold alerts

## Escalation Logic

Errors are automatically escalated when:
- Critical errors unresolved for 1 hour
- High errors unresolved for 4 hours
- Medium errors unresolved for 8 hours
- Error rate exceeds 100/hour
- Critical error count exceeds 50/hour

## Performance Considerations

### Indexing Strategy
- Service + Severity (frequent filter)
- Timestamp descending (sorting)
- Error Type + Service (pattern detection)
- Assigned Developer (workload calculation)
- Status + Created Date (cleanup queries)

### Retention Policy
- Resolved errors: Deleted after 30 days
- Unresolved errors: Deleted after 90 days
- Pattern data: Kept indefinitely
- Notification logs: Kept for 60 days

### Caching
- Recent errors cached for 5 minutes
- Statistics cached for 15 minutes
- Developer workload cached for 10 minutes

## Troubleshooting

### Common Issues

**Notifications not sending:**
```python
# Check configuration
from django.conf import settings
print(settings.SLACK_WEBHOOK_URL)
print(settings.EMAIL_HOST_USER)

# Check Celery tasks
celery -A feeding_hearts inspect active
```

**Errors not being logged:**
```python
# Verify middleware is enabled
from django.conf import settings
print('error_logging.middleware.ErrorLoggingMiddleware' in settings.MIDDLEWARE)

# Check database connection
from error_logging.models import ErrorLog
ErrorLog.objects.count()
```

**High database storage:**
```python
# Run cleanup task
from error_logging.tasks import clean_old_error_logs
clean_old_error_logs()
```

## Security Considerations

- All error logs are access-controlled (staff users only)
- Stack traces contain sensitive info (redact PII)
- Webhook endpoints use CORS validation
- API requires authentication token
- Sensitive data (passwords, API keys) never logged

## Monitoring Dashboard

Access at `/admin/error-logging/` for:
- Real-time error feed
- Service health status
- Developer assignment overview
- Escalation queue
- Notification status
- Error trends and analytics

## Best Practices

1. **Always include context** - Add relevant data to error context
2. **Use appropriate severity** - Don't mark everything as critical
3. **Include stack traces** - Helps with debugging
4. **Monitor notifications** - Ensure developers are receiving alerts
5. **Review patterns** - Look for recurring issues
6. **Test error handling** - Verify webhook endpoints work
7. **Archive old errors** - Keep database clean
8. **Update assignments** - Keep developer assignments current
