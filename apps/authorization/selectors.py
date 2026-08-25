from django.db.models import QuerySet

from apps.employees.models import Employee

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

def get_permission(
    permission_id: int,
) -> Permission:
    """
    Retrieve a permission by its primary key.
    """

    return Permission.objects.get(
        pk=permission_id,
    )


def get_permission_by_code(
    code: str,
) -> Permission:
    """
    Retrieve a permission using its unique code.
    """

    return (
        Permission.objects
        .by_code(code)
        .get()
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
    Retrieve all permissions belonging to an action.
    """

    return Permission.objects.by_action(
        action,
    )


def permission_exists(
    code: str,
) -> bool:
    """
    Determine whether a permission exists.
    """

    return (
        Permission.objects
        .by_code(code)
        .exists()
    )


# ==========================================================
# Role Selectors
# ==========================================================

def get_role(
    role_id: int,
) -> Role:
    """
    Retrieve a role by its primary key.
    """

    return Role.objects.get(
        pk=role_id,
    )


def get_role_by_code(
    code: str,
) -> Role:
    """
    Retrieve a role using its unique code.
    """

    return (
        Role.objects
        .by_code(code)
        .get()
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


def role_exists(
    code: str,
) -> bool:
    """
    Determine whether a role exists.
    """

    return (
        Role.objects
        .by_code(code)
        .exists()
    )


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


def role_has_permission(
    role: Role,
    permission: Permission,
) -> bool:
    """
    Determine whether a role has a permission assigned.
    """

    return (
        RolePermission.objects
        .for_role(role)
        .filter(
            permission=permission,
        )
        .exists()
    )


# ==========================================================
# Employee Role Selectors
# ==========================================================

def get_employee_roles(
    employee: Employee,
) -> QuerySet[EmployeeRole]:
    """
    Retrieve all active role assignments for an employee.
    """

    return (
        EmployeeRole.objects
        .for_employee(employee)
        .select_related(
            "role",
            "assigned_by",
        )
    )


def get_primary_role_assignment(
    employee: Employee,
) -> EmployeeRole | None:
    """
    Retrieve an employee's primary role assignment.
    """

    return (
        EmployeeRole.objects
        .primary_for_employee(employee)
        .select_related(
            "role",
            "assigned_by",
        )
        .first()
    )


def employee_has_role(
    employee: Employee,
    role: Role,
) -> bool:
    """
    Determine whether an employee has a role assigned.
    """

    return (
        EmployeeRole.objects
        .for_employee(employee)
        .filter(
            role=role,
        )
        .exists()
    )


def get_role_employees(
    role: Role,
) -> QuerySet[EmployeeRole]:
    """
    Retrieve all employees assigned to a role.
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
    employee: Employee,
) -> QuerySet[EmployeePermissionOverride]:
    """
    Retrieve all permission overrides assigned to an employee.
    """

    return (
        EmployeePermissionOverride.objects
        .for_employee(employee)
        .select_related(
            "permission",
            "granted_by",
        )
    )


def employee_has_permission_override(
    employee: Employee,
    permission: Permission,
) -> bool:
    """
    Determine whether an employee has a permission override.
    """

    return (
        EmployeePermissionOverride.objects
        .for_employee(employee)
        .filter(
            permission=permission,
        )
        .exists()
    )