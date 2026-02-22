import uuid
from django.db import models
from apps.accounts.models import Employee


class Campaign(models.Model):

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

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    sale_cycle = models.CharField(max_length=50, choices=SaleCycle.choices)
    call_type = models.CharField(max_length=20, choices=CallType.choices)
    phone_no = models.CharField(max_length=20)
    call_flow_url = models.URLField(max_length=500)
    test_call_url = models.URLField(max_length=500, blank=True)
    agent_id = models.CharField(max_length=255)
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

    def __str__(self):
        return self.campaign_name
