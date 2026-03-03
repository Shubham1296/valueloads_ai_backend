import uuid
from django.db import models
from apps.accounts.models import Company, Employee


class Campaign(models.Model):
    """Campaign groups agents and tracks overall performance"""

    class CallType(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    class SaleCycle(models.TextChoices):
        PROSPECTING = "prospecting", "Prospecting"
        QUALIFICATION = "qualification", "Qualification"
        PROPOSAL = "proposal", "Proposal"
        NEGOTIATION = "negotiation", "Negotiation"
        CLOSED_WON = "closed_won", "Closed Won"
        CLOSED_LOST = "closed_lost", "Closed Lost"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="campaigns", null=True, blank=True)

    # Basic info
    campaign_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Campaign settings
    is_active = models.BooleanField(default=True)
    sale_cycle = models.CharField(max_length=50, choices=SaleCycle.choices)
    call_type = models.CharField(max_length=20, choices=CallType.choices)

    # Contact settings
    phone_no = models.CharField(max_length=20, help_text="Caller ID number")

    # Flow configuration
    call_flow_url = models.URLField(max_length=500, blank=True)
    test_call_url = models.URLField(max_length=500, blank=True)

    # Default agent (legacy field, now has many agents via ForeignKey)
    agent_id = models.CharField(max_length=255, blank=True, help_text="External agent reference")

    # Voice settings
    voice_provider = models.CharField(max_length=50, default="elevenlabs")
    default_voice_id = models.UUIDField(null=True, blank=True)

    # Budget & scheduling
    total_budget_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    spent_to_date_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Calling hours (JSON: {"mon": ["09:00", "17:00"], "tue": ["09:00", "17:00"], ...})
    allowed_calling_hours = models.JSONField(default=dict, blank=True)

    # Webhooks
    webhook_url = models.URLField(max_length=500, blank=True)

    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns_deleted"
    )

    # Audit
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="campaigns_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns_updated",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['company', 'status', 'created_at']),
            models.Index(fields=['is_active', 'deleted_at']),
        ]

    def __str__(self):
        return self.campaign_name


class CampaignDailyStats(models.Model):
    """Pre-aggregated daily statistics for fast dashboard performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="campaign_daily_stats")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="daily_stats")
    date = models.DateField()

    # Lead metrics
    leads_created = models.IntegerField(default=0)
    leads_contacted = models.IntegerField(default=0)
    leads_completed = models.IntegerField(default=0)

    # Call metrics
    calls_total = models.IntegerField(default=0)
    calls_answered = models.IntegerField(default=0)
    calls_no_answer = models.IntegerField(default=0)
    calls_failed = models.IntegerField(default=0)
    calls_voicemail = models.IntegerField(default=0)

    # Duration
    total_call_duration_seconds = models.IntegerField(default=0)
    avg_call_duration_seconds = models.FloatField(default=0)
    max_call_duration_seconds = models.IntegerField(default=0)

    # Cost
    total_tokens_consumed = models.IntegerField(default=0)
    total_voice_minutes = models.FloatField(default=0)
    total_cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Rates
    answer_rate = models.FloatField(default=0, help_text="calls_answered / calls_total")
    success_rate = models.FloatField(default=0, help_text="disposition=completed / calls_total")

    # Sentiment
    avg_sentiment_score = models.FloatField(null=True, blank=True)
    positive_sentiment_count = models.IntegerField(default=0)
    negative_sentiment_count = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['campaign', 'date']]
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['campaign', 'date']),
        ]
        verbose_name_plural = "campaign daily stats"

    def __str__(self):
        return f"{self.campaign.campaign_name} - {self.date}"
