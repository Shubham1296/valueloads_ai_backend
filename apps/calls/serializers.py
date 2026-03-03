from rest_framework import serializers
from .models import Call, AIAnalysis, CallRecording, CallCost


class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = '__all__'
        read_only_fields = ['id', 'processed_at']


class CallRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecording
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CallCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallCost
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CallSerializer(serializers.ModelSerializer):
    lead_name = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    ai_analysis = AIAnalysisSerializer(read_only=True)
    recording = CallRecordingSerializer(read_only=True)
    cost = CallCostSerializer(read_only=True)

    class Meta:
        model = Call
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_lead_name(self, obj):
        return f"{obj.lead.first_name} {obj.lead.last_name}"


class CallListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing calls"""
    lead_name = serializers.SerializerMethodField()
    agent_name = serializers.CharField(source='agent.name', read_only=True)

    class Meta:
        model = Call
        fields = ['id', 'lead', 'lead_name', 'agent', 'agent_name', 'status', 'outcome',
                  'duration_seconds', 'tokens_consumed', 'created_at']

    def get_lead_name(self, obj):
        return f"{obj.lead.first_name} {obj.lead.last_name}"
