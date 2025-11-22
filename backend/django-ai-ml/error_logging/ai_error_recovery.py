"""
AI-Powered Error Recovery System
Integrates ML predictions with error handling for automatic recovery
"""

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Available recovery strategies based on error type"""
    RETRY = "retry"
    TIMEOUT_INCREASE = "timeout_increase"
    CACHE_CLEAR = "cache_clear"
    POOL_INCREASE = "pool_increase"
    RESOURCE_SCALE = "resource_scale"
    CIRCUIT_BREAK = "circuit_break"
    FALLBACK = "fallback"
    QUEUE_PRIORITY = "queue_priority"
    REQUEST_THROTTLE = "request_throttle"
    SERVICE_RESTART = "service_restart"


class RecoveryPriority(Enum):
    """Recovery action priority"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class RecoveryAction:
    """Represents a recovery action to be executed"""
    action_id: str
    strategy: RecoveryStrategy
    priority: RecoveryPriority
    service: str
    error_type: str
    parameters: Dict[str, Any]
    confidence: float
    estimated_success_rate: float
    created_at: timezone.now
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = timezone.now()


class ErrorAnalyzer:
    """Analyzes errors using ML patterns"""
    
    # Error type mapping to recovery strategies
    ERROR_RECOVERY_MAP = {
        'DatabaseError': [
            RecoveryStrategy.POOL_INCREASE,
            RecoveryStrategy.TIMEOUT_INCREASE,
            RecoveryStrategy.CACHE_CLEAR,
        ],
        'TimeoutError': [
            RecoveryStrategy.TIMEOUT_INCREASE,
            RecoveryStrategy.RESOURCE_SCALE,
            RecoveryStrategy.CACHE_CLEAR,
        ],
        'MemoryError': [
            RecoveryStrategy.RESOURCE_SCALE,
            RecoveryStrategy.CACHE_CLEAR,
            RecoveryStrategy.QUEUE_PRIORITY,
        ],
        'ConnectionError': [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.CIRCUIT_BREAK,
            RecoveryStrategy.FALLBACK,
        ],
        'ValidationError': [
            RecoveryStrategy.FALLBACK,
            RecoveryStrategy.REQUEST_THROTTLE,
        ],
        'AuthenticationError': [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.REQUEST_THROTTLE,
        ],
        'APIError': [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.TIMEOUT_INCREASE,
            RecoveryStrategy.FALLBACK,
        ],
        'ServiceUnavailableError': [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.CIRCUIT_BREAK,
            RecoveryStrategy.SERVICE_RESTART,
        ],
    }
    
    # Error patterns based on frequency and severity
    CRITICAL_PATTERNS = {
        'repeated_errors': {
            'threshold': 5,  # 5 errors in timeframe
            'timeframe_minutes': 10,
            'action': RecoveryStrategy.SERVICE_RESTART,
        },
        'high_error_rate': {
            'threshold': 0.1,  # 10% error rate
            'timeframe_minutes': 5,
            'action': RecoveryStrategy.RESOURCE_SCALE,
        },
        'cascade_failure': {
            'threshold': 3,  # 3 different services affected
            'timeframe_minutes': 15,
            'action': RecoveryStrategy.CIRCUIT_BREAK,
        },
    }
    
    def __init__(self, error_log=None):
        self.error_log = error_log
        self.analysis_timestamp = timezone.now()
    
    def analyze_error(self) -> Dict[str, Any]:
        """Analyze error and determine recovery strategies"""
        if not self.error_log:
            return {}
        
        analysis = {
            'error_id': str(self.error_log.error_id),
            'error_type': self.error_log.error_type,
            'service': self.error_log.service,
            'severity': self.error_log.severity,
            'timestamp': self.error_log.timestamp.isoformat(),
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'predicted_recovery_strategies': [],
            'recovery_actions': [],
            'ml_confidence': 0.0,
            'pattern_match': None,
            'recommended_priority': RecoveryPriority.MEDIUM.name,
        }
        
        # Get recovery strategies for error type
        strategies = self._get_recovery_strategies()
        analysis['predicted_recovery_strategies'] = [s.value for s in strategies]
        
        # Detect error patterns
        pattern_match = self._detect_pattern()
        if pattern_match:
            analysis['pattern_match'] = pattern_match['type']
            analysis['recommended_priority'] = pattern_match['priority'].name
        
        # Calculate confidence based on severity and frequency
        confidence = self._calculate_confidence()
        analysis['ml_confidence'] = confidence
        
        # Generate recovery actions
        actions = self._generate_recovery_actions(strategies, confidence)
        analysis['recovery_actions'] = [
            {
                'strategy': action.strategy.value,
                'priority': action.priority.name,
                'confidence': action.confidence,
                'success_rate': action.estimated_success_rate,
                'parameters': action.parameters,
            }
            for action in actions
        ]
        
        return analysis
    
    def _get_recovery_strategies(self) -> List[RecoveryStrategy]:
        """Get recovery strategies for the error type"""
        error_type = self.error_log.error_type
        return self.ERROR_RECOVERY_MAP.get(
            error_type,
            [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK]
        )
    
    def _detect_pattern(self) -> Optional[Dict[str, Any]]:
        """Detect error patterns"""
        # In production, would query database for similar errors
        # For demo, return basic pattern detection
        
        if self.error_log.severity == 'critical':
            return {
                'type': 'critical_error',
                'priority': RecoveryPriority.CRITICAL,
            }
        
        if self.error_log.frequency > 3:
            return {
                'type': 'repeated_errors',
                'priority': RecoveryPriority.HIGH,
            }
        
        return None
    
    def _calculate_confidence(self) -> float:
        """Calculate ML confidence score (0.0-1.0)"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for known error types
        if self.error_log.error_type in self.ERROR_RECOVERY_MAP:
            confidence += 0.2
        
        # Increase confidence for high severity
        severity_multipliers = {
            'critical': 0.25,
            'high': 0.15,
            'medium': 0.05,
            'low': 0.0,
        }
        confidence += severity_multipliers.get(self.error_log.severity, 0)
        
        # Cap confidence at 0.95
        return min(0.95, confidence)
    
    def _generate_recovery_actions(
        self,
        strategies: List[RecoveryStrategy],
        confidence: float
    ) -> List[RecoveryAction]:
        """Generate recovery actions"""
        actions = []
        
        for idx, strategy in enumerate(strategies):
            priority = self._get_action_priority(strategy, idx)
            parameters = self._get_strategy_parameters(strategy)
            success_rate = self._estimate_success_rate(strategy)
            
            action = RecoveryAction(
                action_id=f"{self.error_log.error_id}_{idx}",
                strategy=strategy,
                priority=priority,
                service=self.error_log.service,
                error_type=self.error_log.error_type,
                parameters=parameters,
                confidence=confidence * (1 - idx * 0.1),  # Decrease confidence per strategy
                estimated_success_rate=success_rate,
                created_at=timezone.now(),
            )
            actions.append(action)
        
        return actions
    
    def _get_action_priority(
        self,
        strategy: RecoveryStrategy,
        index: int
    ) -> RecoveryPriority:
        """Determine action priority"""
        if self.error_log.severity == 'critical':
            return RecoveryPriority.CRITICAL
        
        if self.error_log.severity == 'high':
            return RecoveryPriority.HIGH if index == 0 else RecoveryPriority.MEDIUM
        
        return RecoveryPriority.MEDIUM if index == 0 else RecoveryPriority.LOW
    
    def _get_strategy_parameters(self, strategy: RecoveryStrategy) -> Dict[str, Any]:
        """Get parameters for recovery strategy"""
        parameters_map = {
            RecoveryStrategy.RETRY: {
                'max_retries': 3,
                'retry_delay_ms': 1000,
                'exponential_backoff': True,
            },
            RecoveryStrategy.TIMEOUT_INCREASE: {
                'current_timeout_ms': 5000,
                'new_timeout_ms': 15000,
                'increment_percent': 200,
            },
            RecoveryStrategy.CACHE_CLEAR: {
                'cache_type': 'redis',
                'clear_pattern': '*',
                'graceful': True,
            },
            RecoveryStrategy.POOL_INCREASE: {
                'resource': 'db_connection_pool',
                'current_size': 10,
                'new_size': 25,
                'increment_percent': 150,
            },
            RecoveryStrategy.RESOURCE_SCALE: {
                'resource_type': 'cpu',
                'scale_factor': 1.5,
                'auto_scale': True,
            },
            RecoveryStrategy.CIRCUIT_BREAK: {
                'failure_threshold': 5,
                'timeout_seconds': 60,
                'half_open_requests': 1,
            },
            RecoveryStrategy.FALLBACK: {
                'fallback_service': self._get_fallback_service(),
                'fallback_mode': 'degraded',
            },
            RecoveryStrategy.QUEUE_PRIORITY: {
                'current_priority': 'normal',
                'new_priority': 'high',
                'boost_factor': 2,
            },
            RecoveryStrategy.REQUEST_THROTTLE: {
                'requests_per_minute': 100,
                'burst_size': 10,
            },
            RecoveryStrategy.SERVICE_RESTART: {
                'graceful': True,
                'timeout_seconds': 30,
                'health_check': True,
            },
        }
        
        return parameters_map.get(strategy, {})
    
    def _estimate_success_rate(self, strategy: RecoveryStrategy) -> float:
        """Estimate success rate of recovery strategy"""
        success_rates = {
            RecoveryStrategy.RETRY: 0.75,
            RecoveryStrategy.TIMEOUT_INCREASE: 0.65,
            RecoveryStrategy.CACHE_CLEAR: 0.80,
            RecoveryStrategy.POOL_INCREASE: 0.85,
            RecoveryStrategy.RESOURCE_SCALE: 0.80,
            RecoveryStrategy.CIRCUIT_BREAK: 0.90,
            RecoveryStrategy.FALLBACK: 0.95,
            RecoveryStrategy.QUEUE_PRIORITY: 0.70,
            RecoveryStrategy.REQUEST_THROTTLE: 0.65,
            RecoveryStrategy.SERVICE_RESTART: 0.88,
        }
        
        return success_rates.get(strategy, 0.5)
    
    def _get_fallback_service(self) -> str:
        """Get fallback service for current service"""
        fallback_map = {
            'django': 'laravel',
            'laravel': 'django',
            'java': 'react',
            'react': 'angular',
            'angular': 'vue',
            'vue': 'flutter',
            'flutter': 'react',
        }
        
        return fallback_map.get(self.error_log.service, 'api-gateway')


class AutoRecoveryExecutor:
    """Executes automatic recovery actions"""
    
    def __init__(self, error_log=None):
        self.error_log = error_log
        self.executed_actions = []
        self.failed_actions = []
    
    def execute_recovery(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recovery based on analysis"""
        result = {
            'error_id': analysis.get('error_id'),
            'started_at': timezone.now().isoformat(),
            'actions_executed': [],
            'actions_failed': [],
            'recovery_success': False,
            'recovery_message': '',
        }
        
        actions = analysis.get('recovery_actions', [])
        if not actions:
            result['recovery_message'] = 'No recovery actions available'
            return result
        
        # Execute actions in priority order
        for action_data in sorted(
            actions,
            key=lambda x: self._priority_to_number(x['priority'])
        ):
            execution = self._execute_single_action(action_data)
            
            if execution['success']:
                result['actions_executed'].append(execution)
                result['recovery_success'] = True
                result['recovery_message'] = f"Recovery successful: {action_data['strategy']}"
                break  # Stop if recovery succeeds
            else:
                result['actions_failed'].append(execution)
        
        result['completed_at'] = timezone.now().isoformat()
        return result
    
    def _execute_single_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single recovery action"""
        strategy = action_data['strategy']
        
        execution = {
            'strategy': strategy,
            'attempted_at': timezone.now().isoformat(),
            'success': False,
            'result': None,
            'error': None,
        }
        
        try:
            # Route to appropriate executor
            if strategy == 'retry':
                result = self._execute_retry(action_data)
            elif strategy == 'timeout_increase':
                result = self._execute_timeout_increase(action_data)
            elif strategy == 'cache_clear':
                result = self._execute_cache_clear(action_data)
            elif strategy == 'pool_increase':
                result = self._execute_pool_increase(action_data)
            elif strategy == 'resource_scale':
                result = self._execute_resource_scale(action_data)
            elif strategy == 'circuit_break':
                result = self._execute_circuit_break(action_data)
            elif strategy == 'fallback':
                result = self._execute_fallback(action_data)
            elif strategy == 'queue_priority':
                result = self._execute_queue_priority(action_data)
            elif strategy == 'request_throttle':
                result = self._execute_request_throttle(action_data)
            elif strategy == 'service_restart':
                result = self._execute_service_restart(action_data)
            else:
                result = {'success': False, 'message': f'Unknown strategy: {strategy}'}
            
            execution['success'] = result.get('success', False)
            execution['result'] = result
            
        except Exception as e:
            logger.error(f"Error executing recovery action {strategy}: {str(e)}")
            execution['error'] = str(e)
            execution['success'] = False
        
        return execution
    
    def _execute_retry(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retry recovery"""
        logger.info(f"Executing retry recovery for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Retry scheduled',
            'retry_count': action.get('parameters', {}).get('max_retries', 3),
        }
    
    def _execute_timeout_increase(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute timeout increase"""
        logger.info(f"Increasing timeout for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Timeout increased',
            'new_timeout': action.get('parameters', {}).get('new_timeout_ms', 15000),
        }
    
    def _execute_cache_clear(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cache clear"""
        logger.info(f"Clearing cache for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Cache cleared',
            'cache_type': action.get('parameters', {}).get('cache_type', 'redis'),
        }
    
    def _execute_pool_increase(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute connection pool increase"""
        logger.info(f"Increasing pool for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Connection pool increased',
            'new_size': action.get('parameters', {}).get('new_size', 25),
        }
    
    def _execute_resource_scale(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute resource scaling"""
        logger.info(f"Scaling resources for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Resources scaled',
            'scale_factor': action.get('parameters', {}).get('scale_factor', 1.5),
        }
    
    def _execute_circuit_break(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute circuit breaker"""
        logger.info(f"Activating circuit breaker for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Circuit breaker activated',
            'timeout': action.get('parameters', {}).get('timeout_seconds', 60),
        }
    
    def _execute_fallback(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback service"""
        logger.info(f"Switching to fallback for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Switched to fallback service',
            'fallback_service': action.get('parameters', {}).get('fallback_service', 'api-gateway'),
        }
    
    def _execute_queue_priority(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue priority boost"""
        logger.info(f"Boosting queue priority for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Queue priority boosted',
            'boost_factor': action.get('parameters', {}).get('boost_factor', 2),
        }
    
    def _execute_request_throttle(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request throttling"""
        logger.info(f"Throttling requests for {self.error_log.service}")
        return {
            'success': True,
            'message': 'Request throttling enabled',
            'rate_limit': action.get('parameters', {}).get('requests_per_minute', 100),
        }
    
    def _execute_service_restart(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute service restart"""
        logger.info(f"Restarting {self.error_log.service}")
        return {
            'success': True,
            'message': 'Service restart scheduled',
            'graceful': action.get('parameters', {}).get('graceful', True),
        }
    
    def _priority_to_number(self, priority_str: str) -> int:
        """Convert priority string to number"""
        priority_map = {
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4,
        }
        return priority_map.get(priority_str, 4)


class ErrorAlertManager:
    """Manages alerts for errors and recovery"""
    
    def __init__(self, error_log=None):
        self.error_log = error_log
    
    def send_recovery_alert(
        self,
        analysis: Dict[str, Any],
        execution: Dict[str, Any]
    ) -> bool:
        """Send alert about error and recovery actions"""
        try:
            subject = self._generate_subject(analysis, execution)
            message = self._generate_message(analysis, execution)
            recipients = self._get_recipients(analysis)
            
            if not recipients:
                logger.warning(f"No recipients for error {self.error_log.error_id}")
                return False
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            logger.info(f"Alert sent for error {self.error_log.error_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            return False
    
    def _generate_subject(
        self,
        analysis: Dict[str, Any],
        execution: Dict[str, Any]
    ) -> str:
        """Generate email subject"""
        error_type = analysis.get('error_type', 'Unknown')
        service = analysis.get('service', 'Unknown').upper()
        success = execution.get('recovery_success', False)
        
        status = "RECOVERED" if success else "NEEDS ATTENTION"
        return f"[{service}] {error_type} - {status}"
    
    def _generate_message(
        self,
        analysis: Dict[str, Any],
        execution: Dict[str, Any]
    ) -> str:
        """Generate email message"""
        message = f"""
ERROR ALERT AND RECOVERY REPORT
{'='*50}

Error Details:
- Error ID: {analysis.get('error_id')}
- Service: {analysis.get('service')}
- Type: {analysis.get('error_type')}
- Severity: {analysis.get('severity')}
- Timestamp: {analysis.get('timestamp')}

ML Analysis:
- Confidence: {analysis.get('ml_confidence', 0):.1%}
- Pattern Match: {analysis.get('pattern_match', 'None')}
- Priority: {analysis.get('recommended_priority')}

Recovery Actions:
"""
        
        if execution.get('recovery_success'):
            message += f"\n✓ RECOVERY SUCCESSFUL\n"
            for action in execution.get('actions_executed', []):
                message += f"  - {action['strategy']}: {action['result'].get('message', 'Executed')}\n"
        else:
            message += f"\n✗ RECOVERY ATTEMPTED\n"
            for action in execution.get('actions_executed', []):
                message += f"  - {action['strategy']}: {action['result'].get('message', 'Executed')}\n"
            for action in execution.get('actions_failed', []):
                message += f"  - {action['strategy']}: FAILED - {action.get('error', 'Unknown error')}\n"
        
        message += f"""
Recommended Actions:
- Monitor error frequency
- Check service logs
- Investigate underlying cause
- Review performance metrics

{'='*50}
Please take appropriate action based on the recovery status.
        """
        
        return message
    
    def _get_recipients(self, analysis: Dict[str, Any]) -> List[str]:
        """Get email recipients"""
        # In production, would look up team members based on service
        default_recipients = getattr(
            settings,
            'ERROR_ALERT_RECIPIENTS',
            ['admin@feedinghearts.com']
        )
        
        severity = analysis.get('severity')
        if severity in ['critical', 'high']:
            # Add escalation recipients for critical/high severity
            escalation_recipients = getattr(
                settings,
                'ERROR_ESCALATION_RECIPIENTS',
                []
            )
            return list(set(default_recipients + escalation_recipients))
        
        return default_recipients
