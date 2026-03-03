import uuid
from django.db import models
from apps.accounts.models import Company, Employee
from apps.campaigns.models import Campaign


class VoiceConfiguration(models.Model):
    """Reusable voice settings for agents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="voice_configs")

    name = models.CharField(max_length=255, help_text="e.g., 'Professional Male', 'Friendly Female'")
    provider = models.CharField(max_length=50, help_text="elevenlabs, google, azure")
    voice_id = models.CharField(max_length=255, help_text="Provider's voice ID")

    # Voice parameters
    language_code = models.CharField(max_length=10, default="en-US")
    speed = models.FloatField(default=1.0, help_text="0.5 to 2.0")
    pitch = models.FloatField(default=1.0, help_text="0.5 to 2.0")
    stability = models.FloatField(default=0.5, help_text="ElevenLabs specific")
    similarity_boost = models.FloatField(default=0.75, help_text="ElevenLabs specific")

    # Sample
    sample_audio_url = models.URLField(max_length=500, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.provider})"


class Agent(models.Model):
    """AI voice agent configuration"""
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        TESTING = "testing", "Testing"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="agents")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="agents")

    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Conversation configuration
    prompt = models.TextField(help_text="System prompt / instructions for the AI")
    welcome_message = models.TextField(help_text="First thing agent says")
    fallback_message = models.TextField(blank=True, help_text="When agent doesn't understand")
    goodbye_message = models.TextField(blank=True)

    # Voice
    voice_config = models.ForeignKey(
        VoiceConfiguration,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="agents"
    )
    # Legacy support:
    voice_id = models.UUIDField(null=True, blank=True)

    # Behavior settings
    max_attempts = models.IntegerField(default=3, help_text="Max call attempts per lead")
    retry_delay_minutes = models.IntegerField(default=60)
    max_call_duration_minutes = models.IntegerField(default=15)
    interrupt_threshold = models.FloatField(default=0.5, help_text="How easily user can interrupt (0-1)")

    # Advanced AI settings
    model_name = models.CharField(max_length=100, default="gpt-4-turbo")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=150)

    # Knowledge base
    knowledge_base_text = models.TextField(blank=True, help_text="Additional context for agent")
    knowledge_base_urls = models.JSONField(default=list, blank=True, help_text='["https://..."]')

    # Transfer settings
    enable_human_handoff = models.BooleanField(default=False)
    handoff_phone_number = models.CharField(max_length=20, blank=True)
    handoff_triggers = models.JSONField(default=list, blank=True, help_text='["angry", "request manager"]')

    # Performance tracking
    total_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    avg_rating = models.FloatField(null=True, blank=True)

    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="agents_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['campaign', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.campaign.campaign_name})"


class AgentVersion(models.Model):
    """Snapshot of agent configuration for A/B testing and rollback"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="versions")

    version_number = models.IntegerField()
    configuration_snapshot = models.JSONField(help_text="Full agent config at this version")

    # Performance of this version
    calls_with_this_version = models.IntegerField(default=0)
    avg_sentiment = models.FloatField(null=True, blank=True)
    success_rate = models.FloatField(null=True, blank=True)

    is_active = models.BooleanField(default=False, help_text="Currently deployed version")

    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="agent_versions_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['agent', 'version_number']]
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.agent.name} v{self.version_number}"
