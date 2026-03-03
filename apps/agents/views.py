from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import VoiceConfiguration, Agent, AgentVersion
from .serializers import (
    VoiceConfigurationSerializer,
    AgentSerializer,
    AgentListSerializer,
    AgentVersionSerializer
)


class VoiceConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing voice configurations.
    """
    queryset = VoiceConfiguration.objects.all()
    serializer_class = VoiceConfigurationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'provider', 'is_active', 'language_code']
    search_fields = ['name', 'provider']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']


class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AI voice agents.

    list: Get list of agents
    retrieve: Get specific agent details
    create: Create new agent
    update: Update agent
    partial_update: Partially update agent
    destroy: Delete agent (soft delete)
    """
    queryset = Agent.objects.filter(deleted_at__isnull=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'campaign', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'total_calls']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        return AgentSerializer

    def perform_destroy(self, instance):
        # Soft delete
        from django.utils import timezone
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of this agent"""
        agent = self.get_object()
        versions = agent.versions.all()
        serializer = AgentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get agent performance metrics"""
        agent = self.get_object()
        return Response({
            'total_calls': agent.total_calls,
            'successful_calls': agent.successful_calls,
            'success_rate': (agent.successful_calls / agent.total_calls * 100) if agent.total_calls > 0 else 0,
            'avg_rating': agent.avg_rating or 0
        })


class AgentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing agent versions.
    Read-only access to version history.
    """
    queryset = AgentVersion.objects.all()
    serializer_class = AgentVersionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['agent', 'is_active']
    ordering_fields = ['version_number', 'created_at']
    ordering = ['-version_number']
