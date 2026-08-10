from django.contrib import admin

from .models import (
    EmployeePermissionOverride,
    EmployeeRole,
    Permission,
    Role,
    RolePermission,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "module",
        "action",
        "is_active",
    )

    list_filter = (
        "module",
        "action",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = (
        "module",
        "action",
        "code",
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "is_active",
        "is_system_role",
    )

    search_fields = (
        "code",
        "name",
    )

    list_filter = (
        "is_active",
        "is_system_role",
    )

    ordering = (
        "name",
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):

    list_display = (
        "role",
        "permission",
        "is_active",
    )

    list_filter = (
        "is_active",
        "role",
        "permission",
    )

    search_fields = (
        "role__code",
        "role__name",
        "permission__code",
        "permission__name",
    )

    ordering = (
        "role",
        "permission",
    )


@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "role",
        "is_primary",
        "assigned_by",
        "assigned_at",
        "is_active",
    )

    list_filter = (
        "is_primary",
        "is_active",
        "role",
    )

    search_fields = (
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
        "role__code",
        "role__name",
    )

    ordering = (
        "employee",
        "-is_primary",
        "role",
    )


@admin.register(EmployeePermissionOverride)
class EmployeePermissionOverrideAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "permission",
        "effect",
        "granted_by",
        "is_active",
    )

    list_filter = (
        "effect",
        "is_active",
        "permission",
    )

    search_fields = (
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
        "permission__code",
        "permission__name",
    )

    ordering = (
        "employee",
        "permission",
    )