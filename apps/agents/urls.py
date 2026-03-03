from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VoiceConfigurationViewSet, AgentViewSet, AgentVersionViewSet

router = DefaultRouter()
router.register(r'voice-configs', VoiceConfigurationViewSet, basename='voiceconfiguration')
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent-versions', AgentVersionViewSet, basename='agentversion')

urlpatterns = [
    path('', include(router.urls)),
]
