from django.contrib import admin
from .models import Lead, LeadImportBatch, LeadNote


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_e164', 'company', 'agent', 'status', 'disposition', 'attempts_count', 'created_at']
    list_filter = ['status', 'disposition', 'is_verified', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone_e164', 'email', 'company__name']
    readonly_fields = ['created_at', 'updated_at', 'call_lock_acquired_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('company', 'agent', 'campaign', 'first_name', 'last_name', 'email', 'phone_e164')
        }),
        ('Address', {
            'fields': ('address_line1', 'city', 'state', 'country', 'postal_code', 'timezone'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'disposition', 'attempts_count', 'successful_contact_count')
        }),
        ('Phone Verification', {
            'fields': ('is_verified', 'verification_method', 'phone_carrier', 'phone_type')
        }),
        ('Scheduling', {
            'fields': ('schedule_at', 'last_called_at', 'next_retry_at', 'do_not_call_before', 'do_not_call_after')
        }),
        ('Metadata', {
            'fields': ('custom_fields', 'tags', 'lead_score', 'source', 'import_batch')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at', 'deleted_by', 'deleted_at')
        }),
    )


@admin.register(LeadImportBatch)
class LeadImportBatchAdmin(admin.ModelAdmin):
    list_display = ['filename', 'company', 'campaign', 'status', 'total_rows', 'successful_imports', 'failed_imports', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['filename', 'company__name', 'campaign__campaign_name']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ['lead', 'note_preview', 'is_pinned', 'created_by', 'created_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['lead__first_name', 'lead__last_name', 'note']
    readonly_fields = ['created_at', 'updated_at']

    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'
