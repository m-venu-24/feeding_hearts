"""
Error Logging API URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ErrorLogViewSet, DeveloperAssignmentViewSet,
    ErrorPatternViewSet, ErrorNotificationViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'errors', ErrorLogViewSet, basename='errorlog')
router.register(r'developers', DeveloperAssignmentViewSet, basename='developer')
router.register(r'patterns', ErrorPatternViewSet, basename='errorpattern')
router.register(r'notifications', ErrorNotificationViewSet, basename='errornotification')

app_name = 'error_logging'

urlpatterns = [
    path('', include(router.urls)),
]
