"""
Error Logging API Views
Provides endpoints for error logging, querying, and notifications
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import logging

from .models import (
    ErrorLog, ErrorNotification, DeveloperAssignment, 
    ErrorPattern, ErrorEscalation
)
from .serializers import (
    ErrorLogSerializer, ErrorNotificationSerializer,
    DeveloperAssignmentSerializer, ErrorPatternSerializer
)

logger = logging.getLogger(__name__)


class ErrorLogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ErrorLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Error Logging
    
    Endpoints:
    - GET /errors/ - List all errors
    - POST /errors/ - Log new error
    - GET /errors/{id}/ - Get error details
    - PATCH /errors/{id}/ - Update error
    - POST /errors/{id}/resolve/ - Mark as resolved
    - POST /errors/{id}/assign/ - Assign to developer
    - POST /errors/{id}/escalate/ - Escalate error
    - GET /errors/stats/ - Get error statistics
    - GET /errors/recent/ - Get recent errors
    - GET /errors/critical/ - Get critical errors
    """
    
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    pagination_class = ErrorLogPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'severity', 'resolved', 'environment', 'assigned_to']
    search_fields = ['message', 'error_type', 'endpoint']
    ordering_fields = ['timestamp', 'severity', 'created_at']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter by date range if provided"""
        queryset = super().get_queryset()
        
        days = self.request.query_params.get('days', None)
        if days:
            date_since = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(timestamp__gte=date_since)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Log new error"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Check if notification should be sent
        error = serializer.instance
        if error.severity in ['critical', 'high']:
            from .tasks import notify_developers_async
            notify_developers_async.delay(str(error.error_id))
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark error as resolved"""
        error = self.get_object()
        
        resolved_by = request.data.get('resolved_by', 'system')
        notes = request.data.get('notes', '')
        
        error.mark_resolved(resolved_by, notes)
        
        return Response(
            {'message': 'Error marked as resolved', 'resolved_at': error.resolved_at},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign error to developer"""
        error = self.get_object()
        developer_id = request.data.get('developer_id')
        
        if not developer_id:
            return Response(
                {'error': 'developer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            developer = DeveloperAssignment.objects.get(developer_id=developer_id)
            error.assign_to_developer(str(developer.developer_id))
            developer.current_load = developer.errorlog_set.filter(resolved=False).count()
            developer.save()
            
            return Response(
                {'message': f'Error assigned to {developer.name}'},
                status=status.HTTP_200_OK
            )
        except DeveloperAssignment.DoesNotExist:
            return Response(
                {'error': 'Developer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate error to higher level"""
        error = self.get_object()
        escalated_to = request.data.get('escalated_to')
        reason = request.data.get('reason', '')
        
        escalation = ErrorEscalation.objects.create(
            error=error,
            escalated_from=error.assigned_to,
            escalated_to=escalated_to,
            escalation_level=(error.escalations.count() + 1),
            reason=reason
        )
        
        # Notify escalated developer
        from .tasks import notify_developers_async
        notify_developers_async.delay(str(error.error_id))
        
        return Response(
            {'message': 'Error escalated', 'escalation_id': str(escalation.escalation_id)},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get error statistics"""
        days = int(request.query_params.get('days', 7))
        date_since = timezone.now() - timedelta(days=days)
        
        errors = ErrorLog.objects.filter(timestamp__gte=date_since)
        
        stats = {
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
            'avg_resolution_hours': 0,
        }
        
        # Calculate average resolution time
        resolved_errors = errors.filter(resolved=True, resolved_at__isnull=False)
        if resolved_errors.exists():
            total_time = sum([
                (e.resolved_at - e.timestamp).total_seconds() 
                for e in resolved_errors
            ])
            stats['avg_resolution_hours'] = total_time / (resolved_errors.count() * 3600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent errors (last 24 hours)"""
        date_since = timezone.now() - timedelta(hours=24)
        errors = ErrorLog.objects.filter(timestamp__gte=date_since).order_by('-timestamp')
        
        serializer = self.get_serializer(errors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical unresolved errors"""
        errors = ErrorLog.objects.filter(
            severity='critical',
            resolved=False
        ).order_by('-timestamp')
        
        serializer = self.get_serializer(errors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_service(self, request):
        """Get error summary by service"""
        service = request.query_params.get('service')
        
        if not service:
            return Response(
                {'error': 'service parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        errors = ErrorLog.objects.filter(service=service)
        
        summary = {
            'service': service,
            'total': errors.count(),
            'by_severity': {
                'critical': errors.filter(severity='critical').count(),
                'high': errors.filter(severity='high').count(),
                'medium': errors.filter(severity='medium').count(),
                'low': errors.filter(severity='low').count(),
                'info': errors.filter(severity='info').count(),
            },
            'recent': ErrorLogSerializer(
                errors.order_by('-timestamp')[:10], many=True
            ).data
        }
        
        return Response(summary)


class DeveloperAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Developer Assignment Management
    
    Endpoints:
    - GET /developers/ - List all developers
    - POST /developers/ - Create new developer assignment
    - GET /developers/{id}/ - Get developer details
    - PATCH /developers/{id}/ - Update developer
    - DELETE /developers/{id}/ - Remove developer
    - GET /developers/workload/ - Get developer workload
    - POST /developers/{id}/on-call/ - Set on-call status
    """
    
    queryset = DeveloperAssignment.objects.all()
    serializer_class = DeveloperAssignmentSerializer
    ordering = ['on_call', 'current_load']
    
    @action(detail=False, methods=['get'])
    def workload(self, request):
        """Get developer workload"""
        developers = DeveloperAssignment.objects.all()
        
        workload = []
        for dev in developers:
            errors = ErrorLog.objects.filter(assigned_to=str(dev.developer_id))
            workload.append({
                'developer': DeveloperAssignmentSerializer(dev).data,
                'assigned_errors': errors.count(),
                'unresolved_errors': errors.filter(resolved=False).count(),
                'critical_errors': errors.filter(severity='critical', resolved=False).count(),
            })
        
        return Response(workload)
    
    @action(detail=True, methods=['post'])
    def on_call(self, request, pk=None):
        """Set developer on-call status"""
        developer = self.get_object()
        on_call = request.data.get('on_call', False)
        
        developer.on_call = on_call
        developer.save()
        
        return Response(
            {'message': f'Developer set to {"on-call" if on_call else "off-call"}'},
            status=status.HTTP_200_OK
        )


class ErrorPatternViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Error Patterns
    
    Endpoints:
    - GET /patterns/ - List error patterns
    - GET /patterns/{id}/ - Get pattern details
    """
    
    queryset = ErrorPattern.objects.all()
    serializer_class = ErrorPatternSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'error_type']
    ordering = ['-occurrence_count']


class ErrorNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Error Notifications
    
    Endpoints:
    - GET /notifications/ - List notifications
    - GET /notifications/{id}/ - Get notification details
    - POST /notifications/{id}/mark-read/ - Mark as read
    """
    
    queryset = ErrorNotification.objects.all()
    serializer_class = ErrorNotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'channel']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()
        
        return Response(
            {'message': 'Notification marked as read'},
            status=status.HTTP_200_OK
        )


# ============== ERROR LOGGING MIDDLEWARE ==============

class ErrorLoggingMiddleware:
    """Middleware to automatically log errors"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            
            # Log 5xx errors
            if response.status_code >= 500:
                self.log_response_error(request, response)
            
            return response
        except Exception as e:
            self.log_exception(request, e)
            raise
    
    def log_response_error(self, request, response):
        """Log response error"""
        ErrorLog.objects.create(
            service='django',
            severity='high',
            error_type='HTTPError',
            message=f'HTTP {response.status_code} error',
            code=response.status_code,
            endpoint=request.path,
            request_id=getattr(request, 'request_id', None),
            user_id=request.user.id if request.user.is_authenticated else None,
            context={
                'method': request.method,
                'path': request.path,
                'ip_address': self.get_client_ip(request),
            },
            environment='production'
        )
    
    def log_exception(self, request, exception):
        """Log exception"""
        import traceback
        
        ErrorLog.objects.create(
            service='django',
            severity='critical',
            error_type=type(exception).__name__,
            message=str(exception),
            endpoint=request.path,
            request_id=getattr(request, 'request_id', None),
            user_id=request.user.id if request.user.is_authenticated else None,
            stack_trace=traceback.format_exc(),
            context={
                'method': request.method,
                'path': request.path,
                'ip_address': self.get_client_ip(request),
            },
            environment='production'
        )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
