from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallViewSet, AIAnalysisViewSet, CallRecordingViewSet, CallCostViewSet

router = DefaultRouter()
router.register(r'calls', CallViewSet, basename='call')
router.register(r'ai-analysis', AIAnalysisViewSet, basename='aianalysis')
router.register(r'recordings', CallRecordingViewSet, basename='callrecording')
router.register(r'costs', CallCostViewSet, basename='callcost')

urlpatterns = [
    path('', include(router.urls)),
]
