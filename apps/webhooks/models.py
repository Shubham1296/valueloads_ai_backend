import uuid
from django.db import models
from apps.accounts.models import Company
from apps.calls.models import Call


class WebhookConfig(models.Model):
    """Webhook delivery configuration per company"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="webhook_config")

    url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)

    # Event subscriptions
    event_call_started = models.BooleanField(default=True)
    event_call_completed = models.BooleanField(default=True)
    event_call_analysed = models.BooleanField(default=True)
    event_call_failed = models.BooleanField(default=True)

    # Security
    secret_key = models.CharField(max_length=255, blank=True, help_text="For HMAC signatures")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook for {self.company.name}"


class WebhookDelivery(models.Model):
    """Webhook delivery log for debugging and retries"""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_config = models.ForeignKey(WebhookConfig, on_delete=models.CASCADE, related_name="deliveries")
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name="webhook_deliveries")

    event_type = models.CharField(max_length=50, help_text="call.started, call.completed, etc.")
    payload = models.JSONField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=4)

    response_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['webhook_config', 'created_at']),
        ]
        ordering = ['-created_at']
        verbose_name_plural = "webhook deliveries"

    def __str__(self):
        return f"{self.event_type} - {self.status}"
