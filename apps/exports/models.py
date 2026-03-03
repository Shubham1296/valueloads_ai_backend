import uuid
from django.db import models
from apps.accounts.models import Company, Employee


class DataExport(models.Model):
    """Track large export jobs"""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class ExportType(models.TextChoices):
        LEADS_CSV = "leads_csv", "Leads CSV"
        CALLS_CSV = "calls_csv", "Calls CSV"
        TRANSCRIPTS_ZIP = "transcripts_zip", "Transcripts ZIP"
        ANALYTICS_EXCEL = "analytics_excel", "Analytics Excel"
        FULL_BACKUP = "full_backup", "Full Data Backup"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="data_exports")
    requested_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="data_exports_requested")

    export_type = models.CharField(max_length=50, choices=ExportType.choices)
    filters = models.JSONField(help_text='{"campaign_id": "...", "date_range": [...]}')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    file_url = models.URLField(max_length=500, blank=True, help_text="S3 signed URL")
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)

    expires_at = models.DateTimeField(help_text="Download link expires after 24hrs")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.export_type} - {self.status}"
