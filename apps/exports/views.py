from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import DataExport
from .serializers import DataExportSerializer


class DataExportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing data exports.

    list: Get list of exports
    retrieve: Get specific export details
    create: Create new export job
    """
    queryset = DataExport.objects.all()
    serializer_class = DataExportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'export_type', 'status', 'requested_by']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        # Set requested_by to current user
        serializer.save(requested_by=self.request.user)
        # TODO: Queue background job to process export

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get download URL for completed export"""
        export = self.get_object()
        if export.status != 'completed':
            return Response(
                {'error': 'Export not completed yet'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'download_url': export.file_url,
            'expires_at': export.expires_at,
            'file_size_bytes': export.file_size_bytes,
            'row_count': export.row_count
        })
