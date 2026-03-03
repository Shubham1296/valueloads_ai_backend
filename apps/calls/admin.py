from django.contrib import admin
from .models import Call, AIAnalysis, CallRecording, CallCost


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead', 'agent', 'company', 'status', 'outcome', 'duration_seconds', 'tokens_consumed', 'created_at']
    list_filter = ['status', 'outcome', 'created_at']
    search_fields = ['lead__first_name', 'lead__last_name', 'agent__name', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Relationships', {
            'fields': ('lead', 'agent', 'company')
        }),
        ('Call Details', {
            'fields': ('status', 'outcome', 'duration_seconds', 'tokens_consumed')
        }),
        ('Content', {
            'fields': ('summary', 'transcript', 'transcript_url', 'recording_url')
        }),
        ('Timestamps', {
            'fields': ('scheduled_at', 'started_at', 'ended_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['call', 'sentiment', 'sentiment_score', 'intent_detected', 'confidence_score', 'processed_at']
    list_filter = ['sentiment', 'processed_at']
    search_fields = ['call__id', 'intent_detected']
    readonly_fields = ['processed_at']


@admin.register(CallRecording)
class CallRecordingAdmin(admin.ModelAdmin):
    list_display = ['call', 's3_url', 'duration_seconds', 'file_size_bytes', 'format', 'is_deleted', 'created_at']
    list_filter = ['format', 'is_deleted', 'created_at']
    search_fields = ['call__id', 's3_key']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CallCost)
class CallCostAdmin(admin.ModelAdmin):
    list_display = ['call', 'voice_provider', 'voice_total_cost', 'ai_provider', 'ai_total_cost', 'total_cost_usd', 'created_at']
    list_filter = ['voice_provider', 'ai_provider', 'created_at']
    search_fields = ['call__id']
    readonly_fields = ['created_at']
