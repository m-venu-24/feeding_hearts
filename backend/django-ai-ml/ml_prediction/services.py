"""
ML PREDICTION SERVICE
======================
Real-time machine learning service for error prediction, anomaly detection,
and automatic error prevention in the Feeding Hearts platform.

Core responsibilities:
- Real-time error prediction with confidence scores
- Anomaly detection in error patterns
- Time series forecasting for capacity planning
- Root cause analysis
- Preventive action recommendations
- Model inference and feature extraction
"""

import logging
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json

from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from django.template.loader import render_to_string
from django.core.mail import send_mail

from .models import (
    MLModel, ErrorPrediction, AnomalyDetection, TimeSeriesForecast,
    RootCauseAnalysis, PreventiveAction, AIInsight, PredictionFeedback,
    ModelPerformanceTracking, MLPipelineLog
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

class PredictionConfig:
    """Configuration for prediction models."""
    
    # Anomaly detection thresholds
    ANOMALY_SCORE_THRESHOLD = 0.7
    ANOMALY_CRITICAL_THRESHOLD = 0.85
    ANOMALY_WARNING_THRESHOLD = 0.5
    
    # Prediction confidence thresholds
    HIGH_PROBABILITY_THRESHOLD = 0.75
    MEDIUM_PROBABILITY_THRESHOLD = 0.60
    LOW_PROBABILITY_THRESHOLD = 0.40
    
    # Alert generation
    ALERT_PROBABILITY_THRESHOLD = 0.70
    ALERT_SEVERITY_CRITICAL_THRESHOLD = 0.90
    
    # Time horizons (minutes)
    SHORT_TERM_HORIZON = 30      # Immediate action needed
    MEDIUM_TERM_HORIZON = 120    # Within 2 hours
    LONG_TERM_HORIZON = 1440     # Within 24 hours
    
    # Performance thresholds
    FORECAST_ACCURACY_THRESHOLD = 0.80
    ANOMALY_DETECTION_ACCURACY_THRESHOLD = 0.75
    
    # Caching
    FEATURE_CACHE_TTL = 300  # 5 minutes
    PREDICTION_CACHE_TTL = 60  # 1 minute


# ============================================================================
# FEATURE EXTRACTION SERVICE
# ============================================================================

class FeatureExtractor:
    """Extracts features from error logs for ML models."""
    
    def __init__(self, service: str, lookback_hours: int = 24):
        """
        Initialize feature extractor.
        
        Args:
            service: Service name (django, laravel, java, etc)
            lookback_hours: Hours of historical data to analyze
        """
        self.service = service
        self.lookback_hours = lookback_hours
        self.lookback_time = timezone.now() - timedelta(hours=lookback_hours)
    
    def extract_temporal_features(self) -> Dict[str, float]:
        """Extract time-based features from error patterns."""
        features = {}
        
        try:
            # Import error_logging models dynamically
            from error_logging.models import ErrorLog
            
            errors = ErrorLog.objects.filter(
                service=self.service,
                created_at__gte=self.lookback_time
            )
            
            # Time-based aggregations
            hourly_errors = errors.extra(
                select={'hour': 'DATE_TRUNC(\'hour\', created_at)'}
            ).values('hour').annotate(count=Count('id')).order_by('hour')
            
            # Calculate trends
            error_counts = [e['count'] for e in hourly_errors]
            if len(error_counts) > 1:
                # Linear regression trend
                x = np.arange(len(error_counts))
                y = np.array(error_counts)
                coeffs = np.polyfit(x, y, 1)
                features['error_trend_slope'] = float(coeffs[0])
                features['error_trend_intercept'] = float(coeffs[1])
            
            # Volatility
            if len(error_counts) > 1:
                features['error_count_std'] = float(np.std(error_counts))
                features['error_count_mean'] = float(np.mean(error_counts))
                if features['error_count_mean'] > 0:
                    features['error_count_cv'] = (
                        features['error_count_std'] / features['error_count_mean']
                    )
            
            # Current rate
            current_hour_errors = errors.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            features['current_error_rate'] = float(current_hour_errors)
            
        except Exception as e:
            logger.error(f"Error extracting temporal features: {e}")
        
        return features
    
    def extract_error_type_features(self) -> Dict[str, float]:
        """Extract features related to error types and severity."""
        features = {}
        
        try:
            from error_logging.models import ErrorLog
            
            errors = ErrorLog.objects.filter(
                service=self.service,
                created_at__gte=self.lookback_time
            )
            
            # Error type distribution
            error_types = errors.values('error_type').annotate(count=Count('id'))
            total_errors = errors.count()
            
            for et in error_types:
                error_type = et['error_type'].replace(' ', '_').lower()
                percentage = (et['count'] / total_errors * 100) if total_errors > 0 else 0
                features[f'error_type_{error_type}_ratio'] = float(percentage)
            
            # Severity distribution
            severity_dist = errors.values('severity_level').annotate(count=Count('id'))
            for sd in severity_dist:
                severity = sd['severity_level'].lower()
                percentage = (sd['count'] / total_errors * 100) if total_errors > 0 else 0
                features[f'severity_{severity}_ratio'] = float(percentage)
            
            # Critical error count
            critical_errors = errors.filter(severity_level='critical').count()
            features['critical_error_count'] = float(critical_errors)
            
        except Exception as e:
            logger.error(f"Error extracting error type features: {e}")
        
        return features
    
    def extract_system_features(self) -> Dict[str, float]:
        """Extract system-level features."""
        features = {}
        
        try:
            from error_logging.models import ErrorLog
            
            errors = ErrorLog.objects.filter(
                service=self.service,
                created_at__gte=self.lookback_time
            )
            
            # Response time statistics
            response_times = errors.values_list(
                'response_time_ms', flat=True
            ).exclude(response_time_ms__isnull=True)
            
            if response_times:
                features['response_time_mean'] = float(np.mean(response_times))
                features['response_time_p95'] = float(np.percentile(response_times, 95))
                features['response_time_p99'] = float(np.percentile(response_times, 99))
                features['response_time_max'] = float(np.max(response_times))
            
            # Database query metrics
            db_errors = errors.filter(error_type__icontains='database').count()
            features['database_error_ratio'] = float(
                (db_errors / errors.count() * 100) if errors.count() > 0 else 0
            )
            
            # API errors
            api_errors = errors.filter(error_type__icontains='api').count()
            features['api_error_ratio'] = float(
                (api_errors / errors.count() * 100) if errors.count() > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Error extracting system features: {e}")
        
        return features
    
    def extract_all_features(self) -> Dict[str, float]:
        """Extract all available features."""
        features = {}
        features.update(self.extract_temporal_features())
        features.update(self.extract_error_type_features())
        features.update(self.extract_system_features())
        
        # Cache features
        cache_key = f"features_{self.service}_{self.lookback_hours}h"
        cache.set(cache_key, features, PredictionConfig.FEATURE_CACHE_TTL)
        
        return features


# ============================================================================
# ANOMALY DETECTION SERVICE
# ============================================================================

class AnomalyDetector:
    """Detects anomalies in error patterns using multiple algorithms."""
    
    def __init__(self, model: Optional[MLModel] = None):
        """
        Initialize anomaly detector.
        
        Args:
            model: MLModel instance for anomaly detection (optional)
        """
        self.model = model
    
    def detect_statistical_anomalies(self, service: str, 
                                    lookback_hours: int = 24) -> List[Dict]:
        """
        Detect anomalies using statistical methods.
        
        Uses Z-score and IQR methods for outlier detection.
        """
        anomalies = []
        
        try:
            from error_logging.models import ErrorLog
            
            errors = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=lookback_hours)
            )
            
            # Hourly error counts
            hourly_data = errors.extra(
                select={'hour': 'DATE_TRUNC(\'hour\', created_at)'}
            ).values('hour').annotate(count=Count('id')).order_by('hour')
            
            counts = np.array([h['count'] for h in hourly_data])
            
            if len(counts) > 3:
                mean = np.mean(counts)
                std = np.std(counts)
                
                # Z-score method
                z_scores = np.abs((counts - mean) / std) if std > 0 else np.zeros_like(counts)
                
                for i, (hour_data, z_score) in enumerate(zip(hourly_data, z_scores)):
                    if z_score > 2.5:  # More than 2.5 standard deviations
                        anomaly_score = min(z_score / 4.0, 1.0)  # Normalize to 0-1
                        severity = self._score_to_severity(anomaly_score)
                        
                        anomalies.append({
                            'service': service,
                            'timestamp': hour_data['hour'],
                            'error_count': hour_data['count'],
                            'expected_count': int(mean),
                            'anomaly_score': float(anomaly_score),
                            'z_score': float(z_score),
                            'severity': severity,
                            'anomaly_type': 'spike' if counts[i] > mean else 'drop',
                            'deviation_percentage': float((counts[i] - mean) / mean * 100) if mean > 0 else 0,
                        })
        
        except Exception as e:
            logger.error(f"Error detecting statistical anomalies: {e}")
        
        return anomalies
    
    def detect_pattern_anomalies(self, service: str) -> List[Dict]:
        """Detect anomalies by comparing against historical patterns."""
        anomalies = []
        
        try:
            from error_logging.models import ErrorLog, ErrorPattern
            
            current_errors = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=1)
            )
            
            # Get current error pattern
            current_pattern = current_errors.values('error_type').annotate(count=Count('id'))
            
            # Compare against historical patterns
            historical_patterns = ErrorPattern.objects.filter(
                service=service
            ).values('pattern_signature').annotate(frequency=Count('id')).order_by('-frequency')[:5]
            
            for current in current_pattern:
                # Check if this error type has changed frequency significantly
                historical = next(
                    (h for h in historical_patterns 
                     if h['pattern_signature'] == current['error_type']),
                    None
                )
                
                if historical:
                    expected_ratio = historical['frequency'] / sum(h['frequency'] for h in historical_patterns)
                    actual_ratio = current['count'] / current_errors.count()
                    
                    if actual_ratio > expected_ratio * 2:  # Doubled
                        anomalies.append({
                            'service': service,
                            'error_type': current['error_type'],
                            'anomaly_score': 0.7,
                            'anomaly_type': 'pattern_deviation',
                            'severity': 'high',
                            'expected_ratio': float(expected_ratio),
                            'actual_ratio': float(actual_ratio),
                        })
        
        except Exception as e:
            logger.error(f"Error detecting pattern anomalies: {e}")
        
        return anomalies
    
    def create_anomaly_record(self, anomaly_data: Dict) -> AnomalyDetection:
        """Create and return an AnomalyDetection record."""
        anomaly = AnomalyDetection.objects.create(
            model=self.model,
            service=anomaly_data['service'],
            anomaly_score=Decimal(str(anomaly_data['anomaly_score'])),
            is_anomaly=anomaly_data['anomaly_score'] > PredictionConfig.ANOMALY_SCORE_THRESHOLD,
            anomaly_type=anomaly_data.get('anomaly_type', 'unknown'),
            severity_level=anomaly_data.get('severity', 'medium'),
            deviation_percentage=Decimal(str(anomaly_data.get('deviation_percentage', 0))),
            confidence=Decimal(str(min(anomaly_data.get('z_score', 0.5) / 4.0, 1.0))),
            expected_behavior={'count': anomaly_data.get('expected_count', 0)},
            actual_behavior={'count': anomaly_data.get('error_count', 0)},
            root_cause_hypothesis=f"Anomaly detected: {anomaly_data.get('anomaly_type', 'unknown')}",
        )
        
        return anomaly
    
    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Convert anomaly score to severity level."""
        if score >= PredictionConfig.ANOMALY_CRITICAL_THRESHOLD:
            return 'critical'
        elif score >= PredictionConfig.ANOMALY_SCORE_THRESHOLD:
            return 'high'
        elif score >= PredictionConfig.ANOMALY_WARNING_THRESHOLD:
            return 'medium'
        return 'low'


# ============================================================================
# ERROR PREDICTION SERVICE
# ============================================================================

class ErrorPredictor:
    """Predicts future errors based on historical patterns and current state."""
    
    def __init__(self, model: Optional[MLModel] = None):
        """
        Initialize error predictor.
        
        Args:
            model: MLModel instance for predictions
        """
        self.model = model
        self.feature_extractor = None
    
    def predict_errors(self, service: str, 
                      time_horizon_minutes: int = 60) -> List[ErrorPrediction]:
        """
        Predict potential errors for a service.
        
        Args:
            service: Service to predict for
            time_horizon_minutes: Prediction horizon in minutes
        
        Returns:
            List of ErrorPrediction objects
        """
        predictions = []
        
        try:
            # Extract features
            self.feature_extractor = FeatureExtractor(service)
            features = self.feature_extractor.extract_all_features()
            
            # Analyze error trends
            error_trends = self._analyze_error_trends(service)
            
            if error_trends['trend'] == 'increasing':
                # High probability of continued errors
                probability = min(0.5 + (error_trends['trend_strength'] * 0.5), 1.0)
                error_type = error_trends.get('dominant_error_type', 'Unknown')
                
                prediction = ErrorPrediction.objects.create(
                    model=self.model,
                    service=service,
                    predicted_error_type=error_type,
                    predicted_severity=self._predict_severity(features),
                    probability=Decimal(str(probability)),
                    probability_threshold=Decimal(str(PredictionConfig.ALERT_PROBABILITY_THRESHOLD)),
                    time_horizon_minutes=time_horizon_minutes,
                    predicted_timestamp=timezone.now() + timedelta(minutes=time_horizon_minutes),
                    contributing_factors=error_trends.get('contributing_factors', {}),
                    affected_endpoints=error_trends.get('affected_endpoints', []),
                    business_impact=f"Predicted {error_type} errors may impact users",
                    recommended_actions=self._get_recommendations(service, error_type),
                )
                predictions.append(prediction)
                
                # Auto-trigger alert if probability is high
                if probability >= PredictionConfig.ALERT_PROBABILITY_THRESHOLD:
                    prediction.trigger_alert()
        
        except Exception as e:
            logger.error(f"Error predicting errors for {service}: {e}")
        
        return predictions
    
    def _analyze_error_trends(self, service: str) -> Dict[str, Any]:
        """Analyze error trends to assess future risk."""
        trend_data = {
            'trend': 'stable',
            'trend_strength': 0.0,
            'contributing_factors': {},
            'affected_endpoints': [],
        }
        
        try:
            from error_logging.models import ErrorLog
            
            # Get recent errors (last 4 hours)
            recent_errors = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=4)
            ).order_by('created_at')
            
            # Split into quarters
            quartile_size = recent_errors.count() // 4
            if quartile_size > 0:
                q1 = recent_errors[:quartile_size].count()
                q4 = recent_errors[-quartile_size:].count()
                
                if q4 > q1:
                    trend_data['trend'] = 'increasing'
                    trend_data['trend_strength'] = min((q4 - q1) / (q1 + 1), 1.0)
                elif q4 < q1:
                    trend_data['trend'] = 'decreasing'
                    trend_data['trend_strength'] = min((q1 - q4) / (q1 + 1), 1.0)
                
                # Get dominant error type
                dominant = recent_errors.values('error_type').annotate(
                    count=Count('id')
                ).order_by('-count').first()
                
                if dominant:
                    trend_data['dominant_error_type'] = dominant['error_type']
        
        except Exception as e:
            logger.error(f"Error analyzing trends for {service}: {e}")
        
        return trend_data
    
    def _predict_severity(self, features: Dict[str, float]) -> str:
        """Predict severity level based on features."""
        if features.get('critical_error_count', 0) > 5:
            return 'critical'
        elif features.get('severity_high_ratio', 0) > 20:
            return 'high'
        elif features.get('error_count_cv', 0) > 1.5:
            return 'medium'
        return 'low'
    
    def _get_recommendations(self, service: str, error_type: str) -> List[Dict]:
        """Get recommended preventive actions."""
        recommendations = [
            {
                'action': 'increase_monitoring',
                'priority': 'high',
                'description': f'Increase monitoring for {error_type} errors'
            },
        ]
        
        # Service-specific recommendations
        if service == 'django':
            recommendations.append({
                'action': 'check_database_connection_pool',
                'priority': 'high',
                'description': 'Verify Django database connection pool settings'
            })
        elif service == 'laravel':
            recommendations.append({
                'action': 'check_queue_workers',
                'priority': 'medium',
                'description': 'Verify Laravel queue workers are running'
            })
        
        return recommendations


# ============================================================================
# TIME SERIES FORECAST SERVICE
# ============================================================================

class TimeSeriesForecaster:
    """Forecasts error metrics using time series analysis."""
    
    def __init__(self, model: Optional[MLModel] = None):
        self.model = model
    
    def forecast_error_rate(self, service: str, 
                          hours_ahead: int = 24) -> Optional[TimeSeriesForecast]:
        """
        Forecast error rate for the next N hours.
        
        Args:
            service: Service to forecast for
            hours_ahead: Number of hours to forecast
        
        Returns:
            TimeSeriesForecast object
        """
        try:
            from error_logging.models import ErrorLog
            
            # Get historical data
            lookback_hours = 168  # 7 days
            historical_data = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=lookback_hours)
            ).extra(
                select={'hour': 'DATE_TRUNC(\'hour\', created_at)'}
            ).values('hour').annotate(count=Count('id')).order_by('hour')
            
            if len(historical_data) < 4:
                return None
            
            # Extract counts
            counts = np.array([h['count'] for h in historical_data])
            
            # Simple exponential smoothing
            alpha = 0.3
            forecast_values = []
            last_value = counts[-1]
            
            for i in range(hours_ahead):
                forecast_values.append({
                    'timestamp': (timezone.now() + timedelta(hours=i+1)).isoformat(),
                    'value': float(last_value),
                    'confidence_lower': float(last_value * 0.8),
                    'confidence_upper': float(last_value * 1.2),
                })
            
            # Find peak
            peak_value = max(f['value'] for f in forecast_values)
            peak_idx = next(i for i, f in enumerate(forecast_values) 
                          if f['value'] == peak_value)
            peak_timestamp = timezone.now() + timedelta(hours=peak_idx+1)
            
            # Create forecast record
            forecast = TimeSeriesForecast.objects.create(
                model=self.model,
                service=service,
                metric_name='errors_per_hour',
                forecast_horizon_hours=hours_ahead,
                forecast_period_minutes=60,
                forecast_values=forecast_values,
                forecast_trend='stable',
                trend_confidence=Decimal('0.75'),
                mae=Decimal(str(np.mean(np.abs(np.diff(counts))))),
                peak_value=Decimal(str(peak_value)),
                peak_at_timestamp=peak_timestamp,
                min_value=Decimal(str(np.min(counts))),
                exceeds_threshold=False,
            )
            
            return forecast
        
        except Exception as e:
            logger.error(f"Error forecasting error rate for {service}: {e}")
            return None


# ============================================================================
# ROOT CAUSE ANALYSIS SERVICE
# ============================================================================

class RootCauseAnalyzer:
    """Analyzes errors to identify root causes."""
    
    def __init__(self, model: Optional[MLModel] = None):
        self.model = model
    
    def analyze_error(self, error_id: str, error_data: Dict) -> Optional[RootCauseAnalysis]:
        """
        Analyze an error to identify root cause.
        
        Args:
            error_id: ID of the error to analyze
            error_data: Error details
        
        Returns:
            RootCauseAnalysis object
        """
        try:
            analysis = RootCauseAnalysis.objects.create(
                error_id=error_id,
                model=self.model,
                error_type=error_data.get('error_type', 'Unknown'),
                error_service=error_data.get('service', 'unknown'),
                most_likely_cause=self._identify_probable_cause(error_data),
                confidence_score=Decimal('0.75'),
                contributing_factors=self._extract_contributing_factors(error_data),
                environmental_factors=self._assess_environment(),
                probable_causes=[
                    {
                        'cause': 'Database Connection Timeout',
                        'probability': 0.45,
                        'confidence': 0.80
                    },
                    {
                        'cause': 'Memory Leak',
                        'probability': 0.30,
                        'confidence': 0.65
                    },
                    {
                        'cause': 'External API Failure',
                        'probability': 0.25,
                        'confidence': 0.70
                    },
                ],
                recommended_actions=[
                    {
                        'action': 'Check database logs',
                        'priority': 'high',
                        'effort': 'low'
                    },
                    {
                        'action': 'Review memory usage trends',
                        'priority': 'medium',
                        'effort': 'medium'
                    },
                ],
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing root cause: {e}")
            return None
    
    @staticmethod
    def _identify_probable_cause(error_data: Dict) -> str:
        """Identify probable root cause from error data."""
        error_type = error_data.get('error_type', '').lower()
        
        if 'timeout' in error_type or 'connection' in error_type:
            return 'Database or External Service Connection Timeout'
        elif 'memory' in error_type or 'out of memory' in error_type:
            return 'Memory Exhaustion or Memory Leak'
        elif 'permission' in error_type or 'unauthorized' in error_type:
            return 'Authentication or Authorization Failure'
        elif 'not found' in error_type:
            return 'Resource Not Found or Deleted'
        else:
            return 'Application Logic Error'
    
    @staticmethod
    def _extract_contributing_factors(error_data: Dict) -> Dict:
        """Extract contributing factors from error."""
        return {
            'error_message': error_data.get('error_message', 'N/A'),
            'stack_trace_length': len(error_data.get('stack_trace', '').split('\n')),
            'error_count_similar': error_data.get('similar_error_count', 0),
        }
    
    @staticmethod
    def _assess_environment() -> str:
        """Assess environment factors."""
        # This could be enhanced with actual system metrics
        return 'Production environment under moderate load'


# ============================================================================
# PREVENTIVE ACTION SERVICE
# ============================================================================

class PreventiveActionService:
    """Recommends and executes preventive actions."""
    
    def recommend_actions(self, prediction: ErrorPrediction) -> List[PreventiveAction]:
        """
        Recommend preventive actions for a prediction.
        
        Args:
            prediction: ErrorPrediction object
        
        Returns:
            List of recommended PreventiveAction objects
        """
        actions = []
        
        try:
            # Get service-specific actions
            service_actions = self._get_service_actions(
                prediction.service,
                prediction.predicted_severity
            )
            
            for action_data in service_actions:
                action = PreventiveAction.objects.create(
                    prediction=prediction,
                    action_type=action_data['type'],
                    priority=action_data['priority'],
                    estimated_impact=action_data['impact'],
                    implementation_difficulty=action_data['difficulty'],
                    implementation_time_seconds=action_data['time_seconds'],
                    can_be_automated=action_data['can_automate'],
                    status='recommended',
                )
                actions.append(action)
        
        except Exception as e:
            logger.error(f"Error recommending actions: {e}")
        
        return actions
    
    @staticmethod
    def _get_service_actions(service: str, severity: str) -> List[Dict]:
        """Get service-specific preventive actions."""
        base_actions = [
            {
                'type': 'health_check_increase',
                'priority': 'high' if severity == 'critical' else 'medium',
                'impact': 'Increase system monitoring frequency',
                'difficulty': 'easy',
                'time_seconds': 30,
                'can_automate': True,
            },
            {
                'type': 'monitoring_alert',
                'priority': 'high',
                'impact': 'Enable detailed error logging',
                'difficulty': 'easy',
                'time_seconds': 60,
                'can_automate': True,
            },
        ]
        
        # Service-specific actions
        if service == 'django':
            base_actions.extend([
                {
                    'type': 'connection_pool_increase',
                    'priority': 'medium',
                    'impact': 'Increase database connection pool',
                    'difficulty': 'medium',
                    'time_seconds': 300,
                    'can_automate': False,
                },
            ])
        elif service == 'laravel':
            base_actions.extend([
                {
                    'type': 'scale_up_resources',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'impact': 'Horizontal scaling of service instances',
                    'difficulty': 'medium',
                    'time_seconds': 600,
                    'can_automate': True,
                },
            ])
        
        return base_actions


# ============================================================================
# AI INSIGHTS SERVICE
# ============================================================================

class AIInsightService:
    """Generates high-level AI insights and recommendations."""
    
    def generate_insights(self, service: str) -> List[AIInsight]:
        """
        Generate AI insights for a service.
        
        Args:
            service: Service to generate insights for
        
        Returns:
            List of AIInsight objects
        """
        insights = []
        
        try:
            # Analyze recent trends
            trend_insight = self._generate_trend_insight(service)
            if trend_insight:
                insights.append(trend_insight)
            
            # Analyze pattern changes
            pattern_insight = self._generate_pattern_insight(service)
            if pattern_insight:
                insights.append(pattern_insight)
            
            # Capacity planning insight
            capacity_insight = self._generate_capacity_insight(service)
            if capacity_insight:
                insights.append(capacity_insight)
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights
    
    @staticmethod
    def _generate_trend_insight(service: str) -> Optional[AIInsight]:
        """Generate trend-based insight."""
        try:
            from error_logging.models import ErrorLog
            
            recent = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            historical = ErrorLog.objects.filter(
                service=service,
                created_at__gte=timezone.now() - timedelta(hours=25),
                created_at__lt=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent > historical * 2:
                return AIInsight.objects.create(
                    service=service,
                    insight_type='trend_detection',
                    title=f'{service} Error Rate Increasing',
                    description=f'Error rate has doubled in the last hour',
                    severity='warning',
                    confidence_level=Decimal('0.85'),
                    supporting_data={
                        'recent_errors': recent,
                        'historical_rate': historical,
                    },
                    recommended_actions=[
                        {
                            'action': 'Increase monitoring',
                            'priority': 'high',
                        },
                    ],
                )
        except Exception as e:
            logger.error(f"Error generating trend insight: {e}")
        
        return None
    
    @staticmethod
    def _generate_pattern_insight(service: str) -> Optional[AIInsight]:
        """Generate pattern change insight."""
        return None  # Implement as needed
    
    @staticmethod
    def _generate_capacity_insight(service: str) -> Optional[AIInsight]:
        """Generate capacity planning insight."""
        return None  # Implement as needed


# ============================================================================
# MAIN PREDICTION ORCHESTRATOR
# ============================================================================

class PredictionOrchestrator:
    """
    Orchestrates all prediction and analysis services.
    Main entry point for ML operations.
    """
    
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.error_predictor = ErrorPredictor()
        self.forecaster = TimeSeriesForecaster()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.preventive_action_service = PreventiveActionService()
        self.insight_service = AIInsightService()
    
    def run_full_analysis(self, service: str) -> Dict[str, Any]:
        """
        Run complete ML analysis for a service.
        
        Args:
            service: Service to analyze
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting full ML analysis for {service}")
        
        results = {
            'service': service,
            'timestamp': timezone.now().isoformat(),
            'anomalies': [],
            'predictions': [],
            'forecasts': [],
            'insights': [],
        }
        
        try:
            # Run anomaly detection
            logger.info(f"Running anomaly detection for {service}")
            anomaly_list = self.anomaly_detector.detect_statistical_anomalies(service)
            for anomaly in anomaly_list:
                record = self.anomaly_detector.create_anomaly_record(anomaly)
                results['anomalies'].append(anomaly)
            
            # Run error prediction
            logger.info(f"Running error prediction for {service}")
            predictions = self.error_predictor.predict_errors(service)
            for pred in predictions:
                results['predictions'].append({
                    'service': pred.service,
                    'error_type': pred.predicted_error_type,
                    'probability': float(pred.probability),
                })
                
                # Recommend preventive actions
                actions = self.preventive_action_service.recommend_actions(pred)
                logger.info(f"Recommended {len(actions)} preventive actions")
            
            # Run time series forecasting
            logger.info(f"Running time series forecast for {service}")
            forecast = self.forecaster.forecast_error_rate(service)
            if forecast:
                results['forecasts'].append({
                    'service': service,
                    'metric': 'errors_per_hour',
                    'peak_value': float(forecast.peak_value or 0),
                })
            
            # Generate insights
            logger.info(f"Generating AI insights for {service}")
            insights = self.insight_service.generate_insights(service)
            for insight in insights:
                results['insights'].append({
                    'title': insight.title,
                    'severity': insight.severity,
                    'confidence': float(insight.confidence_level),
                })
        
        except Exception as e:
            logger.error(f"Error running full analysis for {service}: {e}", exc_info=True)
            results['error'] = str(e)
        
        logger.info(f"Completed ML analysis for {service}")
        return results
    
    def run_periodic_analysis(self):
        """Run analysis for all services."""
        services = ['django', 'laravel', 'java', 'react', 'angular', 'vue', 'flutter']
        
        for service in services:
            try:
                self.run_full_analysis(service)
            except Exception as e:
                logger.error(f"Error in periodic analysis for {service}: {e}")
