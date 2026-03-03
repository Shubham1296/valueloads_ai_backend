from rest_framework import serializers
from .models import Lead, LeadImportBatch, LeadNote


class LeadNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = LeadNote
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    notes = LeadNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['id', 'attempts_count', 'successful_contact_count', 'created_at',
                            'updated_at', 'call_lock_acquired_at']


class LeadListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing leads"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)

    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'phone_e164', 'email', 'status',
                  'disposition', 'agent', 'agent_name', 'campaign', 'campaign_name',
                  'attempts_count', 'created_at']


class LeadImportBatchSerializer(serializers.ModelSerializer):
    imported_by_name = serializers.CharField(source='imported_by.full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)

    class Meta:
        model = LeadImportBatch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'completed_at']
