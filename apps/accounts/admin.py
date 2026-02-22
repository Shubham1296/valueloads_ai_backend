from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, Employee


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ["email", "full_name", "company", "role", "is_active"]
    list_filter = ["role", "company", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "company", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "company", "role", "password1", "password2"),
        }),
    )
