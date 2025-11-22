"""
AI-Powered Error Recovery Middleware
Automatically detects errors and applies ML-based recovery strategies
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
from functools import wraps

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.decorators import decorator_from_middleware_with_args
from django.utils import timezone
from django.conf import settings
from django.db.models import Count

from .models import ErrorLog
from .ai_error_recovery import ErrorAnalyzer, AutoRecoveryExecutor, ErrorAlertManager

logger = logging.getLogger(__name__)


class AIErrorRecoveryMiddleware:
    """
    Middleware for automatic error detection and AI-powered recovery
    
    Features:
    - Catches all exceptions in the request lifecycle
    - Analyzes errors using ML models
    - Executes automatic recovery strategies
    - Logs and alerts developers
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and handle errors"""
        try:
            response = self.get_response(request)
            
            # Check for HTTP error responses
            if response.status_code >= 400:
                self._handle_http_error(request, response)
            
            return response
            
        except Exception as exc:
            return self._handle_exception(request, exc)
        except:
            return self._handle_exception(request, Exception("Unknown error"))
    
    def _handle_http_error(
        self,
        request: HttpRequest,
        response: HttpResponse
    ) -> None:
        """Handle HTTP error responses"""
        status_code = response.status_code
        
        # Determine severity
        if status_code >= 500:
            severity = 'critical'
        elif status_code >= 400:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Log the error
        error_log = self._create_error_log(
            request=request,
            error_type=f'HTTP{status_code}',
            message=f'HTTP {status_code} Error',
            severity=severity,
            context={'status_code': status_code, 'response': str(response)},
        )
        
        # Trigger recovery for severe errors
        if status_code >= 500:
            self._trigger_ai_recovery(error_log, request)
    
    def _handle_exception(
        self,
        request: HttpRequest,
        exc: Exception
    ) -> HttpResponse:
        """Handle application exceptions"""
        
        # Determine error type and severity
        error_type = type(exc).__name__
        severity = self._determine_severity(error_type, exc)
        
        # Create error log
        error_log = self._create_error_log(
            request=request,
            error_type=error_type,
            message=str(exc),
            severity=severity,
            context={
                'exception_type': error_type,
                'traceback': traceback.format_exc(),
                'request_path': request.path,
                'request_method': request.method,
            },
            stack_trace=traceback.format_exc(),
        )
        
        # Trigger AI recovery
        recovery_result = self._trigger_ai_recovery(error_log, request)
        
        # Generate response
        response_data = {
            'error': {
                'type': error_type,
                'message': str(exc),
                'error_id': str(error_log.error_id),
                'severity': severity,
            },
            'recovery': recovery_result,
        }
        
        # Determine HTTP status code
        status_code = self._get_status_code(error_type, severity)
        
        return JsonResponse(response_data, status=status_code)
    
    def _create_error_log(
        self,
        request: HttpRequest,
        error_type: str,
        message: str,
        severity: str,
        context: dict,
        stack_trace: Optional[str] = None,
    ) -> ErrorLog:
        """Create error log in database"""
        try:
            service = self._get_service_from_request(request)
            environment = getattr(settings, 'ENVIRONMENT', 'production')
            
            error_log = ErrorLog.objects.create(
                service=service,
                error_type=error_type,
                message=message,
                severity=severity,
                endpoint=request.path,
                context=context,
                stack_trace=stack_trace,
                environment=environment,
                user_id=getattr(request.user, 'id', None),
                request_id=getattr(request, 'request_id', None),
            )
            
            logger.info(f"Error logged: {error_log.error_id}")
            return error_log
            
        except Exception as e:
            logger.error(f"Failed to create error log: {str(e)}")
            raise
    
    def _trigger_ai_recovery(
        self,
        error_log: ErrorLog,
        request: HttpRequest,
    ) -> dict:
        """Trigger AI-powered recovery"""
        try:
            # Analyze error
            analyzer = ErrorAnalyzer(error_log)
            analysis = analyzer.analyze_error()
            
            # Execute recovery
            executor = AutoRecoveryExecutor(error_log)
            execution = executor.execute_recovery(analysis)
            
            # Send alerts
            alert_manager = ErrorAlertManager(error_log)
            alert_manager.send_recovery_alert(analysis, execution)
            
            logger.info(
                f"Recovery executed for {error_log.error_id}: "
                f"Success={execution['recovery_success']}"
            )
            
            return {
                'attempted': True,
                'success': execution['recovery_success'],
                'message': execution['recovery_message'],
                'actions': [
                    {
                        'strategy': a['strategy'],
                        'success': a['success'],
                    }
                    for a in execution.get('actions_executed', [])
                ],
            }
            
        except Exception as e:
            logger.error(f"Error during AI recovery: {str(e)}")
            return {
                'attempted': False,
                'success': False,
                'message': f'Recovery failed: {str(e)}',
                'actions': [],
            }
    
    def _determine_severity(self, error_type: str, exc: Exception) -> str:
        """Determine error severity"""
        critical_errors = [
            'DatabaseError',
            'OutOfMemoryError',
            'SystemError',
            'AssertionError',
        ]
        
        high_errors = [
            'TimeoutError',
            'ConnectionError',
            'IOError',
            'OSError',
        ]
        
        medium_errors = [
            'ValueError',
            'KeyError',
            'AttributeError',
            'TypeError',
        ]
        
        if error_type in critical_errors:
            return 'critical'
        elif error_type in high_errors:
            return 'high'
        elif error_type in medium_errors:
            return 'medium'
        else:
            return 'low'
    
    def _get_service_from_request(self, request: HttpRequest) -> str:
        """Determine service from request"""
        # Check for service header
        service = request.META.get('HTTP_X_SERVICE', 'django')
        
        # Map to valid choices
        valid_services = [
            'django', 'laravel', 'java', 'react', 
            'angular', 'vue', 'flutter', 'nginx'
        ]
        
        return service if service in valid_services else 'django'
    
    def _get_status_code(self, error_type: str, severity: str) -> int:
        """Get appropriate HTTP status code"""
        if severity == 'critical':
            return 500
        elif severity == 'high':
            return 503
        elif severity == 'medium':
            return 400
        else:
            return 400


def ai_error_handler(func: Callable) -> Callable:
    """
    Decorator for AI-powered error handling on specific views
    
    Usage:
        @ai_error_handler
        def my_view(request):
            ...
    """
    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            return func(request, *args, **kwargs)
        except Exception as exc:
            middleware = AIErrorRecoveryMiddleware(lambda r: HttpResponse())
            return middleware._handle_exception(request, exc)
    
    return wrapper


class ErrorRecoveryContextManager:
    """
    Context manager for error recovery in specific code blocks
    
    Usage:
        with ErrorRecoveryContextManager(service='django'):
            # risky code
            pass
    """
    
    def __init__(self, service: str = 'django', timeout: int = 5000):
        self.service = service
        self.timeout = timeout
        self.error_log = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        
        # Handle exception
        error_type = exc_type.__name__
        message = str(exc_val)
        
        try:
            # Create error log
            self.error_log = ErrorLog.objects.create(
                service=self.service,
                error_type=error_type,
                message=message,
                severity='high',
                environment=getattr(settings, 'ENVIRONMENT', 'production'),
                stack_trace=traceback.format_exc(),
            )
            
            # Analyze and recover
            analyzer = ErrorAnalyzer(self.error_log)
            analysis = analyzer.analyze_error()
            
            executor = AutoRecoveryExecutor(self.error_log)
            execution = executor.execute_recovery(analysis)
            
            logger.info(
                f"Context recovery for {error_type}: "
                f"Success={execution['recovery_success']}"
            )
            
            # Suppress exception if recovery successful
            return execution['recovery_success']
            
        except Exception as e:
            logger.error(f"Error in context recovery: {str(e)}")
            return False


# Utility functions for error recovery

def get_error_summary(service: str, hours: int = 24) -> dict:
    """Get error summary for a service"""
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    errors = ErrorLog.objects.filter(
        service=service,
        timestamp__gte=cutoff_time
    )
    
    return {
        'total_errors': errors.count(),
        'critical_errors': errors.filter(severity='critical').count(),
        'high_errors': errors.filter(severity='high').count(),
        'unresolved_errors': errors.filter(resolved=False).count(),
        'error_types': list(
            errors.values('error_type').annotate(
                count=Count('id')
            ).order_by('-count')
        ),
    }


def trigger_manual_recovery(error_id: str) -> dict:
    """Manually trigger recovery for a specific error"""
    try:
        error_log = ErrorLog.objects.get(error_id=error_id)
        
        analyzer = ErrorAnalyzer(error_log)
        analysis = analyzer.analyze_error()
        
        executor = AutoRecoveryExecutor(error_log)
        execution = executor.execute_recovery(analysis)
        
        alert_manager = ErrorAlertManager(error_log)
        alert_manager.send_recovery_alert(analysis, execution)
        
        return {
            'success': True,
            'error_id': error_id,
            'recovery': execution,
        }
        
    except ErrorLog.DoesNotExist:
        logger.error(f"Error not found: {error_id}")
        return {
            'success': False,
            'error': f'Error not found: {error_id}',
        }
    except Exception as e:
        logger.error(f"Manual recovery failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
        }
