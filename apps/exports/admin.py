from django.contrib import admin
from .models import DataExport


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['export_type', 'company', 'requested_by', 'status', 'row_count', 'file_size_bytes', 'created_at', 'completed_at']
    list_filter = ['export_type', 'status', 'created_at']
    search_fields = ['company__name', 'requested_by__email']
    readonly_fields = ['created_at', 'completed_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('company', 'requested_by', 'export_type', 'status')
        }),
        ('Filters', {
            'fields': ('filters',)
        }),
        ('Results', {
            'fields': ('file_url', 'file_size_bytes', 'row_count', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
