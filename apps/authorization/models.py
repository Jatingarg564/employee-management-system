from django.db import models

from apps.core.models import TimeStampedActiveModel

from .choices import (
    PermissionAction,
    PermissionModule,
    PermissionEffect,
)


class Permission(TimeStampedActiveModel):
    """
    Represents a single atomic permission that can be assigned to system roles.
    """

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique permission identifier.",
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable permission name.",
    )

    module = models.CharField(
        max_length=50,
        choices=PermissionModule.choices,
        db_index=True,
    )

    action = models.CharField(
        max_length=50,
        choices=PermissionAction.choices,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "module",
            "action",
            "name",
        ]

        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def __str__(self):
        return self.code


class Role(TimeStampedActiveModel):
    """
    Represents a collection of permissions that can be assigned to employees.
    """

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique role identifier.",
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable role name.",
    )

    description = models.TextField(
        blank=True,
    )

    is_system_role = models.BooleanField(
        default=False,
        help_text="Indicates whether this role is protected from modification or deletion.",
    )

    class Meta:
        ordering = [
            "name",
        ]

        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name

class RolePermission(TimeStampedActiveModel):
    """
    Maps permissions to roles and defines the default permissions
    inherited by every employee assigned to that role.
    """

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="permission_roles",
    )

    class Meta:
        ordering = [
            "role",
            "permission",
        ]

        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "role",
                    "permission",
                ],
                name="unique_role_permission",
            ),
        ]

    def __str__(self):
        return f"{self.role.code} → {self.permission.code}"

class EmployeeRole(TimeStampedActiveModel):
    """
    Assigns roles to employees.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="employee_roles",
    )

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="employee_roles",
    )

    is_primary = models.BooleanField(
        default=False,
    )

    assigned_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "employee",
            "-is_primary",
        ]

        verbose_name = "Employee Role"
        verbose_name_plural = "Employee Roles"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "role",
                ],
                name="unique_employee_role",
            ),
        ]

    def __str__(self):
        return f"{self.employee} → {self.role}"

class EmployeePermissionOverride(TimeStampedActiveModel):
    """
    Overrides permissions granted through roles for a specific employee.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="permission_overrides",
    )

    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="employee_overrides",
    )

    effect = models.CharField(
        max_length=10,
        choices=PermissionEffect.choices,
    )

    granted_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permission_overrides",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    remarks = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "employee",
            "permission",
        ]

        verbose_name = "Employee Permission Override"
        verbose_name_plural = "Employee Permission Overrides"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "permission",
                ],
                name="unique_employee_permission_override",
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee} → "
            f"{self.permission} ({self.effect})"
        )