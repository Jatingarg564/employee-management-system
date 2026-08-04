from django.db.models import QuerySet

from .models import (
    EmployeePermissionOverride,
    EmployeeRole,
    Permission,
    Role,
    RolePermission,
)


# ==========================================================
# Permission Selectors
# ==========================================================

def get_permission(permission_id: int) -> Permission:
    """
    Retrieve a permission by its primary key.
    """

    return Permission.objects.get(
        pk=permission_id,
    )


def get_permission_by_code(code: str) -> Permission:
    """
    Retrieve a permission using its unique permission code.
    """

    return Permission.objects.get(
        code=code,
    )


def get_permissions() -> QuerySet[Permission]:
    """
    Retrieve all permissions.
    """

    return Permission.objects.all()


def get_active_permissions() -> QuerySet[Permission]:
    """
    Retrieve all active permissions.
    """

    return Permission.objects.active()


def get_permissions_by_module(
    module: str,
) -> QuerySet[Permission]:
    """
    Retrieve all permissions belonging to a module.
    """

    return Permission.objects.by_module(
        module,
    )


def get_permissions_by_action(
    action: str,
) -> QuerySet[Permission]:
    """
    Retrieve all permissions for a specific action.
    """

    return Permission.objects.by_action(
        action,
    )


def permission_exists(code: str) -> bool:
    """
    Determine whether a permission exists.
    """

    return Permission.objects.filter(
        code=code,
    ).exists()


# ==========================================================
# Role Selectors
# ==========================================================

def get_role(role_id: int) -> Role:
    """
    Retrieve a role by its primary key.
    """

    return Role.objects.get(
        pk=role_id,
    )


def get_role_by_code(code: str) -> Role:
    """
    Retrieve a role using its unique code.
    """

    return Role.objects.get(
        code=code,
    )


def get_roles() -> QuerySet[Role]:
    """
    Retrieve all roles.
    """

    return Role.objects.all()


def get_active_roles() -> QuerySet[Role]:
    """
    Retrieve all active roles.
    """

    return Role.objects.active()


def get_system_roles() -> QuerySet[Role]:
    """
    Retrieve all predefined system roles.
    """

    return Role.objects.system_roles()


def get_custom_roles() -> QuerySet[Role]:
    """
    Retrieve all custom roles.
    """

    return Role.objects.custom_roles()


def role_exists(code: str) -> bool:
    """
    Determine whether a role exists.
    """

    return Role.objects.filter(
        code=code,
    ).exists()


# ==========================================================
# Role Permission Selectors
# ==========================================================

def get_role_permissions(
    role: Role,
) -> QuerySet[RolePermission]:
    """
    Retrieve all permissions assigned to a role.
    """

    return (
        RolePermission.objects
        .for_role(role)
        .select_related(
            "permission",
        )
    )


def get_role_permission_codes(
    role: Role,
):
    """
    Retrieve permission codes assigned to a role.
    """

    return (
        RolePermission.objects
        .for_role(role)
        .values_list(
            "permission__code",
            flat=True,
        )
    )


# ==========================================================
# Employee Role Selectors
# ==========================================================

def get_employee_roles(
    employee,
) -> QuerySet[EmployeeRole]:
    """
    Retrieve all current role assignments for an employee.
    """

    return (
        EmployeeRole.objects
        .for_employee(employee)
        .select_related(
            "role",
        )
    )


def get_primary_role(
    employee,
):
    """
    Retrieve an employee's primary role.
    """

    assignment = (
        EmployeeRole.objects
        .primary()
        .filter(
            employee=employee,
        )
        .select_related(
            "role",
        )
        .first()
    )

    return assignment.role if assignment else None


def get_role_employees(
    role,
) -> QuerySet[EmployeeRole]:
    """
    Retrieve employees assigned to a role.
    """

    return (
        EmployeeRole.objects
        .for_role(role)
        .select_related(
            "employee",
        )
    )


# ==========================================================
# Employee Permission Override Selectors
# ==========================================================

def get_employee_permission_overrides(
    employee,
) -> QuerySet[EmployeePermissionOverride]:
    """
    Retrieve current permission overrides assigned to an employee.
    """

    return (
        EmployeePermissionOverride.objects
        .for_employee(employee)
        .select_related(
            "permission",
        )
    )
