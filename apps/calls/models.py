import uuid
from django.db import models
from apps.accounts.models import Company
from apps.agents.models import Agent
from apps.leads.models import Lead


class Call(models.Model):
    """Records of call interactions"""
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Outcome(models.TextChoices):
        ANSWERED = "answered", "Answered"
        NO_ANSWER = "no_answer", "No Answer"
        BUSY = "busy", "Busy"
        FAILED = "failed", "Failed"
        VOICEMAIL = "voicemail", "Voicemail"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="calls")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="calls")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="calls")

    # Call details
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    outcome = models.CharField(max_length=20, choices=Outcome.choices, blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)

    # AI metrics
    tokens_consumed = models.IntegerField(default=0)

    # Content
    summary = models.TextField(blank=True)
    transcript = models.TextField(blank=True)
    transcript_url = models.URLField(max_length=500, blank=True)
    recording_url = models.URLField(max_length=500, blank=True)

    # Timestamps
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['lead', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['status', 'scheduled_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Call to {self.lead.first_name} {self.lead.last_name} - {self.status}"


class AIAnalysis(models.Model):
    """AI processing results for call"""
    class Sentiment(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEUTRAL = "neutral", "Neutral"
        NEGATIVE = "negative", "Negative"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="ai_analysis")

    sentiment = models.CharField(max_length=20, choices=Sentiment.choices, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True, help_text="-1.0 to 1.0")

    key_points = models.JSONField(default=list, blank=True, help_text='["interested in product", "budget concerns"]')
    topics_discussed = models.JSONField(default=list, blank=True)
    objections_raised = models.JSONField(default=list, blank=True)

    intent_detected = models.CharField(max_length=100, blank=True, help_text="purchase_intent, information_gathering")
    confidence_score = models.FloatField(null=True, blank=True)

    next_actions = models.JSONField(default=list, blank=True, help_text='["send pricing", "schedule demo"]')
    recommendations = models.TextField(blank=True)

    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for Call {self.call.id} - {self.sentiment}"


class CallRecording(models.Model):
    """Call recording metadata and storage"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="recording")

    # Storage
    s3_bucket = models.CharField(max_length=255, blank=True)
    s3_key = models.CharField(max_length=500, blank=True)
    s3_url = models.URLField(max_length=500, help_text="Permanent S3 URL")
    signed_url = models.URLField(max_length=1000, blank=True, help_text="Temporary signed URL")
    signed_url_expires_at = models.DateTimeField(null=True, blank=True)

    # File metadata
    file_size_bytes = models.BigIntegerField(default=0)
    duration_seconds = models.IntegerField(default=0)
    format = models.CharField(max_length=20, default="mp3", help_text="mp3, wav, etc.")

    # Retention
    retain_until = models.DateTimeField(null=True, blank=True, help_text="Auto-delete after this date")
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['retain_until', 'is_deleted']),
        ]

    def __str__(self):
        return f"Recording for Call {self.call.id}"


class CallCost(models.Model):
    """Detailed cost breakdown for billing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="cost")

    # Voice costs
    voice_provider = models.CharField(max_length=50)
    voice_minutes = models.FloatField(default=0)
    voice_cost_per_minute = models.DecimalField(max_digits=10, decimal_places=4)
    voice_total_cost = models.DecimalField(max_digits=10, decimal_places=4)

    # AI/LLM costs
    ai_provider = models.CharField(max_length=50, default="openai")
    ai_tokens_consumed = models.IntegerField(default=0)
    ai_cost_per_token = models.DecimalField(max_digits=10, decimal_places=6)
    ai_total_cost = models.DecimalField(max_digits=10, decimal_places=4)

    # Phone/carrier costs
    phone_provider = models.CharField(max_length=50, blank=True)
    phone_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Total
    total_cost_usd = models.DecimalField(max_digits=10, decimal_places=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cost for Call {self.call.id}: ${self.total_cost_usd}"
