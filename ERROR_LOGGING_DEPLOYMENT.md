# Error Logging System - Configuration & Deployment

## Environment Variables

### Django Backend (`.env`)

```bash
# Error Logging Configuration
ERROR_LOGGING_ENABLED=True
ERROR_LOGGING_RETENTION_DAYS=90

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/feeding_hearts_db
MONGODB_URL=mongodb://localhost:27017/feeding_hearts_errors

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@feedinghearts.com

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=True

# Twilio Configuration (SMS)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
SMS_ENABLED=False

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json

# Dashboard
DASHBOARD_URL=https://feedinghearts.local
DASHBOARD_ADMIN_EMAIL=admin@feedinghearts.com

# Notification Threshold
ERROR_THRESHOLD_HOURLY=100
CRITICAL_ERROR_THRESHOLD_HOURLY=50
ESCALATION_ENABLED=True

# Security
ALLOWED_WEBHOOK_IPS=127.0.0.1,localhost,192.168.0.0/16
WEBHOOK_SECRET_KEY=your-secret-key-here
```

### Laravel Backend (`.env`)

```bash
# Error Logging
ERROR_LOGGING_URL=http://django:8000/api/error-logging/webhook/laravel/
ERROR_LOGGING_ENABLED=true
ERROR_LOGGING_TIMEOUT=5

# Service Name
APP_SERVICE_NAME=laravel-web-api
APP_ENV=production
```

### Java Service (`application.yml`)

```yaml
spring:
  application:
    name: java-geolocation-service

error-logging:
  url: http://django:8000/api/error-logging/webhook/java/
  enabled: true
  timeout: 5000
  retry:
    attempts: 3
    delay: 1000

logging:
  level:
    root: INFO
    com.feedinghearts: DEBUG
  pattern:
    console: "%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
```

### Frontend Configuration

#### React (`.env`)

```bash
REACT_APP_ENV=production
REACT_APP_API_URL=https://api.feedinghearts.com
REACT_APP_ERROR_LOGGING_ENABLED=true
REACT_APP_ERROR_LOGGING_THRESHOLD=medium
REACT_APP_DASHBOARD_URL=https://dashboard.feedinghearts.com
```

#### Angular (`environment.ts`)

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.feedinghearts.com',
  errorLogging: {
    enabled: true,
    threshold: 'medium',
    webhookUrl: '/api/error-logging/webhook/frontend/',
  },
  dashboardUrl: 'https://dashboard.feedinghearts.com',
};
```

#### Vue (`.env`)

```bash
VITE_ENV=production
VITE_API_URL=https://api.feedinghearts.com
VITE_ERROR_LOGGING_ENABLED=true
VITE_DASHBOARD_URL=https://dashboard.feedinghearts.com
```

#### Flutter (`lib/config/environment.dart`)

```dart
class Environment {
  static const String apiBaseUrl = 'https://api.feedinghearts.com';
  static const String errorLoggingUrl = 'https://api.feedinghearts.com/api/error-logging/webhook/mobile/';
  static const bool errorLoggingEnabled = true;
  static const String environment = 'production';
}
```

---

## Docker Compose Configuration

### Add to `docker-compose.full.yml`

```yaml
version: '3.8'

