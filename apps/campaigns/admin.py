from django.contrib import admin
from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["campaign_name", "call_type", "sale_cycle", "phone_no", "is_active", "created_at"]
    list_filter = ["is_active", "call_type", "sale_cycle"]
    search_fields = ["campaign_name", "phone_no", "agent_id"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
