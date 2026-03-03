from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Integration, IntegrationLog
from .serializers import IntegrationSerializer, IntegrationLogSerializer


class IntegrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing third-party integrations.
    """
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'integration_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['created_at', 'last_sync_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Trigger a sync with this integration"""
        integration = self.get_object()
        # TODO: Implement integration sync logic
        return Response({
            'message': 'Sync initiated',
            'integration': integration.name
        })

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get sync logs for this integration"""
        integration = self.get_object()
        logs = integration.logs.all()[:50]  # Last 50 logs
        serializer = IntegrationLogSerializer(logs, many=True)
        return Response(serializer.data)


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing integration logs.
    Read-only access.
    """
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['integration', 'action', 'success']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
