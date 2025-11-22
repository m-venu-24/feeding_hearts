from django.urls import path
from .views import PredictionViewSet

prediction_list = PredictionViewSet.as_view({
    'post': 'list'
})

urlpatterns = [
    path('donation-demand/', PredictionViewSet.as_view({'post': 'predict_donation_demand'}), name='predict-demand'),
    path('recommend/', PredictionViewSet.as_view({'post': 'recommend_donations'}), name='recommend'),
    path('anomaly/', PredictionViewSet.as_view({'post': 'detect_anomaly'}), name='detect-anomaly'),
]
