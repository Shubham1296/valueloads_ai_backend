from django.contrib import admin
from .models import WebhookConfig, WebhookDelivery


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ['company', 'url', 'is_active', 'event_call_started', 'event_call_completed', 'event_call_analysed', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['company__name', 'url']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['webhook_config', 'call', 'event_type', 'status', 'attempt_count', 'response_status_code', 'created_at', 'delivered_at']
    list_filter = ['status', 'event_type', 'created_at']
    search_fields = ['webhook_config__company__name', 'call__id', 'event_type']
    readonly_fields = ['created_at', 'delivered_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('webhook_config', 'call', 'event_type', 'status')
        }),
        ('Delivery Details', {
            'fields': ('attempt_count', 'max_attempts', 'next_retry_at')
        }),
        ('Response', {
            'fields': ('response_status_code', 'response_body', 'error_message')
        }),
        ('Payload', {
            'fields': ('payload',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'delivered_at')
        }),
    )
