"""
Django Management Command: Initialize Unified Phases
Creates all 10 phases and their connections automatically
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models_unified import (
    UnifiedPhase, PhaseConnection, UnifiedSystemState
)


class Command(BaseCommand):
    help = 'Initialize all 10 unified phases and their connections'
    
    def handle(self, *args, **options):
        """Execute phase initialization"""
        
        self.stdout.write('Starting unified phase initialization...')
        
        # Define all 10 phases
        phases_data = [
            {
                'phase_id': 1,
                'name': 'Core Infrastructure',
                'description': 'Database, Authentication, User Management',
                'database_name': 'postgres_core',
                'api_endpoint': '/api/phase-1/',
            },
            {
                'phase_id': 2,
                'name': 'Food Inventory Management',
                'description': 'Track food items, stock levels, storage locations',
                'database_name': 'postgres_inventory',
                'api_endpoint': '/api/phase-2/',
            },
            {
                'phase_id': 3,
                'name': 'Distribution Logistics',
                'description': 'Plan routes, track deliveries, manage distribution points',
                'database_name': 'postgres_logistics',
                'api_endpoint': '/api/phase-3/',
            },
            {
                'phase_id': 4,
                'name': 'Recipient Management',
                'description': 'Manage recipient profiles, dietary restrictions, preferences',
                'database_name': 'postgres_recipients',
                'api_endpoint': '/api/phase-4/',
            },
            {
                'phase_id': 5,
                'name': 'Donation Management',
                'description': 'Track donations, process donor information, manage drives',
                'database_name': 'postgres_donations',
                'api_endpoint': '/api/phase-5/',
            },
            {
                'phase_id': 6,
                'name': 'Analytics & Reporting',
                'description': 'Aggregate operational data, generate reports',
                'database_name': 'postgres_analytics',
                'api_endpoint': '/api/phase-6/',
            },
            {
                'phase_id': 7,
                'name': 'Mobile App Integration',
                'description': 'Mobile interface, offline support, sync',
                'database_name': 'postgres_mobile',
                'api_endpoint': '/api/phase-7/',
            },
            {
                'phase_id': 8,
                'name': 'Advanced Analytics (ML)',
                'description': 'Machine learning models, pattern analysis, predictions',
                'database_name': 'mongodb_ml',
                'api_endpoint': '/api/phase-8/',
            },
            {
                'phase_id': 9,
                'name': 'Error Logging & Monitoring',
                'description': 'Capture errors, system monitoring, alerting',
                'database_name': 'mongodb_logging',
                'api_endpoint': '/api/phase-9/',
            },
            {
                'phase_id': 10,
                'name': 'AI Prediction & Recovery',
                'description': 'Predict issues, recommend actions, automated recovery',
                'database_name': 'mongodb_predictions',
                'api_endpoint': '/api/phase-10/',
            },
        ]
        
        # Create or update phases
        created_count = 0
        updated_count = 0
        
        for phase_data in phases_data:
            phase, created = UnifiedPhase.objects.update_or_create(
                phase_id=phase_data['phase_id'],
                defaults={
                    'name': phase_data['name'],
                    'description': phase_data['description'],
                    'database_name': phase_data['database_name'],
                    'api_endpoint': phase_data['api_endpoint'],
                    'status': 'active',
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Phase {phase.phase_id}: {phase.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↺ Updated Phase {phase.phase_id}: {phase.name}')
                )
        
        self.stdout.write(f'\nPhases: {created_count} created, {updated_count} updated\n')
        
        # Define phase connections (40+ routes)
        connections_data = [
            # Phase 1 (Core) → Operational phases (2-5)
            {'from': 1, 'to': 2, 'flow': 'downstream', 'trigger': 'api'},
            {'from': 1, 'to': 3, 'flow': 'downstream', 'trigger': 'api'},
            {'from': 1, 'to': 4, 'flow': 'downstream', 'trigger': 'api'},
            {'from': 1, 'to': 5, 'flow': 'downstream', 'trigger': 'api'},
            
            # Phase 2 (Inventory) → Phase 3 (Logistics)
            {'from': 2, 'to': 3, 'flow': 'downstream', 'trigger': 'event'},
            
            # Phase 3 (Logistics) → Phase 2 (Inventory) - feedback
            {'from': 3, 'to': 2, 'flow': 'upstream', 'trigger': 'event'},
            
            # Phase 5 (Donations) → Phase 2 (Inventory) - replenish
            {'from': 5, 'to': 2, 'flow': 'upstream', 'trigger': 'event'},
            
            # Operational phases (2,3,4,5) → Phase 6 (Analytics)
            {'from': 2, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 3, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 4, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 5, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            
            # Mobile app (Phase 7) bidirectional with operational phases
            {'from': 1, 'to': 7, 'flow': 'bidirectional', 'trigger': 'api'},
            {'from': 7, 'to': 1, 'flow': 'bidirectional', 'trigger': 'api'},
            
            {'from': 2, 'to': 7, 'flow': 'bidirectional', 'trigger': 'api'},
            {'from': 7, 'to': 2, 'flow': 'bidirectional', 'trigger': 'api'},
            
            {'from': 4, 'to': 7, 'flow': 'bidirectional', 'trigger': 'api'},
            {'from': 7, 'to': 4, 'flow': 'bidirectional', 'trigger': 'api'},
            
            # Analytics phases (6,8) get data from operational
            {'from': 6, 'to': 8, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 2, 'to': 8, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 4, 'to': 8, 'flow': 'downstream', 'trigger': 'schedule'},
            
            # All phases → Phase 9 (Error Logging)
            {'from': 1, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 2, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 3, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 4, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 5, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 6, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 7, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 8, 'to': 9, 'flow': 'downstream', 'trigger': 'event'},
            
            # Phase 9 (Error Logging) → Phase 10 (AI Prediction)
            {'from': 9, 'to': 10, 'flow': 'downstream', 'trigger': 'event'},
            
            # Phase 10 (AI Prediction) → Operational phases (recovery actions)
            {'from': 10, 'to': 1, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 10, 'to': 2, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 10, 'to': 3, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 10, 'to': 4, 'flow': 'downstream', 'trigger': 'event'},
            {'from': 10, 'to': 5, 'flow': 'downstream', 'trigger': 'event'},
            
            # Additional connections for data flow
            {'from': 3, 'to': 5, 'flow': 'bidirectional', 'trigger': 'api'},
            {'from': 4, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 7, 'to': 6, 'flow': 'downstream', 'trigger': 'schedule'},
            {'from': 8, 'to': 1, 'flow': 'downstream', 'trigger': 'event'},
        ]
        
        # Create or update connections
        connection_created = 0
        connection_updated = 0
        
        for conn_data in connections_data:
            from_phase = UnifiedPhase.objects.get(phase_id=conn_data['from'])
            to_phase = UnifiedPhase.objects.get(phase_id=conn_data['to'])
            
            connection, created = PhaseConnection.objects.update_or_create(
                from_phase=from_phase,
                to_phase=to_phase,
                defaults={
                    'flow_type': conn_data['flow'],
                    'trigger_type': conn_data['trigger'],
                    'is_active': True,
                }
            )
            
            if created:
                connection_created += 1
            else:
                connection_updated += 1
        
        self.stdout.write(
            f'Connections: {connection_created} created, {connection_updated} updated\n'
        )
        
        # Initialize system state
        system_state, created = UnifiedSystemState.objects.get_or_create(id=1)
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ System state initialized'))
        else:
            self.stdout.write(self.style.WARNING('↺ System state updated'))
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ All 10 phases initialized successfully!')
        )
        self.stdout.write(f'  - {phases_data.__len__()} phases configured')
        self.stdout.write(f'  - {connections_data.__len__()} connections established')
        self.stdout.write('  - System ready for operation\n')
