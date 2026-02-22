from django.contrib.auth import authenticate
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, Employee


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "email", "first_name", "last_name", "role", "company", "created_at"]
        read_only_fields = ["id", "role", "created_at"]


# ── Company + Admin registration ──────────────────────────────────────────────

class CompanyRegisterSerializer(serializers.Serializer):
    # Company fields
    company_name = serializers.CharField(max_length=255)
    # Admin employee fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_email(self, value):
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_company_name(self, value):
        slug = slugify(value)
        if Company.objects.filter(slug=slug).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def create(self, validated_data):
        slug = slugify(validated_data["company_name"])
        company = Company.objects.create(name=validated_data["company_name"], slug=slug)
        employee = Employee.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            company=company,
            role=Employee.Role.ADMIN,
            is_staff=True,
        )
        return company, employee


# ── Employee registration (under existing company) ────────────────────────────

class EmployeeRegisterSerializer(serializers.Serializer):
    company_slug = serializers.SlugField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_email(self, value):
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_company_slug(self, value):
        try:
            self._company = Company.objects.get(slug=value)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company not found.")
        return value

    def create(self, validated_data):
        employee = Employee.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            company=self._company,
            role=Employee.Role.EMPLOYEE,
        )
        return employee


# ── Login ──────────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


# ── Token response helper ──────────────────────────────────────────────────────

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
