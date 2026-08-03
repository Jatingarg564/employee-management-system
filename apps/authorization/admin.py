from django.contrib import admin
from .models import Permission, Role

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "code",
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
        "name",
        "is_active",
        "is_system_role",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
        "is_system_role",
    )

    ordering = (
        "name",
    )