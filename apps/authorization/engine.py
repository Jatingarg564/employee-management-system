from typing import FrozenSet, Iterable

from apps.employees.models import Employee

from .choices import PermissionEffect
from .constants import (
    SUPER_ADMIN_ROLE_CODE,
    SYSTEM_ADMIN_ROLE_CODE,
)
from .selectors import (
    get_employee_permission_overrides,
    get_employee_roles,
    get_primary_role,
    get_role_permission_codes,
)


# ==========================================================
# Internal Helpers
# ==========================================================

def _resolve_role_permissions(
    employee: Employee,
) -> set[str]:
    """
    Resolve permission codes inherited from every role assigned
    to the employee.
    """

    permission_codes = set()

    for assignment in get_employee_roles(employee):

        permission_codes.update(
            get_role_permission_codes(
                assignment.role,
            )
        )

    return permission_codes


def _resolve_permission_overrides(
    employee: Employee,
) -> tuple[set[str], set[str]]:
    """
    Resolve employee specific permission overrides.

    Returns:
        (
            allowed_permissions,
            denied_permissions,
        )
    """

    allowed_permissions = set()

    denied_permissions = set()

    overrides = get_employee_permission_overrides(
        employee,
    )

    for override in overrides:

        permission_code = override.permission.code

        if override.effect == PermissionEffect.ALLOW:

            allowed_permissions.add(
                permission_code,
            )

        else:

            denied_permissions.add(
                permission_code,
            )

    return (
        allowed_permissions,
        denied_permissions,
    )


def _get_permission_set(
    employee: Employee,
) -> FrozenSet[str]:
    """
    Central permission resolver.

    This helper exists to allow Redis caching in the future
    without changing the public engine API.
    """

    return get_effective_permission_codes(
        employee,
    )


# ==========================================================
# Permission Resolution
# ==========================================================

def get_effective_permission_codes(
    employee: Employee,
) -> FrozenSet[str]:
    """
    Resolve the final permission set available to an employee.
    """

    permissions = _resolve_role_permissions(
        employee,
    )

    allowed_permissions, denied_permissions = (
        _resolve_permission_overrides(
            employee,
        )
    )

    permissions.difference_update(
        denied_permissions,
    )

    permissions.update(
        allowed_permissions,
    )

    return frozenset(
        permissions,
    )


# ==========================================================
# Permission Checks
# ==========================================================

def has_permission(
    employee: Employee,
    permission_code: str,
) -> bool:
    """
    Determine whether an employee has a specific permission.
    """

    if is_super_admin(employee):

        return True

    return (
        permission_code
        in _get_permission_set(employee)
    )


def has_any_permission(
    employee: Employee,
    permission_codes: Iterable[str],
) -> bool:
    """
    Determine whether an employee has at least one permission.
    """

    if is_super_admin(employee):

        return True

    permissions = _get_permission_set(
        employee,
    )

    return any(
        permission in permissions
        for permission in permission_codes
    )


def has_all_permissions(
    employee: Employee,
    permission_codes: Iterable[str],
) -> bool:
    """
    Determine whether an employee has every supplied permission.
    """

    if is_super_admin(employee):

        return True

    permissions = _get_permission_set(
        employee,
    )

    return all(
        permission in permissions
        for permission in permission_codes
    )


# ==========================================================
# Role Checks
# ==========================================================

def has_role(
    employee: Employee,
    role_code: str,
) -> bool:
    """
    Determine whether an employee is assigned a specific role.
    """

    return any(
        assignment.role.code == role_code
        for assignment in get_employee_roles(
            employee,
        )
    )


def has_any_role(
    employee: Employee,
    role_codes: Iterable[str],
) -> bool:
    """
    Determine whether an employee has at least one role.
    """

    employee_roles = {
        assignment.role.code
        for assignment in get_employee_roles(
            employee,
        )
    }

    return any(
        role in employee_roles
        for role in role_codes
    )


def has_all_roles(
    employee: Employee,
    role_codes: Iterable[str],
) -> bool:
    """
    Determine whether an employee has every supplied role.
    """

    employee_roles = {
        assignment.role.code
        for assignment in get_employee_roles(
            employee,
        )
    }

    return all(
        role in employee_roles
        for role in role_codes
    )


# ==========================================================
# Administrative Checks
# ==========================================================

def is_super_admin(
    employee: Employee,
) -> bool:
    """
    Determine whether the employee is assigned the Super Administrator role.
    """

    primary_role = get_primary_role(
        employee,
    )

    return (
        primary_role is not None
        and primary_role.code == SUPER_ADMIN_ROLE_CODE
    )


def is_system_admin(
    employee: Employee,
) -> bool:
    """
    Determine whether the employee is assigned the System Administrator role.
    """

    primary_role = get_primary_role(
        employee,
    )

    return (
        primary_role is not None
        and primary_role.code == SYSTEM_ADMIN_ROLE_CODE
    )


# ==========================================================
# Module Checks
# ==========================================================

def can_access_module(
    employee: Employee,
    module: str,
) -> bool:
    """
    Determine whether an employee has access to a module.
    """

    if is_super_admin(employee):

        return True

    permissions = _get_permission_set(
        employee,
    )

    return any(
        permission.startswith(
            f"{module}."
        )
        for permission in permissions
    )


def can_perform_action(
    employee: Employee,
    module: str,
    action: str,
) -> bool:
    """
    Determine whether an employee can perform an action within a module.
    """

    return has_permission(
        employee,
        f"{module}.{action}",
    )