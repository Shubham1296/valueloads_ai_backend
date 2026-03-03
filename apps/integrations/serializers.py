from rest_framework import serializers
from .models import Integration, IntegrationLog


class IntegrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Integration
        fields = '__all__'
        read_only_fields = ['id', 'last_sync_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'credentials': {'write_only': True}  # Don't expose credentials in responses
        }


class IntegrationLogSerializer(serializers.ModelSerializer):
    integration_name = serializers.CharField(source='integration.name', read_only=True)

    class Meta:
        model = IntegrationLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
