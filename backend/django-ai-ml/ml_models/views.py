from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DonationPredictor, RecommendationEngine, AnomalyDetector
import numpy as np

class PredictionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def predict_donation_demand(self, request):
        """Predict donation demand for a location"""
        try:
            location = request.data.get('location')
            time_period = request.data.get('time_period', 'week')
            
            # Sample prediction (integrate real model)
            prediction = {
                'location': location,
                'predicted_demand': 150,  # Expected donations
                'confidence': 0.92,
                'time_period': time_period,
            }
            return Response(prediction, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def recommend_donations(self, request):
        """Get donation recommendations for user"""
        try:
            user_preferences = request.data.get('preferences', {})
            
            # Sample recommendations
            recommendations = [
                {
                    'donation_id': '1',
                    'food_type': 'Fresh Vegetables',
                    'score': 0.95,
                    'reason': 'Matches your dietary preferences'
                },
                {
                    'donation_id': '2',
                    'food_type': 'Organic Fruits',
                    'score': 0.88,
                    'reason': 'Popular in your area'
                },
            ]
            return Response(recommendations, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def detect_anomaly(self, request):
        """Check if donation pattern is suspicious"""
        try:
            donation_data = request.data
            is_suspicious, flags = AnomalyDetector.detect_fraud(donation_data)
            
            return Response({
                'is_suspicious': is_suspicious,
                'flags': flags,
                'confidence': 0.85,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
