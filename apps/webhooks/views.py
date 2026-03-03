from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import WebhookConfig, WebhookDelivery
from .serializers import (
    WebhookConfigSerializer,
    WebhookDeliverySerializer,
    WebhookDeliveryListSerializer
)


class WebhookConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing webhook configurations.
    One config per company.
    """
    queryset = WebhookConfig.objects.all()
    serializer_class = WebhookConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'is_active']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test webhook event"""
        webhook_config = self.get_object()
        # TODO: Implement webhook test logic
        return Response({
            'message': 'Test webhook queued',
            'webhook_url': webhook_config.url
        })


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing webhook delivery logs.
    Read-only access.
    """
    queryset = WebhookDelivery.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['webhook_config', 'call', 'event_type', 'status']
    ordering_fields = ['created_at', 'delivered_at', 'attempt_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return WebhookDeliveryListSerializer
        return WebhookDeliverySerializer

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Manually retry a failed webhook delivery"""
        delivery = self.get_object()
        if delivery.status == 'failed':
            # TODO: Implement retry logic
            return Response({'message': 'Webhook retry queued'})
        return Response(
            {'error': 'Can only retry failed deliveries'},
            status=status.HTTP_400_BAD_REQUEST
        )
