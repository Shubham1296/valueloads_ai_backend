import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Company(models.Model):
    """Multi-tenant company/organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    # Subscription & limits
    plan_tier = models.CharField(max_length=50, default="free", help_text="free, starter, pro, enterprise")
    call_credits_remaining = models.IntegerField(default=100)
    max_concurrent_calls = models.IntegerField(default=5)
    max_agents = models.IntegerField(default=3)

    # Settings
    timezone = models.CharField(max_length=50, default="UTC")
    default_voice_provider = models.CharField(max_length=50, default="elevenlabs")

    # Status
    is_active = models.BooleanField(default=True)
    suspended_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "companies"
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        return self.name


class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Employee.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class Employee(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EmployeeManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} ({self.company})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class APIKey(models.Model):
    """API authentication keys for company access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="api_keys")

    # Key security (store hash, not plaintext)
    key_hash = models.CharField(max_length=255, unique=True, help_text="SHA256 hash of API key")
    key_prefix = models.CharField(max_length=12, help_text="Display prefix like 'sk_live_XyZ'")

    # Metadata
    name = models.CharField(max_length=255, help_text="e.g., 'Production Key', 'Test Key'")
    scopes = models.JSONField(default=list, blank=True, help_text="['leads:write', 'calls:read']")

    # Status & usage
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    request_count = models.BigIntegerField(default=0)

    # Audit
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="api_keys_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['key_hash']),
            models.Index(fields=['company', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"


class AuditLog(models.Model):
    """Audit trail for compliance and security"""
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        VIEW = "view", "View"
        EXPORT = "export", "Export"

    class Resource(models.TextChoices):
        LEAD = "lead", "Lead"
        AGENT = "agent", "Agent"
        CALL = "call", "Call"
        CAMPAIGN = "campaign", "Campaign"
        API_KEY = "api_key", "API Key"
        COMPANY_SETTINGS = "settings", "Company Settings"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="audit_logs")

    # Actor
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)

    # Action details
    action = models.CharField(max_length=20, choices=Action.choices)
    resource_type = models.CharField(max_length=50, choices=Resource.choices)
    resource_id = models.UUIDField()

    # Change tracking
    changes = models.JSONField(null=True, blank=True, help_text='{"field": ["old", "new"]}')
    metadata = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['employee', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} {self.resource_type} at {self.timestamp}"
