from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lead, LeadImportBatch, LeadNote
from .serializers import (
    LeadSerializer,
    LeadListSerializer,
    LeadImportBatchSerializer,
    LeadNoteSerializer
)


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leads.

    list: Get list of leads with filtering
    retrieve: Get specific lead details
    create: Create new lead
    update: Update lead
    partial_update: Partially update lead
    destroy: Delete lead (soft delete)
    """
    queryset = Lead.objects.filter(deleted_at__isnull=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'agent', 'campaign', 'status', 'disposition', 'is_verified']
    search_fields = ['first_name', 'last_name', 'phone_e164', 'email']
    ordering_fields = ['created_at', 'last_called_at', 'schedule_at', 'lead_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer

    def perform_destroy(self, instance):
        # Soft delete
        from django.utils import timezone
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to this lead"""
        lead = self.get_object()
        serializer = LeadNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lead=lead, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def call_history(self, request, pk=None):
        """Get call history for this lead"""
        lead = self.get_object()
        calls = lead.calls.all().order_by('-created_at')
        from apps.calls.serializers import CallListSerializer
        serializer = CallListSerializer(calls, many=True)
        return Response(serializer.data)


class LeadImportBatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing lead import batches.
    """
    queryset = LeadImportBatch.objects.all()
    serializer_class = LeadImportBatchSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'campaign', 'status']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']


class LeadNoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing lead notes.
    """
    queryset = LeadNote.objects.all()
    serializer_class = LeadNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lead', 'is_pinned']
    ordering_fields = ['created_at', 'is_pinned']
    ordering = ['-is_pinned', '-created_at']
