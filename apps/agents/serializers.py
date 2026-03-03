from rest_framework import serializers
from .models import VoiceConfiguration, Agent, AgentVersion


class VoiceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AgentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentVersion
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AgentSerializer(serializers.ModelSerializer):
    voice_config_name = serializers.CharField(source='voice_config.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = ['id', 'total_calls', 'successful_calls', 'avg_rating', 'created_at', 'updated_at']


class AgentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing agents"""
    voice_config_name = serializers.CharField(source='voice_config.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)

    class Meta:
        model = Agent
        fields = ['id', 'name', 'status', 'campaign', 'campaign_name', 'voice_config_name',
                  'total_calls', 'successful_calls', 'created_at']
