from django.db import models

from apps.core.models import TimeStampedActiveModel, TimeStampedModel

from .choices import (
    PermissionAction,
    PermissionEffect,
    PermissionModule,
)

from .managers import (
    EmployeePermissionOverrideManager,
    EmployeeRoleManager,
    PermissionManager,
    RoleManager,
    RolePermissionManager,
)

class Permission(TimeStampedActiveModel):
    """
    Represents a single atomic permission that can be assigned
    to authorization roles.
    """

    objects = PermissionManager()

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique permission identifier (e.g. employee.view).",
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Human-readable permission name.",
    )

    module = models.CharField(
        max_length=50,
        choices=PermissionModule.choices,
        db_index=True,
        help_text="Business module to which the permission belongs.",
    )

    action = models.CharField(
        max_length=50,
        choices=PermissionAction.choices,
        help_text="Action allowed within the selected module.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the permission.",
    )

    class Meta:

        ordering = (
            "module",
            "action",
            "name",
        )

        verbose_name = "Permission"

        verbose_name_plural = "Permissions"

    def __str__(self):
        return self.code

class Role(TimeStampedActiveModel):
    """
    Represents a collection of permissions that can be assigned
    to employees.
    """

    objects = RoleManager()

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=(
            "Unique role identifier "
            "(e.g. SUPER_ADMIN, HR, MANAGER)."
        ),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable role name.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the role.",
    )

    is_system_role = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Indicates whether this role is a "
            "predefined system role."
        ),
    )

    class Meta:

        ordering = (
            "name",
        )

        verbose_name = "Role"

        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name
 
class RolePermission(TimeStampedActiveModel):
    """
    Maps permissions to roles.

    Every record represents a single permission assigned
    to a specific role.
    """

    objects = RolePermissionManager()

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        help_text="Role receiving the permission.",
    )

    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        help_text="Permission assigned to the role.",
    )

    class Meta:

        ordering = (
            "role",
            "permission",
        )

        verbose_name = "Role Permission"

        verbose_name_plural = "Role Permissions"

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "role",
                    "permission",
                ),
                name="unique_role_permission",
            ),
        ]

        indexes = [
            models.Index(
                fields=(
                    "role",
                    "is_active",
                ),
                name="idx_role_permission_role_active",
            ),
            models.Index(
                fields=(
                    "permission",
                    "is_active",
                ),
                name="idx_role_permission_permission_active",
            ),
        ]

    def __str__(self):
        return (
            f"{self.role.code} → "
            f"{self.permission.code}"
        )

class EmployeeRole(TimeStampedActiveModel):
    """
    Assigns authorization roles to employees.

    An employee may have multiple roles, but only one
    active primary role.
    """

    objects = EmployeeRoleManager()

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="employee_roles",
        help_text="Employee receiving the role.",
    )

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="employee_roles",
        help_text="Role assigned to the employee.",
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates whether this is the employee's primary role.",
    )

    assigned_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
        help_text="Employee who assigned the role.",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Assigned At",
        help_text="Date and time when the role was assigned.",
    )

    remarks = models.TextField(
        blank=True,
        help_text="Optional remarks regarding the role assignment.",
    )

    class Meta:

        ordering = (
            "employee",
            "-is_primary",
            "role",
        )

        verbose_name = "Employee Role"

        verbose_name_plural = "Employee Roles"

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "employee",
                    "role",
                ),
                name="unique_employee_role",
            ),
            models.UniqueConstraint(
                fields=(
                    "employee",
                ),
                condition=models.Q(
                    is_primary=True,
                ),
                name="unique_primary_role_per_employee",
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} → "
            f"{self.role.code}"
        )
    
class EmployeePermissionOverride(TimeStampedActiveModel):
    """
    Overrides role-based permissions for a specific employee.

    Overrides are applied after role permissions when
    resolving an employee's effective permissions.
    """

    objects = EmployeePermissionOverrideManager()

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="permission_overrides",
        help_text="Employee receiving the permission override.",
    )

    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="employee_overrides",
        help_text="Permission being overridden.",
    )

    effect = models.CharField(
        max_length=10,
        choices=PermissionEffect.choices,
        help_text="Determines whether the permission is explicitly allowed or denied.",
    )

    granted_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permission_overrides",
        help_text="Employee who granted the permission override.",
    )

    reason = models.TextField(
        blank=True,
        help_text="Business reason for creating the permission override.",
    )

    class Meta:

        ordering = (
            "employee",
            "permission",
        )

        verbose_name = "Employee Permission Override"

        verbose_name_plural = "Employee Permission Overrides"

        constraints = [

            models.UniqueConstraint(
                fields=(
                    "employee",
                    "permission",
                ),
                name="unique_employee_permission_override",
            ),

        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} → "
            f"{self.permission.code} ({self.effect})"
        )
    