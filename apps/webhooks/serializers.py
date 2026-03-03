from rest_framework import serializers
from .models import WebhookConfig, WebhookDelivery


class WebhookConfigSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = WebhookConfig
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'delivered_at']


class WebhookDeliveryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing webhook deliveries"""
    class Meta:
        model = WebhookDelivery
        fields = ['id', 'event_type', 'status', 'attempt_count', 'response_status_code',
                  'created_at', 'delivered_at']
