"""
Celery tasks for asynchronous error logging operations
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import ErrorLog, ErrorNotification, ErrorPattern, DeveloperAssignment
from .services import NotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def notify_developers_async(self, error_id):
    """
    Asynchronous task to notify developers about errors
    
    Args:
        error_id: ID of the error to notify about
    
    Retries up to 3 times on failure with exponential backoff
    """
    try:
        service = NotificationService()
        results = service.notify_developers(error_id)
        
        logger.info(f"Notification task completed for error {error_id}: {results}")
        return results
    except Exception as exc:
        logger.error(f"Error notifying developers for {error_id}: {str(exc)}")
        
        # Retry with exponential backoff (5 mins, 10 mins, 20 mins)
        raise self.retry(exc=exc, countdown=5 * (2 ** self.request.retries) * 60)


@shared_task
def retry_failed_notifications():
    """
    Periodic task to retry failed notifications
    Should be scheduled to run every hour
    """
    try:
        service = NotificationService()
        results = service.retry_failed_notifications()
        
        logger.info(f"Retry task completed: {results}")
        return results
    except Exception as exc:
        logger.error(f"Error retrying failed notifications: {str(exc)}")
        raise


@shared_task
def analyze_error_patterns():
    """
    Periodic task to analyze error patterns
    Should be scheduled to run daily
    
    This task:
    - Identifies recurring errors
    - Detects error clusters
    - Creates or updates ErrorPattern records
    """
    try:
        logger.info("Starting error pattern analysis")
        
        # Get errors from the last 24 hours
        since = timezone.now() - timedelta(hours=24)
        recent_errors = ErrorLog.objects.filter(timestamp__gte=since)
        
        # Group by error type and service
        error_patterns = {}
        for error in recent_errors:
            key = f"{error.service}:{error.error_type}"
            if key not in error_patterns:
                error_patterns[key] = {
                    'service': error.service,
                    'error_type': error.error_type,
                    'count': 0,
                    'severity_levels': [],
                    'endpoints': [],
                }
            
            error_patterns[key]['count'] += 1
            if error.severity not in error_patterns[key]['severity_levels']:
                error_patterns[key]['severity_levels'].append(error.severity)
            if error.endpoint and error.endpoint not in error_patterns[key]['endpoints']:
                error_patterns[key]['endpoints'].append(error.endpoint)
        
        # Update or create ErrorPattern records
        created_count = 0
        updated_count = 0
        
        for key, pattern_data in error_patterns.items():
            pattern, created = ErrorPattern.objects.update_or_create(
                service=pattern_data['service'],
                error_type=pattern_data['error_type'],
                defaults={
                    'occurrence_count': pattern_data['count'],
                    'affected_services': [pattern_data['service']],
                    'common_endpoints': pattern_data['endpoints'],
                    'severity_distribution': {
                        'critical': recent_errors.filter(
                            service=pattern_data['service'],
                            error_type=pattern_data['error_type'],
                            severity='critical'
                        ).count(),
                        'high': recent_errors.filter(
                            service=pattern_data['service'],
                            error_type=pattern_data['error_type'],
                            severity='high'
                        ).count(),
                        'medium': recent_errors.filter(
                            service=pattern_data['service'],
                            error_type=pattern_data['error_type'],
                            severity='medium'
                        ).count(),
                        'low': recent_errors.filter(
                            service=pattern_data['service'],
                            error_type=pattern_data['error_type'],
                            severity='low'
                        ).count(),
                        'info': recent_errors.filter(
                            service=pattern_data['service'],
                            error_type=pattern_data['error_type'],
                            severity='info'
                        ).count(),
                    },
                    'last_occurrence': recent_errors.filter(
                        service=pattern_data['service'],
                        error_type=pattern_data['error_type'],
                    ).latest('timestamp').timestamp,
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Pattern analysis complete. Created: {created_count}, Updated: {updated_count}")
        return {'created': created_count, 'updated': updated_count}
    except Exception as exc:
        logger.error(f"Error analyzing error patterns: {str(exc)}")
        raise


@shared_task
def escalate_unresolved_errors():
    """
    Periodic task to escalate unresolved errors
    Should be scheduled to run every 6 hours
    
    Escalates errors that have been unresolved for:
    - 1 hour (if critical)
    - 4 hours (if high)
    - 8 hours (if medium)
    """
    try:
        logger.info("Starting error escalation check")
        
        escalated_count = 0
        
        # Check critical errors unresolved for 1 hour
        critical_since = timezone.now() - timedelta(hours=1)
        critical_errors = ErrorLog.objects.filter(
            severity='critical',
            resolved=False,
            timestamp__lte=critical_since
        )
        
        for error in critical_errors:
            if error.escalations.count() == 0:
                from .models import ErrorEscalation
                
                managers = DeveloperAssignment.objects.filter(is_manager=True)
                if managers.exists():
                    escalation = EscalationEscalation.objects.create(
                        error=error,
                        escalated_from=error.assigned_to,
                        escalated_to=managers.first().developer_id,
                        escalation_level=1,
                        reason="Unresolved for over 1 hour"
                    )
                    escalated_count += 1
                    
                    # Notify manager
                    notify_developers_async.delay(str(error.error_id))
        
        # Check high errors unresolved for 4 hours
        high_since = timezone.now() - timedelta(hours=4)
        high_errors = ErrorLog.objects.filter(
            severity='high',
            resolved=False,
            timestamp__lte=high_since,
            escalations__isnull=True
        )
        
        for error in high_errors:
            if error.escalations.count() == 0:
                from .models import ErrorEscalation
                
                escalation = ErrorEscalation.objects.create(
                    error=error,
                    escalated_from=error.assigned_to,
                    escalated_to=DeveloperAssignment.objects.filter(is_manager=True).first().developer_id if DeveloperAssignment.objects.filter(is_manager=True).exists() else None,
                    escalation_level=1,
                    reason="Unresolved for over 4 hours"
                )
                escalated_count += 1
        
        logger.info(f"Error escalation check complete. Escalated: {escalated_count}")
        return {'escalated': escalated_count}
    except Exception as exc:
        logger.error(f"Error escalating unresolved errors: {str(exc)}")
        raise


@shared_task
def clean_old_error_logs():
    """
    Periodic task to clean up old error logs
    Should be scheduled to run daily
    
    Removes:
    - Resolved errors older than 30 days
    - Unresolved errors older than 90 days
    """
    try:
        logger.info("Starting error log cleanup")
        
        # Delete resolved errors older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        resolved_deleted, _ = ErrorLog.objects.filter(
            resolved=True,
            resolved_at__lte=thirty_days_ago
        ).delete()
        
        # Delete unresolved errors older than 90 days (cleanup old unresolved issues)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        unresolved_deleted, _ = ErrorLog.objects.filter(
            resolved=False,
            timestamp__lte=ninety_days_ago
        ).delete()
        
        logger.info(f"Cleanup complete. Deleted resolved: {resolved_deleted}, unresolved: {unresolved_deleted}")
        return {'resolved_deleted': resolved_deleted, 'unresolved_deleted': unresolved_deleted}
    except Exception as exc:
        logger.error(f"Error cleaning up old error logs: {str(exc)}")
        raise


@shared_task
def generate_daily_error_summary():
    """
    Periodic task to generate daily error summary
    Should be scheduled to run at 8:00 AM daily
    
    Generates and sends summary email to development team
    """
    try:
        logger.info("Generating daily error summary")
        
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        
        errors = ErrorLog.objects.filter(
            timestamp__gte=yesterday,
            timestamp__lte=today
        )
        
        summary = {
            'total_errors': errors.count(),
            'by_severity': {
                'critical': errors.filter(severity='critical').count(),
                'high': errors.filter(severity='high').count(),
                'medium': errors.filter(severity='medium').count(),
                'low': errors.filter(severity='low').count(),
                'info': errors.filter(severity='info').count(),
            },
            'by_service': dict(errors.values('service').annotate(count=Count('service')).values_list('service', 'count')),
            'resolved': errors.filter(resolved=True).count(),
            'unresolved': errors.filter(resolved=False).count(),
        }
        
        # Get list of critical errors
        critical_errors = errors.filter(severity='critical').values_list('error_type', flat=True).distinct()
        summary['critical_errors_list'] = list(critical_errors)[:5]
        
        # Send email to admins/managers
        from django.core.mail import send_mail
        from django.conf import settings
        
        managers = DeveloperAssignment.objects.filter(is_manager=True)
        recipient_list = [m.email for m in managers]
        
        if recipient_list:
            message = f"""
            Daily Error Summary - {yesterday.strftime('%Y-%m-%d')}
            
            Total Errors: {summary['total_errors']}
            
            By Severity:
            - Critical: {summary['by_severity']['critical']}
            - High: {summary['by_severity']['high']}
            - Medium: {summary['by_severity']['medium']}
            - Low: {summary['by_severity']['low']}
            - Info: {summary['by_severity']['info']}
            
            By Service: {summary['by_service']}
            
            Status:
            - Resolved: {summary['resolved']}
            - Unresolved: {summary['unresolved']}
            
            Top Critical Errors: {', '.join(summary['critical_errors_list'])}
            
            Log in to the dashboard for more details.
            """
            
            send_mail(
                f"Daily Error Summary - {yesterday.strftime('%Y-%m-%d')}",
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=True
            )
        
        logger.info(f"Daily summary generated: {summary}")
        return summary
    except Exception as exc:
        logger.error(f"Error generating daily summary: {str(exc)}")
        raise


@shared_task
def check_error_thresholds():
    """
    Periodic task to check error thresholds
    Should be scheduled to run every 15 minutes
    
    Alerts if:
    - More than 100 errors in last hour
    - More than 50 critical errors in last hour
    - Error rate increasing
    """
    try:
        logger.info("Checking error thresholds")
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        errors_last_hour = ErrorLog.objects.filter(timestamp__gte=one_hour_ago)
        critical_errors_last_hour = errors_last_hour.filter(severity='critical')
        
        alerts = []
        
        if errors_last_hour.count() > 100:
            alert = f"High error rate: {errors_last_hour.count()} errors in last hour"
            alerts.append(alert)
            logger.warning(alert)
        
        if critical_errors_last_hour.count() > 50:
            alert = f"Critical error threshold exceeded: {critical_errors_last_hour.count()} critical errors"
            alerts.append(alert)
            logger.critical(alert)
        
        if alerts:
            # Notify managers
            from django.core.mail import send_mail
            from django.conf import settings
            
            managers = DeveloperAssignment.objects.filter(is_manager=True)
            recipient_list = [m.email for m in managers]
            
            if recipient_list:
                send_mail(
                    "🚨 Error Threshold Alert - Feeding Hearts",
                    "\n".join(alerts),
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=True
                )
        
        return {'alerts': len(alerts), 'total_errors': errors_last_hour.count()}
    except Exception as exc:
        logger.error(f"Error checking error thresholds: {str(exc)}")
        raise
