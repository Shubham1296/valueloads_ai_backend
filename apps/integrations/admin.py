from django.contrib import admin
from .models import Integration, IntegrationLog


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'integration_type', 'is_active', 'last_sync_at', 'last_sync_status', 'created_at']
    list_filter = ['integration_type', 'is_active', 'created_at']
    search_fields = ['name', 'company__name']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'action', 'success', 'records_processed', 'records_succeeded', 'records_failed', 'created_at']
    list_filter = ['action', 'success', 'created_at']
    search_fields = ['integration__name', 'error_message']
    readonly_fields = ['created_at']
