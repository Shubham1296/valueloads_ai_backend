from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationLogViewSet

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')
router.register(r'logs', IntegrationLogViewSet, basename='integrationlog')

urlpatterns = [
    path('', include(router.urls)),
]
