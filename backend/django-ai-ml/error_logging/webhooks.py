"""
Webhook handlers for receiving error reports from external services
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

from .middleware import (
    LaravelErrorNotifier, JavaServiceErrorNotifier,
    FrontendErrorNotifier, MobileAppErrorNotifier
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def laravel_error_webhook(request):
    """
    Webhook endpoint for Laravel service errors
    
    Expected payload:
    {
        "error_type": "ExceptionType",
        "message": "Error message",
        "severity": "high",
        "endpoint": "/api/endpoint",
        "code": 500,
        "stack_trace": "...",
        "context": {},
        "environment": "production"
    }
    """
    try:
        error_data = request.data
        result = LaravelErrorNotifier.process_error(error_data)
        
        logger.info(f"Laravel error logged: {result['error_id']}")
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to log Laravel error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def java_error_webhook(request):
    """
    Webhook endpoint for Java service errors
    
    Expected payload:
    {
        "errorType": "ExceptionType",
        "message": "Error message",
        "severity": "high",
        "endpoint": "/api/endpoint",
        "code": 500,
        "stackTrace": "...",
        "context": {},
        "environment": "production"
    }
    """
    try:
        error_data = request.data
        result = JavaServiceErrorNotifier.process_error(error_data)
        
        logger.info(f"Java error logged: {result['error_id']}")
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to log Java error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def frontend_error_webhook(request):
    """
    Webhook endpoint for frontend (React/Angular/Vue) errors
    
    Expected payload:
    {
        "service": "react|angular|vue",
        "errorType": "JSError",
        "message": "Error message",
        "severity": "high",
        "endpoint": "/path",
        "userAgent": "...",
        "url": "https://...",
        "source": "source.js",
        "lineno": 123,
        "colno": 45,
        "timestamp": "2024-01-01T12:00:00Z",
        "user_id": "user_uuid",
        "environment": "production"
    }
    """
    try:
        error_data = request.data
        result = FrontendErrorNotifier.process_error(error_data)
        
        logger.info(f"Frontend error logged: {result['error_id']}")
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to log frontend error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def mobile_error_webhook(request):
    """
    Webhook endpoint for mobile (Flutter) app errors
    
    Expected payload:
    {
        "error_type": "FlutterException",
        "message": "Error message",
        "severity": "high",
        "screen": "ScreenName",
        "device": "iPhone 12",
        "os": "iOS",
        "app_version": "1.0.0",
        "user_id": "user_uuid",
        "session_id": "session_uuid",
        "environment": "production"
    }
    """
    try:
        error_data = request.data
        result = MobileAppErrorNotifier.process_error(error_data)
        
        logger.info(f"Mobile error logged: {result['error_id']}")
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to log mobile error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def generic_error_webhook(request):
    """
    Generic webhook endpoint for any service
    
    Expected payload:
    {
        "service": "service_name",
        "error_type": "ExceptionType",
        "message": "Error message",
        "severity": "high",
        "endpoint": "/api/endpoint",
        "code": 500,
        "context": {},
        "environment": "production"
    }
    """
    try:
        from .models import ErrorLog
        
        error_data = request.data
        
        error = ErrorLog.objects.create(
            service=error_data.get('service', 'unknown'),
            severity=error_data.get('severity', 'medium'),
            error_type=error_data.get('error_type', 'Exception'),
            message=error_data.get('message', ''),
            code=error_data.get('code'),
            endpoint=error_data.get('endpoint'),
            stack_trace=error_data.get('stack_trace'),
            context=error_data.get('context', {}),
            environment=error_data.get('environment', 'production')
        )
        
        result = {
            'error_id': str(error.error_id),
            'status': 'logged',
            'timestamp': error.timestamp.isoformat(),
        }
        
        logger.info(f"Generic error logged from {error_data.get('service', 'unknown')}: {result['error_id']}")
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed to log error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_health(request):
    """Health check endpoint for webhook"""
    return Response({
        'status': 'healthy',
        'message': 'Error logging webhook is operational'
    })
