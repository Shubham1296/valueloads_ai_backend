from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookConfigViewSet, WebhookDeliveryViewSet

router = DefaultRouter()
router.register(r'configs', WebhookConfigViewSet, basename='webhookconfig')
router.register(r'deliveries', WebhookDeliveryViewSet, basename='webhookdelivery')

urlpatterns = [
    path('', include(router.urls)),
]
