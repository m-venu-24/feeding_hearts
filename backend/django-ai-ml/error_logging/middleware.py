"""
Error Logging Middleware and Integrations
Automatic error capture for all services
"""

import logging
import traceback
import json
import uuid
from typing import Optional
from django.utils import timezone
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware:
    """
    Django middleware for automatic error logging
    
    Features:
    - Captures all exceptions
    - Logs HTTP 5xx errors
    - Tracks request/response context
    - Stores stack traces
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add request ID
        request.request_id = str(uuid.uuid4())
        
        try:
            response = self.get_response(request)
            
            # Log 5xx errors
            if response.status_code >= 500:
                self._log_response_error(request, response)
            
            return response
        except Exception as e:
            self._log_exception(request, e)
            
            # Return error response
            return JsonResponse({
                'error': 'Internal server error',
                'request_id': request.request_id
            }, status=500)
    
    def _log_response_error(self, request, response):
        """Log HTTP response error"""
        from .models import ErrorLog
        
        ErrorLog.objects.create(
            service='django',
            severity='high',
            error_type='HTTPError',
            message=f'HTTP {response.status_code} error',
            code=response.status_code,
            endpoint=request.path,
            request_id=request.request_id,
            user_id=request.user.id if request.user.is_authenticated else None,
            context={
                'method': request.method,
                'path': request.path,
                'ip_address': self._get_client_ip(request),
                'query_params': dict(request.GET.items()),
                'status_code': response.status_code,
            },
            environment='production'
        )
        
        logger.error(f"HTTP Error {response.status_code} at {request.path}")
    
    def _log_exception(self, request, exception):
        """Log uncaught exception"""
        from .models import ErrorLog
        
        ErrorLog.objects.create(
            service='django',
            severity='critical',
            error_type=type(exception).__name__,
            message=str(exception),
            endpoint=request.path,
            request_id=request.request_id,
            user_id=request.user.id if request.user.is_authenticated else None,
            stack_trace=traceback.format_exc(),
            context={
                'method': request.method,
                'path': request.path,
                'ip_address': self._get_client_ip(request),
                'query_params': dict(request.GET.items()) if request.GET else {},
            },
            environment='production'
        )
        
        logger.exception(f"Uncaught exception in {request.path}")
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class ErrorCaptureDecorator:
    """
    Decorator for capturing errors in Django views
    
    Usage:
    @error_capture_decorator
    def my_view(request):
        pass
    """
    
    def __init__(self, view_func):
        self.view_func = view_func
    
    def __call__(self, request, *args, **kwargs):
        try:
            return self.view_func(request, *args, **kwargs)
        except Exception as e:
            from .models import ErrorLog
            
            ErrorLog.objects.create(
                service='django',
                severity='high',
                error_type=type(e).__name__,
                message=str(e),
                endpoint=request.path,
                request_id=getattr(request, 'request_id', str(uuid.uuid4())),
                user_id=request.user.id if request.user.is_authenticated else None,
                stack_trace=traceback.format_exc(),
                context={
                    'method': request.method,
                    'path': request.path,
                    'view': self.view_func.__name__,
                },
            )
            
            logger.error(f"Error in view {self.view_func.__name__}: {str(e)}")
            raise


def error_capture_decorator(view_func):
    """Wrapper function for error capture decorator"""
    return ErrorCaptureDecorator(view_func)


class DjangoLoggerHandler(logging.Handler):
    """
    Custom logging handler for Django that logs to ErrorLog model
    
    Usage:
    handler = DjangoLoggerHandler()
    handler.setLevel(logging.WARNING)
    logger = logging.getLogger('myapp')
    logger.addHandler(handler)
    """
    
    def emit(self, record):
        """Emit a log record to ErrorLog model"""
        try:
            from .models import ErrorLog
            
            # Map logging levels to severity
            severity_map = {
                logging.CRITICAL: 'critical',
                logging.ERROR: 'high',
                logging.WARNING: 'medium',
                logging.INFO: 'low',
                logging.DEBUG: 'info',
            }
            
            severity = severity_map.get(record.levelno, 'medium')
            
            ErrorLog.objects.create(
                service=record.name,
                severity=severity,
                error_type=record.name,
                message=self.format(record),
                code=getattr(record, 'status_code', None),
                context={
                    'logger': record.name,
                    'function': record.funcName,
                    'line': record.lineno,
                    'module': record.module,
                },
                environment='production'
            )
        except Exception:
            # Don't raise exceptions in logging handlers
            self.handleError(record)


# ============== SERVICE-SPECIFIC INTEGRATIONS ==============

class LaravelErrorNotifier:
    """
    Integration for sending errors from Laravel service to error logging
    
    Usage:
    - Configure webhook in Laravel service to POST errors to:
      POST /api/error-logging/webhook/laravel/
    """
    
    @staticmethod
    def process_error(error_data: dict) -> dict:
        """Process error data from Laravel"""
        from .models import ErrorLog
        
        error = ErrorLog.objects.create(
            service='laravel',
            severity=error_data.get('severity', 'medium'),
            error_type=error_data.get('error_type', 'Exception'),
            message=error_data.get('message', ''),
            code=error_data.get('code'),
            endpoint=error_data.get('endpoint'),
            stack_trace=error_data.get('stack_trace'),
            context=error_data.get('context', {}),
            environment=error_data.get('environment', 'production')
        )
        
        return {
            'error_id': str(error.error_id),
            'status': 'logged',
            'timestamp': error.timestamp.isoformat(),
        }


class JavaServiceErrorNotifier:
    """
    Integration for sending errors from Java service to error logging
    
    Usage:
    - Configure webhook in Java service to POST errors to:
      POST /api/error-logging/webhook/java/
    """
    
    @staticmethod
    def process_error(error_data: dict) -> dict:
        """Process error data from Java service"""
        from .models import ErrorLog
        
        error = ErrorLog.objects.create(
            service='java',
            severity=error_data.get('severity', 'medium'),
            error_type=error_data.get('errorType', 'Exception'),
            message=error_data.get('message', ''),
            code=error_data.get('code'),
            endpoint=error_data.get('endpoint'),
            stack_trace=error_data.get('stackTrace'),
            context=error_data.get('context', {}),
            environment=error_data.get('environment', 'production')
        )
        
        return {
            'error_id': str(error.error_id),
            'status': 'logged',
            'timestamp': error.timestamp.isoformat(),
        }


class FrontendErrorNotifier:
    """
    Integration for sending errors from frontend services to error logging
    
    Usage:
    - Configure error handler in React/Angular/Vue to POST errors to:
      POST /api/error-logging/webhook/frontend/
    """
    
    @staticmethod
    def process_error(error_data: dict) -> dict:
        """Process error data from frontend"""
        from .models import ErrorLog
        
        frontend_service = error_data.get('service', 'frontend')
        if frontend_service not in ['react', 'angular', 'vue']:
            frontend_service = 'frontend'
        
        error = ErrorLog.objects.create(
            service=frontend_service,
            severity=error_data.get('severity', 'medium'),
            error_type=error_data.get('errorType', 'JSError'),
            message=error_data.get('message', ''),
            endpoint=error_data.get('endpoint'),
            context={
                'userAgent': error_data.get('userAgent'),
                'url': error_data.get('url'),
                'timestamp': error_data.get('timestamp'),
                'source': error_data.get('source'),
                'lineno': error_data.get('lineno'),
                'colno': error_data.get('colno'),
                'user_id': error_data.get('user_id'),
            },
            environment=error_data.get('environment', 'production')
        )
        
        return {
            'error_id': str(error.error_id),
            'status': 'logged',
            'timestamp': error.timestamp.isoformat(),
        }


class MobileAppErrorNotifier:
    """
    Integration for sending errors from Flutter mobile app to error logging
    
    Usage:
    - Configure Dart error handler to POST errors to:
      POST /api/error-logging/webhook/mobile/
    """
    
    @staticmethod
    def process_error(error_data: dict) -> dict:
        """Process error data from mobile app"""
        from .models import ErrorLog
        
        error = ErrorLog.objects.create(
            service='flutter',
            severity=error_data.get('severity', 'medium'),
            error_type=error_data.get('error_type', 'FlutterException'),
            message=error_data.get('message', ''),
            endpoint=error_data.get('screen'),
            context={
                'device': error_data.get('device'),
                'os': error_data.get('os'),
                'app_version': error_data.get('app_version'),
                'user_id': error_data.get('user_id'),
                'session_id': error_data.get('session_id'),
            },
            environment=error_data.get('environment', 'production')
        )
        
        return {
            'error_id': str(error.error_id),
            'status': 'logged',
            'timestamp': error.timestamp.isoformat(),
        }
