import uuid
from django.db import models
from apps.accounts.models import Company, Employee
from apps.agents.models import Agent
from apps.campaigns.models import Campaign


class Lead(models.Model):
    """Contact to be called by an agent"""
    class Status(models.TextChoices):
        NEW = "new", "New"
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        STOPPED = "stopped", "Stopped"

    class Disposition(models.TextChoices):
        NOT_INTERESTED = "not_interested", "Not Interested"
        HUNG_UP = "hung_up", "Hung Up"
        COMPLETED = "completed", "Completed"
        NO_ANSWER = "no_answer", "No Answer"
        CALLBACK_REQUESTED = "callback_requested", "Callback Requested"
        VOICEMAIL = "voicemail", "Voicemail Left"
        WRONG_NUMBER = "wrong_number", "Wrong Number"
        DNC = "dnc", "Do Not Call"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="leads")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="leads")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="leads")

    # Contact information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone_e164 = models.CharField(max_length=20, help_text="E.164 format: +14155552671")

    # Address (optional)
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, blank=True, help_text="ISO 2-letter code")
    postal_code = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, blank=True, default="America/New_York")

    # Status tracking
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    disposition = models.CharField(max_length=50, choices=Disposition.choices, null=True, blank=True)

    # Call tracking
    attempts_count = models.IntegerField(default=0)
    successful_contact_count = models.IntegerField(default=0, help_text="Times actually spoke")

    # Phone verification
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, blank=True, help_text="company_verified, twilio_lookup")
    phone_carrier = models.CharField(max_length=100, blank=True)
    phone_type = models.CharField(max_length=20, blank=True, help_text="mobile, landline, voip")

    # Scheduling
    schedule_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_called_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    do_not_call_before = models.TimeField(null=True, blank=True, help_text="e.g., 09:00")
    do_not_call_after = models.TimeField(null=True, blank=True, help_text="e.g., 20:00")

    # Locking (prevent concurrent calls)
    currently_in_call = models.BooleanField(default=False)
    call_lock_acquired_at = models.DateTimeField(null=True, blank=True)

    # Flexible metadata
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"company": "Acme Corp", "title": "VP Sales", "linkedin": "https://..."}'
    )

    # Tags for segmentation
    tags = models.JSONField(default=list, blank=True, help_text='["high-value", "warm-lead"]')

    # Lead score (can be calculated)
    lead_score = models.IntegerField(null=True, blank=True, help_text="0-100 score")

    # Source attribution
    source = models.CharField(max_length=100, blank=True, help_text="csv_upload, api, crm_sync")
    import_batch = models.ForeignKey(
        'LeadImportBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads"
    )

    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads_deleted"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads_created"
    )

    class Meta:
        indexes = [
            models.Index(fields=['company', 'status', 'created_at']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['phone_e164', 'company']),
            models.Index(fields=['schedule_at']),
            models.Index(fields=['currently_in_call']),
            # Composite for scheduler query
            models.Index(fields=['status', 'schedule_at'], name='leads_lead_scheduler_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_e164}"


class LeadImportBatch(models.Model):
    """Track bulk CSV imports"""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partial Success"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="lead_import_batches")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="lead_import_batches")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="lead_import_batches")

    filename = models.CharField(max_length=500)
    file_url = models.URLField(max_length=500, help_text="S3 location")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_rows = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)

    error_log = models.JSONField(default=list, blank=True, help_text='[{"row": 5, "error": "Invalid phone"}]')

    imported_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="lead_imports")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.filename} ({self.status})"


class LeadNote(models.Model):
    """Manual notes on leads"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")

    note = models.TextField()
    is_pinned = models.BooleanField(default=False)

    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="lead_notes_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"Note on {self.lead.first_name} {self.lead.last_name}"
