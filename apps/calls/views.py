from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Sum, Count
from .models import Call, AIAnalysis, CallRecording, CallCost
from .serializers import (
    CallSerializer,
    CallListSerializer,
    AIAnalysisSerializer,
    CallRecordingSerializer,
    CallCostSerializer
)


class CallViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing calls.

    list: Get list of calls
    retrieve: Get specific call details with AI analysis
    create: Create new call record
    update: Update call
    """
    queryset = Call.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'agent', 'lead', 'status', 'outcome']
    search_fields = ['lead__first_name', 'lead__last_name', 'lead__phone_e164']
    ordering_fields = ['created_at', 'started_at', 'duration_seconds']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CallListSerializer
        return CallSerializer

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get aggregate call metrics"""
        queryset = self.filter_queryset(self.get_queryset())

        metrics = queryset.aggregate(
            total_calls=Count('id'),
            total_answered=Count('id', filter=queryset.filter(outcome='answered').values('id')),
            avg_duration=Avg('duration_seconds'),
            total_duration=Sum('duration_seconds'),
            total_tokens=Sum('tokens_consumed')
        )

        metrics['answer_rate'] = (
            (metrics['total_answered'] / metrics['total_calls'] * 100)
            if metrics['total_calls'] > 0 else 0
        )

        return Response(metrics)


class AIAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing AI call analysis.
    Read-only access.
    """
    queryset = AIAnalysis.objects.all()
    serializer_class = AIAnalysisSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['call', 'sentiment']
    ordering_fields = ['processed_at', 'sentiment_score']
    ordering = ['-processed_at']


class CallRecordingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing call recordings.
    Read-only access to recording metadata.
    """
    queryset = CallRecording.objects.all()
    serializer_class = CallRecordingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['call', 'is_deleted', 'format']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class CallCostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing call costs.
    Read-only access for billing data.
    """
    queryset = CallCost.objects.all()
    serializer_class = CallCostSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['call', 'voice_provider', 'ai_provider']
    ordering_fields = ['created_at', 'total_cost_usd']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def total_costs(self, request):
        """Get total costs aggregated"""
        queryset = self.filter_queryset(self.get_queryset())

        totals = queryset.aggregate(
            total_voice_cost=Sum('voice_total_cost'),
            total_ai_cost=Sum('ai_total_cost'),
            total_cost=Sum('total_cost_usd'),
            total_minutes=Sum('voice_minutes'),
            total_tokens=Sum('ai_tokens_consumed')
        )

        return Response(totals)
