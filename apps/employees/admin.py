from django.contrib import admin

from .models import Department, Designation, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    """

    list_display = (
        "name",
        "code",
        "manager",
        "head",
        "location",
        "budget",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
        "location",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 20

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Designation model.
    """

    list_display = (
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 20


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Employee model.
    """

    list_display = (
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
        "employment_type",
        "role",
        "status",
        "reporting_to",
        "date_of_joining",
    )

    search_fields = (
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "phone_number",
    )

    list_filter = (
        "department",
        "designation",
        "employment_type",
        "role",
        "status",
        "date_of_joining",
    )

    ordering = (
        "employee_code",
    )

    readonly_fields = (
        "employee_code",
        "created_at",
        "updated_at",
    )

    date_hierarchy = "date_of_joining"

    list_per_page = 20