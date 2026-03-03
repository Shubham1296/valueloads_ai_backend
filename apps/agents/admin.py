from django.contrib import admin
from .models import VoiceConfiguration, Agent, AgentVersion


@admin.register(VoiceConfiguration)
class VoiceConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'company', 'language_code', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active', 'language_code']
    search_fields = ['name', 'company__name']
    readonly_fields = ['created_at']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'campaign', 'status', 'total_calls', 'successful_calls', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'company__name', 'campaign__campaign_name']
    readonly_fields = ['total_calls', 'successful_calls', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'company', 'campaign', 'status')
        }),
        ('Conversation', {
            'fields': ('prompt', 'welcome_message', 'fallback_message', 'goodbye_message')
        }),
        ('Voice', {
            'fields': ('voice_config', 'voice_id')
        }),
        ('Behavior', {
            'fields': ('max_attempts', 'retry_delay_minutes', 'max_call_duration_minutes', 'interrupt_threshold')
        }),
        ('AI Settings', {
            'fields': ('model_name', 'temperature', 'max_tokens')
        }),
        ('Performance', {
            'fields': ('total_calls', 'successful_calls', 'avg_rating')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at', 'deleted_at')
        }),
    )


@admin.register(AgentVersion)
class AgentVersionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'version_number', 'is_active', 'calls_with_this_version', 'success_rate', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['agent__name']
    readonly_fields = ['created_at']
