from rest_framework import serializers
from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "uuid",
            "campaign_name",
            "is_active",
            "sale_cycle",
            "call_type",
            "phone_no",
            "call_flow_url",
            "test_call_url",
            "agent_id",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_by", "created_at", "updated_by", "updated_at"]