services:
  # ... existing services ...

  # PostgreSQL for Error Logging
  postgres-error-logs:
    image: postgres:16-alpine
    container_name: postgres_error_logs
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: feeding_hearts_errors
    volumes:
      - postgres_error_logs_data:/var/lib/postgresql/data
      - ./database/postgres/error-logging-schema.sql:/docker-entrypoint-initdb.d/01-error-schema.sql
    ports:
      - "5433:5432"
    networks:
      - feeding_hearts_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MongoDB for Error Logging (Optional - dual storage)
  mongodb-error-logs:
    image: mongo:7.0
    container_name: mongodb_error_logs
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-password}
      MONGO_INITDB_DATABASE: feeding_hearts_errors
    volumes:
      - mongodb_error_logs_data:/data/db
      - ./database/mongodb/error-logging-schema.js:/docker-entrypoint-initdb.d/01-error-schema.js
    ports:
      - "27018:27017"
    networks:
      - feeding_hearts_network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for Celery Task Queue
  redis-celery:
    image: redis:7.0-alpine
    container_name: redis_celery
    ports:
      - "6380:6379"
    networks:
      - feeding_hearts_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Celery Worker for Error Notifications
  celery-worker:
    build:
      context: ./backend/django-ai-ml
      dockerfile: Dockerfile
    container_name: celery_worker
    command: celery -A feeding_hearts worker -l info --concurrency=4
    environment:
      - CELERY_BROKER_URL=redis://redis-celery:6379/0
      - CELERY_RESULT_BACKEND=redis://redis-celery:6379/0
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD:-password}@postgres:5432/feeding_hearts_db
      - MONGODB_URL=mongodb://admin:${MONGO_PASSWORD:-password}@mongodb:27017/feeding_hearts_errors
    depends_on:
      - postgres
      - mongodb
      - redis-celery
      - django-api
    networks:
      - feeding_hearts_network
    restart: unless-stopped

  # Celery Beat for Scheduled Tasks
  celery-beat:
    build:
      context: ./backend/django-ai-ml
      dockerfile: Dockerfile
    container_name: celery_beat
    command: celery -A feeding_hearts beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - CELERY_BROKER_URL=redis://redis-celery:6379/0
      - CELERY_RESULT_BACKEND=redis://redis-celery:6379/0
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD:-password}@postgres:5432/feeding_hearts_db
    depends_on:
      - postgres
      - redis-celery
      - django-api
    networks:
      - feeding_hearts_network
    restart: unless-stopped

  # Nginx reverse proxy with error logging
  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/error-logging.conf:/etc/nginx/conf.d/error-logging.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - django-api
      - laravel-api
      - java-service
      - react-app
      - angular-app
      - vue-app
    networks:
      - feeding_hearts_network
    restart: unless-stopped

volumes:
  postgres_error_logs_data:
  mongodb_error_logs_data:

networks:
  feeding_hearts_network:
    driver: bridge
```

### Nginx Error Logging Configuration (`nginx/error-logging.conf`)

```nginx
# Error Logging Webhook Integration
upstream error_logging {
    server django:8000;
}

# Log format with additional details
log_format error_log_format '$remote_addr - $remote_user [$time_local] '
                          '"$request" $status $body_bytes_sent '
                          '"$http_referer" "$http_user_agent" '
                          'rt=$request_time uct="$upstream_connect_time" '
                          'uht="$upstream_header_time" urt="$upstream_response_time"';

# Log errors to file
error_log /var/log/nginx/error.log warn;

