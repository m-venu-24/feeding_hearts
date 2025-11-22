"""
Celery Tasks for Unified Phase Integration
Async event processing and routing between phases
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from api.models_unified import (
    UnifiedPhase, UnifiedEvent, PhaseConnection, 
    UnifiedSystemState, PhaseDataTransform
)
from api.unified_phase_orchestration import UnifiedPhaseOrchestrator

logger = logging.getLogger(__name__)


# ============================================================================
# EVENT PROCESSING TASKS
# ============================================================================

@shared_task(bind=True, max_retries=3)
def process_unified_event(self, event_id):
    """
    Process a unified event and route to target phases
    
    Args:
        event_id: UUID of the UnifiedEvent to process
    """
    try:
        event = UnifiedEvent.objects.get(event_id=event_id)
        
        # Mark as processing
        event.status = 'processing'
        event.save()
        
        start_time = timezone.now()
        
        # Get orchestrator
        orchestrator = UnifiedPhaseOrchestrator()
        
        # Find connected phases for this event
        connections = PhaseConnection.objects.filter(
            from_phase=event.source_phase,
            is_active=True,
            trigger_type__in=['event', 'api']
        )
        
        target_phases = [conn.to_phase for conn in connections]
        
        # Route to all target phases
        successful_routes = 0
        for target_phase in target_phases:
            try:
                # Execute phase-specific processing
                result = orchestrator.route_event_to_phase(event, target_phase)
                
                if result['success']:
                    successful_routes += 1
                    
                    # Update connection success count
                    connection = connections.get(to_phase=target_phase)
                    connection.success_count += 1
                    connection.save()
                else:
                    # Update connection failure count
                    connection = connections.get(to_phase=target_phase)
                    connection.failure_count += 1
                    connection.save()
                    
                    logger.warning(
                        f'Event {event_id} failed routing to phase {target_phase.phase_id}'
                    )
                    
            except Exception as e:
                logger.error(
                    f'Error routing event {event_id} to phase {target_phase.phase_id}: {str(e)}'
                )
                continue
        
        # Mark event as completed
        event.status = 'completed'
        event.processed_at = timezone.now()
        event.processing_time_ms = int((event.processed_at - start_time).total_seconds() * 1000)
        event.save()
        
        # Update system state
        update_system_state.delay(
            total_events=1,
            failed_events=0 if successful_routes > 0 else 1,
            processing_time_ms=event.processing_time_ms
        )
        
        logger.info(
            f'Event {event_id} processed successfully. '
            f'Routed to {successful_routes}/{len(target_phases)} phases'
        )
        
        return {
            'event_id': str(event_id),
            'status': 'completed',
            'routed_to_phases': successful_routes,
            'processing_time_ms': event.processing_time_ms,
        }
        
    except UnifiedEvent.DoesNotExist:
        logger.error(f'Event {event_id} not found')
        raise
    except Exception as exc:
        logger.error(f'Error processing event {event_id}: {str(exc)}')
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def process_scheduled_events():
    """
    Process scheduled events between phases
    Runs periodically (every 5 minutes)
    """
    
    # Get all active scheduled connections
    scheduled_connections = PhaseConnection.objects.filter(
        is_active=True,
        trigger_type='schedule'
    )
    
    processed_count = 0
    
    for connection in scheduled_connections:
        try:
            # Create a synthetic event for the scheduled connection
            event = UnifiedEvent.objects.create(
                event_type=f'{connection.from_phase.name}_scheduled_sync',
                source_phase=connection.from_phase,
                status='pending',
                data={
                    'connection_id': str(connection.connection_id),
                    'trigger': 'scheduled',
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
            event.target_phases.add(connection.to_phase)
            
            # Queue for processing
            process_unified_event.delay(str(event.event_id))
            processed_count += 1
            
        except Exception as e:
            logger.error(
                f'Error creating scheduled event for connection '
                f'{connection.connection_id}: {str(e)}'
            )
            continue
    
    logger.info(f'Scheduled {processed_count} events for processing')
    return {'scheduled_events': processed_count}


@shared_task
def process_failed_events_retry():
    """
    Retry failed events
    Runs periodically (every 10 minutes)
    """
    
    # Get failed events from the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    failed_events = UnifiedEvent.objects.filter(
        status='failed',
        created_at__gte=one_hour_ago
    )
    
    retry_count = 0
    
    for event in failed_events:
        try:
            # Reset status and requeue
            event.status = 'pending'
            event.save()
            
            process_unified_event.delay(str(event.event_id))
            retry_count += 1
            
        except Exception as e:
            logger.error(f'Error retrying event {event.event_id}: {str(e)}')
            continue
    
    logger.info(f'Retried {retry_count} failed events')
    return {'retried_events': retry_count}


# ============================================================================
# SYSTEM STATE MANAGEMENT TASKS
# ============================================================================

@shared_task
def update_system_state(total_events=0, failed_events=0, processing_time_ms=0):
    """
    Update unified system state metrics
    
    Args:
        total_events: Number of events processed
        failed_events: Number of failed events
        processing_time_ms: Processing time in milliseconds
    """
    
    try:
        system_state, created = UnifiedSystemState.objects.get_or_create(id=1)
        
        # Update metrics
        system_state.total_events_processed += total_events
        system_state.total_events_failed += failed_events
        system_state.active_phases = UnifiedPhase.objects.filter(status='active').count()
        
        # Calculate average processing time
        if total_events > 0:
            current_total = (
                system_state.average_event_processing_time_ms * 
                (system_state.total_events_processed - total_events)
            )
            new_total = current_total + (processing_time_ms * total_events)
            system_state.average_event_processing_time_ms = (
                new_total / system_state.total_events_processed
            )
        
        # Check health
        if system_state.total_events_processed > 0:
            failure_rate = (
                system_state.total_events_failed / system_state.total_events_processed
            )
            system_state.is_healthy = failure_rate < 0.05  # Less than 5% failures
        
        system_state.last_health_check = timezone.now()
        system_state.save()
        
        logger.info(
            f'System state updated: {total_events} events processed, '
            f'{failed_events} failed'
        )
        
        return {
            'total_events_processed': system_state.total_events_processed,
            'is_healthy': system_state.is_healthy,
        }
        
    except Exception as e:
        logger.error(f'Error updating system state: {str(e)}')
        raise


@shared_task
def monitor_phase_health():
    """
    Monitor health of all phases
    Runs periodically (every minute)
    """
    
    phases = UnifiedPhase.objects.all()
    
    for phase in phases:
        try:
            # Get recent events for this phase
            recent_events = UnifiedEvent.objects.filter(
                source_phase=phase
            ).order_by('-created_at')[:100]
            
            if not recent_events.exists():
                phase.status = 'idle'
                phase.save()
                continue
            
            # Calculate failure rate
            failed_count = recent_events.filter(status='failed').count()
            total_count = recent_events.count()
            failure_rate = (failed_count / total_count) if total_count > 0 else 0
            
            # Determine phase health
            if failure_rate > 0.3:  # More than 30% failures
                phase.status = 'degraded'
            elif failure_rate > 0:  # Some failures
                phase.status = 'warning'
            else:
                phase.status = 'active'
            
            # Update last event time
            phase.last_event_processed = recent_events.first().created_at
            phase.save()
            
        except Exception as e:
            logger.error(f'Error monitoring phase {phase.phase_id}: {str(e)}')
            phase.status = 'error'
            phase.save()
            continue
    
    logger.info('Phase health monitoring completed')
    return {'phases_monitored': phases.count()}


# ============================================================================
# DATA TRANSFORMATION TASKS
# ============================================================================

@shared_task
def apply_data_transformations(event_id):
    """
    Apply data transformations as events flow between phases
    
    Args:
        event_id: UUID of the UnifiedEvent
    """
    
    try:
        event = UnifiedEvent.objects.get(event_id=event_id)
        
        # Find applicable transformations
        transformations = PhaseDataTransform.objects.filter(
            from_phase=event.source_phase,
            is_active=True
        )
        
        transformed_data = dict(event.data)
        
        for transform in transformations:
            try:
                # Execute transformation logic
                source_value = transformed_data.get(transform.source_field)
                
                if source_value is not None:
                    # Parse and execute transformation logic
                    # Example: "double", "uppercase", "add_prefix:PHASE_"
                    target_value = execute_transformation(
                        source_value,
                        transform.transformation_logic
                    )
                    
                    transformed_data[transform.target_field] = target_value
                    
            except Exception as e:
                logger.warning(
                    f'Error applying transformation {transform.transform_id}: {str(e)}'
                )
                continue
        
        # Update event data
        event.data = transformed_data
        event.save()
        
        logger.info(f'Transformations applied to event {event_id}')
        return {'event_id': str(event_id), 'transformations_applied': True}
        
    except UnifiedEvent.DoesNotExist:
        logger.error(f'Event {event_id} not found')
        raise


def execute_transformation(value, logic):
    """
    Execute transformation logic
    
    Args:
        value: Source value
        logic: Transformation logic string
    
    Returns:
        Transformed value
    """
    
    if logic == 'double':
        return value * 2
    elif logic == 'uppercase':
        return str(value).upper()
    elif logic == 'lowercase':
        return str(value).lower()
    elif logic.startswith('add_prefix:'):
        prefix = logic.split(':')[1]
        return prefix + str(value)
    elif logic.startswith('add_suffix:'):
        suffix = logic.split(':')[1]
        return str(value) + suffix
    else:
        # Return unchanged if transformation not recognized
        return value


# ============================================================================
# REPORTING TASKS
# ============================================================================

@shared_task
def generate_unified_system_report():
    """
    Generate comprehensive unified system report
    Runs daily
    """
    
    try:
        report = {
            'timestamp': timezone.now().isoformat(),
            'summary': {},
            'phase_details': {},
            'connection_statistics': {},
        }
        
        # Get system state
        try:
            system_state = UnifiedSystemState.objects.latest('id')
        except UnifiedSystemState.DoesNotExist:
            system_state = None
        
        if system_state:
            report['summary'] = {
                'total_events_processed': system_state.total_events_processed,
                'total_events_failed': system_state.total_events_failed,
                'active_phases': system_state.active_phases,
                'average_processing_time_ms': system_state.average_event_processing_time_ms,
                'is_healthy': system_state.is_healthy,
            }
        
        # Phase details
        for phase in UnifiedPhase.objects.all():
            events = UnifiedEvent.objects.filter(source_phase=phase)
            failed = events.filter(status='failed').count()
            total = events.count()
            
            report['phase_details'][phase.phase_id] = {
                'name': phase.name,
                'status': phase.status,
                'total_events': total,
                'failed_events': failed,
                'success_rate': ((total - failed) / total * 100) if total > 0 else 100,
            }
        
        # Connection statistics
        for connection in PhaseConnection.objects.all():
            total = connection.success_count + connection.failure_count
            
            report['connection_statistics'][str(connection.connection_id)] = {
                'from_phase': connection.from_phase.phase_id,
                'to_phase': connection.to_phase.phase_id,
                'flow_type': connection.flow_type,
                'total_executions': total,
                'success_count': connection.success_count,
                'failure_count': connection.failure_count,
                'success_rate': (connection.success_count / total * 100) if total > 0 else 100,
            }
        
        logger.info('Unified system report generated')
        return report
        
    except Exception as e:
        logger.error(f'Error generating system report: {str(e)}')
        raise


# ============================================================================
# CLEANUP TASKS
# ============================================================================

@shared_task
def cleanup_old_events(days=30):
    """
    Clean up old completed events
    
    Args:
        days: Delete events older than this many days
    """
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    deleted_count, _ = UnifiedEvent.objects.filter(
        status='completed',
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f'Deleted {deleted_count} old events')
    return {'deleted_events': deleted_count}


@shared_task
def verify_phase_connections():
    """
    Verify that all phase connections are still valid
    Runs daily
    """
    
    connections = PhaseConnection.objects.filter(is_active=True)
    
    verified_count = 0
    failed_count = 0
    
    for connection in connections:
        try:
            # Attempt to verify connection
            from_phase = connection.from_phase
            to_phase = connection.to_phase
            
            # Check if phases are active
            if from_phase.status == 'active' and to_phase.status == 'active':
                verified_count += 1
            else:
                # Deactivate connection if phases are not active
                connection.is_active = False
                connection.save()
                failed_count += 1
                
        except Exception as e:
            logger.error(
                f'Error verifying connection {connection.connection_id}: {str(e)}'
            )
            failed_count += 1
            continue
    
    logger.info(
        f'Connection verification completed: {verified_count} active, {failed_count} inactive'
    )
    return {
        'verified_connections': verified_count,
        'failed_connections': failed_count,
    }
