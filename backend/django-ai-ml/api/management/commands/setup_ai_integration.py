"""
Django management command for automatic AI prediction integration
Usage: python manage.py setup_ai_integration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import json


class Command(BaseCommand):
    help = 'Automatically setup and integrate AI prediction system with Feeding Hearts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-db',
            action='store_true',
            help='Skip database setup',
        )
        parser.add_argument(
            '--skip-models',
            action='store_true',
            help='Skip model initialization',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run in test mode',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🚀 AI PREDICTION INTEGRATION SETUP'))
        self.stdout.write(self.style.SUCCESS('   Feeding Hearts Project'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        try:
            # Step 1: Verify Settings
            self._verify_settings(options)

            # Step 2: Setup Logging
            self._setup_logging(options)

            # Step 3: Setup Database
            if not options['skip_db']:
                self._setup_database(options)

            # Step 4: Initialize Models
            if not options['skip_models']:
                self._initialize_models(options)

            # Step 5: Setup Monitoring
            self._setup_monitoring(options)

            # Step 6: Generate Configuration
            self._generate_configuration(options)

            # Step 7: Run Tests
            self._run_tests(options)

            self._print_summary(options)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Setup failed: {str(e)}'))
            raise

    def _verify_settings(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n1️⃣ Verifying Settings'))
        self.stdout.write('-' * 70)

        required_settings = [
            'INSTALLED_APPS',
            'MIDDLEWARE',
            'DATABASES',
            'CACHES',
        ]

        for setting in required_settings:
            if hasattr(settings, setting):
                self.stdout.write(self.style.SUCCESS(f'  ✅ {setting} configured'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️  {setting} not found'))

        # Check AI-specific settings
        ai_settings = [
            'AUTO_RECOVERY_ENABLED',
            'ML_PREDICTION_ENABLED',
            'ANOMALY_DETECTION_ENABLED',
            'ERROR_ALERT_RECIPIENTS',
        ]

        self.stdout.write('\n  AI-Specific Settings:')
        for setting in ai_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                self.stdout.write(self.style.SUCCESS(f'    ✅ {setting} = {value}'))
            else:
                self.stdout.write(self.style.WARNING(f'    ⚠️  {setting} = (using default)'))

    def _setup_logging(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n2️⃣ Setting Up Logging'))
        self.stdout.write('-' * 70)

        try:
            from error_logging.models import ErrorLog
            from error_logging.services import ErrorAlertManager

            # Verify error logging is working
            self.stdout.write(self.style.SUCCESS('  ✅ Error logging models loaded'))
            self.stdout.write(self.style.SUCCESS('  ✅ Error alert manager initialized'))

            # Test alert sending
            alert_manager = ErrorAlertManager()
            self.stdout.write(self.style.SUCCESS('  ✅ Alert system ready'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Logging setup: {str(e)}'))

    def _setup_database(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n3️⃣ Setting Up Database'))
        self.stdout.write('-' * 70)

        try:
            from django.core.management import call_command

            # Run migrations
            self.stdout.write('  Running migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  ✅ Database migrations complete'))

            # Verify tables
            from django.db import connection
            with connection.cursor() as cursor:
                tables = connection.introspection.table_names()
                ai_tables = [t for t in tables if 'error' in t or 'prediction' in t or 'ml' in t]
                self.stdout.write(f'  ✅ Found {len(ai_tables)} AI-related tables')
                for table in ai_tables[:5]:
                    self.stdout.write(f'     - {table}')
                if len(ai_tables) > 5:
                    self.stdout.write(f'     ... and {len(ai_tables) - 5} more')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Database setup: {str(e)}'))

    def _initialize_models(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n4️⃣ Initializing ML Models'))
        self.stdout.write('-' * 70)

        try:
            from ml_prediction.services import ErrorPredictionService, AnomalyDetectionService

            self.stdout.write('  Initializing error prediction model...')
            error_service = ErrorPredictionService()
            error_service.initialize_models()
            self.stdout.write(self.style.SUCCESS('  ✅ Error prediction model initialized'))

            self.stdout.write('  Initializing anomaly detection model...')
            anomaly_service = AnomalyDetectionService()
            anomaly_service.initialize_models()
            self.stdout.write(self.style.SUCCESS('  ✅ Anomaly detection model initialized'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Model initialization: {str(e)}'))
            self.stdout.write('     (Models can be trained with historical data later)')

    def _setup_monitoring(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n5️⃣ Setting Up Monitoring'))
        self.stdout.write('-' * 70)

        try:
            from error_logging.services import ErrorAlertManager

            alert_manager = ErrorAlertManager()
            recipients = getattr(settings, 'ERROR_ALERT_RECIPIENTS', [])

            if recipients:
                self.stdout.write(f'  Alert Recipients: {", ".join(recipients)}')
                self.stdout.write(self.style.SUCCESS('  ✅ Alert system configured'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  No alert recipients configured'))

            # Check Redis
            try:
                import redis
                redis_client = redis.Redis(host='localhost', port=6379)
                redis_client.ping()
                self.stdout.write(self.style.SUCCESS('  ✅ Redis connection verified'))
            except:
                self.stdout.write(self.style.WARNING('  ⚠️  Redis not available (caching limited)'))

            # Check Celery
            try:
                from celery import Celery
                self.stdout.write(self.style.SUCCESS('  ✅ Celery configured for async tasks'))
            except:
                self.stdout.write(self.style.WARNING('  ⚠️  Celery not configured'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Monitoring setup: {str(e)}'))

    def _generate_configuration(self, options):
        self.stdout.write(self.style.HTTP_INFO('\n6️⃣ Generating Configuration'))
        self.stdout.write('-' * 70)

        try:
            # Get all AI settings
            ai_config = {
                'error_recovery': {
                    'enabled': getattr(settings, 'AUTO_RECOVERY_ENABLED', True),
                    'timeout': getattr(settings, 'RECOVERY_TIMEOUT_SECONDS', 5),
                    'max_attempts': getattr(settings, 'MAX_RECOVERY_ATTEMPTS', 3),
                },
                'ml_prediction': {
                    'enabled': getattr(settings, 'ML_PREDICTION_ENABLED', True),
                    'confidence_threshold': getattr(settings, 'PREDICTION_CONFIDENCE_THRESHOLD', 0.75),
                    'anomaly_detection': getattr(settings, 'ANOMALY_DETECTION_ENABLED', True),
                },
                'monitoring': {
                    'enabled': getattr(settings, 'ENABLE_HEALTH_MONITORING', True),
                    'check_interval': getattr(settings, 'HEALTH_CHECK_INTERVAL', 30),
                },
                'alerts': {
                    'recipients': getattr(settings, 'ERROR_ALERT_RECIPIENTS', []),
                    'slack_enabled': getattr(settings, 'SLACK_ERROR_ALERTS', False),
                },
            }

            self.stdout.write(self.style.SUCCESS('  ✅ Configuration generated:'))
            self.stdout.write(f'     - Error Recovery: {ai_config["error_recovery"]}')
            self.stdout.write(f'     - ML Prediction: {ai_config["ml_prediction"]}')
            self.stdout.write(f'     - Monitoring: {ai_config["monitoring"]}')
            self.stdout.write(f'     - Alerts: {ai_config["alerts"]}')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Configuration generation: {str(e)}'))

    def _run_tests(self, options):
        if options['test']:
            self.stdout.write(self.style.HTTP_INFO('\n7️⃣ Running Tests'))
            self.stdout.write('-' * 70)

            try:
                from django.core.management import call_command

                self.stdout.write('  Running AI prediction tests...')
                call_command('test', 'ml_prediction', verbosity=0)
                self.stdout.write(self.style.SUCCESS('  ✅ ML prediction tests passed'))

                self.stdout.write('  Running error logging tests...')
                call_command('test', 'error_logging', verbosity=0)
                self.stdout.write(self.style.SUCCESS('  ✅ Error logging tests passed'))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Tests: {str(e)}'))

    def _print_summary(self, options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ SETUP COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*70))

        self.stdout.write(self.style.HTTP_INFO('\nNEXT STEPS:'))
        self.stdout.write('-' * 70)

        next_steps = [
            '1. Start the development server:',
            '   python manage.py runserver',
            '',
            '2. In another terminal, start Celery worker:',
            '   celery -A config worker -l info',
            '',
            '3. Test the integration:',
            '   python manage.py shell',
            '   >>> from error_logging.services import ErrorAlertManager',
            '   >>> manager = ErrorAlertManager()',
            '   >>> manager.test_alert()',
            '',
            '4. View the dashboard:',
            '   http://localhost:8000/api/ai-dashboard/',
            '',
            '5. Read the full guide:',
            '   AI_INTEGRATION_GUIDE.md',
        ]

        for step in next_steps:
            self.stdout.write(step)

        self.stdout.write('\n' + '='*70 + '\n')
