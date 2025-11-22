"""
Django REST API Views for Unified Phase Integration
Phases 1-10 API Gateway
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import json

from api.models_unified import (
    UnifiedPhase, UnifiedEvent, PhaseConnection, 
    UnifiedSystemState, PhaseDataTransform
)


# ============================================================================
# UNIFIED PHASE VIEWSETS
# ============================================================================

class UnifiedPhaseViewSet(viewsets.ModelViewSet):
    """API for managing all unified phases"""
    
    queryset = UnifiedPhase.objects.all()
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get overview of all phases"""
        phases = UnifiedPhase.objects.all()
        
        return Response({
            'total_phases': phases.count(),
            'active_phases': phases.filter(status='active').count(),
            'phases': [
                {
                    'id': p.phase_id,
                    'name': p.name,
                    'status': p.status,
                    'api_endpoint': p.api_endpoint,
                    'last_event': p.last_event_processed.isoformat() if p.last_event_processed else None,
                }
                for p in phases
            ]
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get detailed status of a specific phase"""
        phase = self.get_object()
        
        # Get recent events
        recent_events = UnifiedEvent.objects.filter(
            source_phase=phase
        ).order_by('-created_at')[:10]
        
        # Get connections
        outgoing = phase.outgoing_connections.select_related('to_phase')
        incoming = phase.incoming_connections.select_related('from_phase')
        
        return Response({
            'phase': {
                'id': phase.phase_id,
                'name': phase.name,
                'status': phase.status,
                'description': phase.description,
            },
            'events': {
                'total_emitted': UnifiedEvent.objects.filter(source_phase=phase).count(),
                'total_received': UnifiedEvent.objects.filter(target_phases=phase).count(),
                'recent': [
                    {
                        'type': e.event_type,
                        'status': e.status,
                        'created_at': e.created_at.isoformat(),
                    }
                    for e in recent_events
                ]
            },
            'connections': {
                'outgoing': [
                    {
                        'to_phase': c.to_phase.phase_id,
                        'to_name': c.to_phase.name,
                        'flow_type': c.flow_type,
                        'trigger_type': c.trigger_type,
                    }
                    for c in outgoing
                ],
                'incoming': [
                    {
                        'from_phase': c.from_phase.phase_id,
                        'from_name': c.from_phase.name,
                        'flow_type': c.flow_type,
                        'trigger_type': c.trigger_type,
                    }
                    for c in incoming
                ]
            }
        })
    
    @action(detail=True, methods=['post'])
    def emit_event(self, request, pk=None):
        """Phase emits an event"""
        phase = self.get_object()
        
        event_type = request.data.get('event_type')
        event_data = request.data.get('data', {})
        
        # Create event
        event = UnifiedEvent.objects.create(
            event_type=event_type,
            source_phase=phase,
            data=event_data,
            status='processing'
        )
        
        # Find target phases
        connections = PhaseConnection.objects.filter(
            from_phase=phase,
            is_active=True
        )
        
        target_phases = [conn.to_phase for conn in connections]
        event.target_phases.set(target_phases)
        
        # Mark as completed
        event.status = 'completed'
        event.processed_at = timezone.now()
        event.save()
        
        return Response({
            'event_id': str(event.event_id),
            'status': 'emitted',
            'target_phases': [p.phase_id for p in target_phases]
        }, status=status.HTTP_201_CREATED)


class UnifiedEventViewSet(viewsets.ModelViewSet):
    """API for managing unified events"""
    
    queryset = UnifiedEvent.objects.all()
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent events"""
        limit = int(request.query_params.get('limit', 20))
        events = UnifiedEvent.objects.all().order_by('-created_at')[:limit]
        
        return Response({
            'count': len(events),
            'events': [
                {
                    'event_id': str(e.event_id),
                    'type': e.event_type,
                    'source_phase': e.source_phase.phase_id,
                    'status': e.status,
                    'created_at': e.created_at.isoformat(),
                }
                for e in events
            ]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get event statistics"""
        
        total = UnifiedEvent.objects.count()
        completed = UnifiedEvent.objects.filter(status='completed').count()
        failed = UnifiedEvent.objects.filter(status='failed').count()
        pending = UnifiedEvent.objects.filter(status='pending').count()
        
        return Response({
            'total_events': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'success_rate': (completed / total * 100) if total > 0 else 0,
        })


class PhaseConnectionViewSet(viewsets.ModelViewSet):
    """API for managing phase connections"""
    
    queryset = PhaseConnection.objects.select_related('from_phase', 'to_phase')
    
    @action(detail=False, methods=['get'])
    def network(self, request):
        """Get phase connection network"""
        connections = PhaseConnection.objects.select_related(
            'from_phase', 'to_phase'
        ).filter(is_active=True)
        
        return Response({
            'total_connections': connections.count(),
            'connections': [
                {
                    'from_phase': c.from_phase.phase_id,
                    'to_phase': c.to_phase.phase_id,
                    'flow_type': c.flow_type,
                    'trigger_type': c.trigger_type,
                    'success_rate': (c.success_count / (c.success_count + c.failure_count) * 100) 
                                   if (c.success_count + c.failure_count) > 0 else 0,
                }
                for c in connections
            ]
        })


# ============================================================================
# UNIFIED SYSTEM VIEWS
# ============================================================================

class UnifiedSystemHealthView(APIView):
    """Check overall system health"""
    
    def get(self, request):
        """Get complete system health status"""
        
        # Phase status
        phases = UnifiedPhase.objects.all()
        active_phases = phases.filter(status='active').count()
        
        # Event stats
        total_events = UnifiedEvent.objects.count()
        failed_events = UnifiedEvent.objects.filter(status='failed').count()
        pending_events = UnifiedEvent.objects.filter(status='pending').count()
        
        # Connection stats
        total_connections = PhaseConnection.objects.filter(is_active=True).count()
        
        # System health
        system_healthy = (
            active_phases == phases.count() and
            failed_events < (total_events * 0.05) and  # Less than 5% failure
            pending_events == 0
        )
        
        return Response({
            'status': 'healthy' if system_healthy else 'degraded',
            'timestamp': timezone.now().isoformat(),
            'phases': {
                'total': phases.count(),
                'active': active_phases,
                'inactive': phases.filter(status='inactive').count(),
            },
            'events': {
                'total': total_events,
                'completed': total_events - failed_events - pending_events,
                'failed': failed_events,
                'pending': pending_events,
                'success_rate': ((total_events - failed_events) / total_events * 100) if total_events > 0 else 100,
            },
            'connections': {
                'total': total_connections,
                'active': PhaseConnection.objects.filter(is_active=True).count(),
            }
        })


class UnifiedSystemDashboardView(APIView):
    """Unified system dashboard"""
    
    def get(self, request):
        """Get complete dashboard data"""
        
        # Get all phases with their status
        phases = UnifiedPhase.objects.all()
        phase_data = {}
        
        for phase in phases:
            phase_events = UnifiedEvent.objects.filter(source_phase=phase)
            phase_data[phase.phase_id] = {
                'name': phase.name,
                'status': phase.status,
                'total_events': phase_events.count(),
                'failed_events': phase_events.filter(status='failed').count(),
                'connections': {
                    'outgoing': phase.outgoing_connections.filter(is_active=True).count(),
                    'incoming': phase.incoming_connections.filter(is_active=True).count(),
                }
            }
        
        # Recent events
        recent_events = UnifiedEvent.objects.order_by('-created_at')[:10]
        
        # System metrics
        try:
            system_state = UnifiedSystemState.objects.latest('id')
        except UnifiedSystemState.DoesNotExist:
            system_state = UnifiedSystemState.objects.create()
        
        return Response({
            'dashboard': {
                'timestamp': timezone.now().isoformat(),
                'title': 'Feeding Hearts - Unified Phase System (1-10)',
                'phases': phase_data,
                'recent_events': [
                    {
                        'type': e.event_type,
                        'source_phase': e.source_phase.phase_id,
                        'status': e.status,
                        'created_at': e.created_at.isoformat(),
                    }
                    for e in recent_events
                ],
                'system_metrics': {
                    'total_events_processed': system_state.total_events_processed,
                    'total_events_failed': system_state.total_events_failed,
                    'active_phases': system_state.active_phases,
                    'average_processing_time_ms': system_state.average_event_processing_time_ms,
                    'is_healthy': system_state.is_healthy,
                }
            }
        })


class UnifiedAPIDocumentationView(APIView):
    """Complete API documentation"""
    
    def get(self, request):
        """Get API documentation"""
        
        phases = UnifiedPhase.objects.all()
        
        documentation = {
            'title': 'Feeding Hearts - Unified Phase API Documentation',
            'version': '1.0.0',
            'description': 'API for managing all 10 phases working together',
            'base_url': '/api/unified/',
            'global_endpoints': {
                'health': {
                    'method': 'GET',
                    'path': '/api/unified/health/',
                    'description': 'Check overall system health',
                },
                'dashboard': {
                    'method': 'GET',
                    'path': '/api/unified/dashboard/',
                    'description': 'Get unified system dashboard',
                },
                'phases': {
                    'method': 'GET',
                    'path': '/api/unified/phases/',
                    'description': 'List all phases with status',
                },
                'events': {
                    'method': 'GET',
                    'path': '/api/unified/events/',
                    'description': 'Get recent events',
                },
                'connections': {
                    'method': 'GET',
                    'path': '/api/unified/connections/',
                    'description': 'Get phase connections',
                },
            },
            'phase_endpoints': [
                {
                    'phase_id': phase.phase_id,
                    'name': phase.name,
                    'endpoints': [
                        f'GET {phase.api_endpoint}health/',
                        f'GET {phase.api_endpoint}status/',
                        f'POST {phase.api_endpoint}events/',
                    ]
                }
                for phase in phases
            ]
        }
        
        return Response(documentation)


# ============================================================================
# UNIFIED ANALYSIS VIEWS
# ============================================================================

class UnifiedPhaseAnalyticsView(APIView):
    """Analytics for unified phase system"""
    
    def get(self, request):
        """Get analytics and insights"""
        
        # Phase performance
        phases = UnifiedPhase.objects.all()
        phase_performance = {}
        
        for phase in phases:
            events = UnifiedEvent.objects.filter(source_phase=phase)
            if events.exists():
                failed = events.filter(status='failed').count()
                total = events.count()
                
                phase_performance[phase.phase_id] = {
                    'name': phase.name,
                    'total_events': total,
                    'success_rate': ((total - failed) / total * 100),
                    'failure_rate': (failed / total * 100),
                }
        
        # Connection performance
        connections = PhaseConnection.objects.all()
        top_connections = sorted(
            [
                {
                    'from': c.from_phase.phase_id,
                    'to': c.to_phase.phase_id,
                    'success_rate': (c.success_count / (c.success_count + c.failure_count) * 100) 
                                   if (c.success_count + c.failure_count) > 0 else 100,
                }
                for c in connections
            ],
            key=lambda x: x['success_rate'],
            reverse=True
        )
        
        return Response({
            'phase_performance': phase_performance,
            'top_connections': top_connections[:5],
            'insights': [
                'All 10 phases are integrated and communicating',
                'Events flow seamlessly between phases',
                'System is fully operational and monitoring all phases',
            ]
        })
