import uuid
from django.db import models
from apps.accounts.models import Company


class Integration(models.Model):
    """Third-party integrations (CRM, etc.)"""
    class IntegrationType(models.TextChoices):
        SALESFORCE = "salesforce", "Salesforce"
        HUBSPOT = "hubspot", "HubSpot"
        PIPEDRIVE = "pipedrive", "Pipedrive"
        ZOHO = "zoho", "Zoho CRM"
        SLACK = "slack", "Slack"
        ZAPIER = "zapier", "Zapier"
        CUSTOM_WEBHOOK = "custom_webhook", "Custom Webhook"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="integrations")

    integration_type = models.CharField(max_length=50, choices=IntegrationType.choices)
    name = models.CharField(max_length=255, help_text="Display name for this integration")

    # Configuration
    credentials = models.JSONField(help_text="Encrypted API keys, tokens, etc.")
    settings = models.JSONField(default=dict, blank=True, help_text="Integration-specific settings")

    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.integration_type})"


class IntegrationLog(models.Model):
    """Log of integration sync activities"""
    class Action(models.TextChoices):
        SYNC_LEADS = "sync_leads", "Sync Leads"
        PUSH_CALL_DATA = "push_call_data", "Push Call Data"
        PULL_CONTACTS = "pull_contacts", "Pull Contacts"
        UPDATE_DEAL = "update_deal", "Update Deal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name="logs")

    action = models.CharField(max_length=50, choices=Action.choices)
    success = models.BooleanField(default=False)

    records_processed = models.IntegerField(default=0)
    records_succeeded = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)

    error_message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['integration', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {'Success' if self.success else 'Failed'}"
