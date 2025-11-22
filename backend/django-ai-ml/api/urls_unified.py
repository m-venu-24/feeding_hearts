"""
URL Configuration for Unified Phase API
Routing for all 10 phases working together
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views_unified import (
    UnifiedPhaseViewSet, UnifiedEventViewSet, PhaseConnectionViewSet,
    UnifiedSystemHealthView, UnifiedSystemDashboardView,
    UnifiedAPIDocumentationView, UnifiedPhaseAnalyticsView
)

# Create router
router = DefaultRouter()
router.register(r'phases', UnifiedPhaseViewSet, basename='unified-phase')
router.register(r'events', UnifiedEventViewSet, basename='unified-event')
router.register(r'connections', PhaseConnectionViewSet, basename='phase-connection')

# URL patterns
urlpatterns = [
    # Router patterns
    path('', include(router.urls)),
    
    # System health and dashboard
    path('health/', UnifiedSystemHealthView.as_view(), name='unified-health'),
    path('dashboard/', UnifiedSystemDashboardView.as_view(), name='unified-dashboard'),
    path('docs/', UnifiedAPIDocumentationView.as_view(), name='unified-docs'),
    path('analytics/', UnifiedPhaseAnalyticsView.as_view(), name='unified-analytics'),
]