# Capture error responses and forward to error logging
server {
    listen 80;
    server_name _;

    # Proxy errors to error logging system
    error_page 500 502 503 504 @handle_error;

    location @handle_error {
        default_type application/json;
        
        # Log error details
        access_log /var/log/nginx/error_details.log error_log_format;
        
        # Return error response
        return 500 '{"error":"Internal Server Error","status":500}';
    }

    # Route to different backends
    location /api/ai-ml/ {
        proxy_pass http://django:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/web/ {
        proxy_pass http://laravel:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/geo/ {
        proxy_pass http://java:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Database Initialization

### PostgreSQL Setup

```bash
# Connect to PostgreSQL
psql -U postgres -d feeding_hearts_db

# Run the error logging schema
\i database/postgres/error-logging-schema.sql

# Verify tables created
\dt error_logging.*

# Check views
\dv error_logging.*
```

### MongoDB Setup

```bash
# Connect to MongoDB
mongosh mongodb://admin:password@localhost:27017

# Switch to error database
use feeding_hearts_errors

# Run the error logging schema
load('/path/to/database/mongodb/error-logging-schema.js')

# Verify collections
db.getCollectionNames()

# Check indexes
db.error_logs.getIndexes()
```

---

## Celery Beat Scheduled Tasks

### Add to Django Admin (`feeding_hearts/celery.py`)

```python
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feeding_hearts.settings')

app = Celery('feeding_hearts')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

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
    'generate-daily-error-summary': {
        'task': 'error_logging.tasks.generate_daily_error_summary',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    'check-error-thresholds': {
        'task': 'error_logging.tasks.check_error_thresholds',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

---

## Monitoring & Observability

### Health Check Endpoints

```bash
# Django API health
curl http://localhost:8000/api/error-logging/webhook/health/

# PostgreSQL connection
psql -U postgres -d feeding_hearts_db -c "SELECT 1"

# MongoDB connection
mongosh --eval "db.adminCommand('ping')"

# Redis connection
redis-cli ping

# Celery task queue
celery -A feeding_hearts inspect active
```

### Prometheus Metrics (Optional)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

---

## Security Checklist

- [ ] Set strong database passwords
- [ ] Configure HTTPS/TLS for API endpoints
- [ ] Enable CORS only for trusted domains
- [ ] Rotate API keys and tokens regularly
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting on webhook endpoints
- [ ] Enable database encryption at rest
- [ ] Configure backup strategy
- [ ] Set up audit logging
- [ ] Monitor for suspicious error patterns
- [ ] Review and sanitize error messages
- [ ] Implement PII redaction in error logs
- [ ] Set up firewall rules for database access
- [ ] Configure VPN/SSH access for databases
- [ ] Enable database query logging

---

## Deployment Checklist

### Pre-Deployment
- [ ] Database migrations tested locally
- [ ] All services can communicate
- [ ] Email/Slack/SMS credentials validated
- [ ] Celery workers starting successfully
- [ ] Error logging endpoints responding
- [ ] All environment variables set

### Deployment
- [ ] Build Docker images
- [ ] Deploy database containers
- [ ] Deploy application services
- [ ] Deploy Celery workers
- [ ] Deploy Celery beat scheduler
- [ ] Verify all services running

### Post-Deployment
- [ ] Test error logging endpoints
- [ ] Verify notifications being sent
- [ ] Check database connectivity
- [ ] Monitor Celery task queue
- [ ] Review logs for errors
- [ ] Test error escalation
- [ ] Verify pattern detection

---

## Performance Tuning

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX CONCURRENTLY idx_errors_service_severity 
ON error_logs(service, severity);

CREATE INDEX CONCURRENTLY idx_errors_timestamp_resolved 
ON error_logs(timestamp DESC, resolved);

CREATE INDEX CONCURRENTLY idx_errors_assigned_to 
ON error_logs(assigned_to);

-- Partition large tables by date
CREATE TABLE error_logs_2024_q1 
PARTITION OF error_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM error_logs 
WHERE service = 'django' AND severity = 'critical' 
ORDER BY timestamp DESC LIMIT 100;
```

### Caching Strategy

```python
# Cache error statistics
from django.views.decorators.cache import cache_page

@cache_page(15 * 60)  # Cache for 15 minutes
@api_view(['GET'])
def error_stats(request):
    # Calculate statistics
    pass

# Invalidate cache on new errors
from django.core.cache import cache

class ErrorLog(models.Model):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Invalidate stats cache
        cache.delete('error_stats')
```

---

## Troubleshooting Guide

### Common Issues

**Issue: Errors not being logged**
```bash
# Check middleware is enabled
grep "ErrorLoggingMiddleware" settings.py

# Check database connection
python manage.py dbshell
SELECT COUNT(*) FROM error_logging_errorlog;

# Check logs
tail -f /var/log/django/error.log
```

**Issue: Notifications not sending**
```bash
# Check Celery tasks
celery -A feeding_hearts inspect active
celery -A feeding_hearts inspect registered

# Test email configuration
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'noreply@feedinghearts.com', ['admin@feedinghearts.com'])

# Check Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_SLACK_WEBHOOK_URL
```

**Issue: High database storage**
```bash
# Run cleanup
python manage.py shell
from error_logging.tasks import clean_old_error_logs
clean_old_error_logs()

# Check database size
SELECT pg_size_pretty(pg_database_size('feeding_hearts_db'));
```

---

## Next Steps

1. Deploy error logging system to staging
2. Configure notification channels
3. Test error capture from all services
4. Verify escalation logic
5. Set up monitoring dashboards
6. Train development team on system
7. Configure on-call schedules
8. Monitor and optimize performance
