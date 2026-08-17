from collections.abc import Iterable
from apps.employees.models import Employee
from django.core.exceptions import ValidationError

from apps.authorization.choices import PermissionEffect
from apps.authorization.engine import (
    can_access_module,
    can_perform_action,
    has_all_permissions,
    has_any_permission, 
    has_permission,
    is_super_admin,
    is_system_admin,
)

from .constants import (
    PERMISSION_CODE_FORMAT,
    PROTECTED_ROLES,
    RESERVED_PERMISSION_PREFIXES,
    SYSTEM_ROLE_CONFIGURATION,
)
from .models import (
    EmployeePermissionOverride,
    EmployeeRole,
    Permission,
    Role,
    RolePermission,
)


# ==========================================================
# Helper Functions
# ==========================================================

def get_system_role_configuration(
    role_code: str,
) -> dict[str, object]:
    """
    Return the configuration associated with a system role.
    """

    return SYSTEM_ROLE_CONFIGURATION.get(
        role_code,
        {},
    )


def get_required_permissions(
    role_code: str,
) -> set[str]:
    """
    Retrieve the required permissions for a system role.
    """

    configuration = get_system_role_configuration(
        role_code,
    )

    return configuration.get(
        "required_permissions",
        set[str](),
    )


def is_protected_role(
    role_code: str,
) -> bool:
    """
    Determine whether a role is protected.
    """

    configuration = get_system_role_configuration(
        role_code,
    )

    return configuration.get(
        "is_protected",
        False,
    )

# ==========================================================
# Permission Validators
# ==========================================================

def validate_permission_code(
    code: str,
    permission: Permission | None = None,
) -> None:
    """
    Validate that the permission code is unique.
    """

    queryset = Permission.objects.filter(
        code=code,
    )

    if permission is not None:

        queryset = queryset.exclude(
            pk=permission.pk,
        )

    if queryset.exists():

        raise ValidationError(
            "A permission with this code already exists.",
        )


def validate_permission_name(
    name: str,
    permission: Permission | None = None,
) -> None:
    """
    Validate that the permission name is unique.
    """

    queryset = Permission.objects.filter(
        name=name,
    )

    if permission is not None:

        queryset = queryset.exclude(
            pk=permission.pk,
        )

    if queryset.exists():

        raise ValidationError(
            "A permission with this name already exists.",
        )


def validate_permission_code_structure(
    code: str,
    module: str,
    action: str,
) -> None:
    """
    Validate that the permission code follows the
    '<module>.<action>' naming convention.
    """

    expected_code = PERMISSION_CODE_FORMAT.format(
        module=module,
        action=action,
    )

    if code != expected_code:

        raise ValidationError(
            f"Permission code must be '{expected_code}'.",
        )


def validate_reserved_permission_code(
    code: str,
) -> None:
    """
    Validate that reserved permission namespaces
    cannot be used by custom permissions.
    """

    for prefix in RESERVED_PERMISSION_PREFIXES:

        if code.startswith(
            prefix,
        ):

            raise ValidationError(
                f"'{prefix}' is a reserved permission namespace.",
            )


def validate_permission_activation(
    permission: Permission,
) -> None:
    """
    Validate that the permission can be activated.
    """

    if permission.is_active:

        raise ValidationError(
            "Permission is already active.",
        )


def validate_permission_deactivation(
    permission: Permission,
) -> None:
    """
    Validate that the permission can be deactivated.

    A permission must be active before deactivation.
    Mandatory permissions required by protected system
    roles cannot be deactivated.
    """

    if not permission.is_active:

        raise ValidationError(
            "Permission is already inactive.",
        )

    for role_code in PROTECTED_ROLES:

        required_permissions = get_required_permissions(
            role_code,
        )

        if permission.code in required_permissions:

            raise ValidationError(
                "Mandatory system permissions cannot be deactivated.",
            )


def validate_permission_deletion(
    permission: Permission,
) -> None:
    """
    Validate that a mandatory system permission
    cannot be physically deleted.
    """

    for role_code in PROTECTED_ROLES:

        required_permissions = get_required_permissions(
            role_code,
        )

        if permission.code in required_permissions:

            raise ValidationError(
                "Mandatory system permissions cannot be deleted.",
            )

        
def validate_permission_not_assigned_to_any_role(
    permission: Permission,
) -> None:
    """
    Validate that the permission is not currently
    assigned to any role.
    """

    if RolePermission.objects.filter(
        permission=permission,
    ).exists():

        raise ValidationError(
            "Permission is assigned to one or more roles.",
        )

    
def validate_permission_is_active(
    permission: Permission,
) -> None:
    """
    Validate that only active permissions can be
    assigned to roles.
    """

    if not permission.is_active:

        raise ValidationError(
            "Inactive permissions cannot be assigned.",
        )

# ==========================================================
# Role Validators
# ==========================================================

def validate_role_code(
    code: str,
    role: Role | None = None,
) -> None:
    """
    Validate that the role code is unique.
    """

    queryset = Role.objects.filter(
        code=code,
    )

    if role is not None:

        queryset = queryset.exclude(
            pk=role.pk,
        )

    if queryset.exists():

        raise ValidationError(
            "A role with this code already exists.",
        )


def validate_role_name(
    name: str,
    role: Role | None = None,
) -> None:
    """
    Validate that the role name is unique.
    """

    queryset = Role.objects.filter(
        name=name,
    )

    if role is not None:

        queryset = queryset.exclude(
            pk=role.pk,
        )

    if queryset.exists():

        raise ValidationError(
            "A role with this name already exists.",
        )


def validate_role_activation(
    role: Role,
) -> None:
    """
    Validate that the role can be activated.
    """

    if role.is_active:

        raise ValidationError(
            "Role is already active.",
        )


def validate_role_deactivation(
    role: Role,
) -> None:
    """
    Validate that the role can be deactivated.
    """

    if not role.is_active:

        raise ValidationError(
            "Role is already inactive.",
        )


def validate_role_deletion(
    role: Role,
) -> None:
    """
    Validate that the role is allowed to be deleted.
    """

    if is_protected_role(
        role.code,
    ):

        raise ValidationError(
            "Protected system roles cannot be deleted.",
        )


def validate_system_role_modification(
    role: Role,
) -> None:
    """
    Validate that protected system roles cannot
    be modified.
    """

    if is_protected_role(
        role.code,
    ):

        raise ValidationError(
            "Protected system roles cannot be modified.",
        )


def validate_role_not_in_use(
    role: Role,
) -> None:
    """
    Validate that the role is not assigned to employees
    and does not have permission mappings.
    """

    if EmployeeRole.objects.filter(
        role=role,
    ).exists():

        raise ValidationError(
            "Role is assigned to one or more employees.",
        )

    if RolePermission.objects.filter(
        role=role,
    ).exists():

        raise ValidationError(
            "Role has assigned permissions.",
        )


def validate_role_is_active(
    role: Role,
) -> None:
    """
    Validate that only active roles can be assigned
    to employees.
    """

    if not role.is_active:

        raise ValidationError(
            "Inactive roles cannot be assigned.",
        )

# ==========================================================
# Role Permission Validators
# ==========================================================

def validate_duplicate_role_permission(
    role: Role,
    permission: Permission,
) -> None:
    """
    Validate that the permission is not already assigned
    to the supplied role.
    """

    if RolePermission.objects.filter(
        role=role,
        permission=permission,
    ).exists():

        raise ValidationError(
            "This permission is already assigned to the role.",
        )


def validate_role_permission_removal(
    role: Role,
    permission: Permission,
) -> None:
    """
    Validate that the permission assignment exists before
    attempting removal.
    """

    if not RolePermission.objects.filter(
        role=role,
        permission=permission,
    ).exists():

        raise ValidationError(
            "The permission is not assigned to this role.",
        )


def validate_mandatory_permission_removal(
    role: Role,
    permission: Permission,
) -> None:
    """
    Validate that mandatory permissions cannot be removed
    from protected system roles.
    """

    if not is_protected_role(
        role.code,
    ):
        return

    required_permissions = get_required_permissions(
        role.code,
    )

    if permission.code in required_permissions:

        raise ValidationError(
            "Mandatory permissions cannot be removed from this role.",
        )


def validate_mandatory_permission_set(
    role: Role,
    permissions: Iterable[Permission],
) -> None:
    """
    Validate that protected roles retain every mandatory
    permission during bulk replacement.
    """

    if not is_protected_role(
        role.code,
    ):
        return

    required_permissions = get_required_permissions(
        role.code,
    )

    incoming_permission_codes = {
        permission.code
        for permission in permissions
    }

    missing_permissions = (
        required_permissions
        - incoming_permission_codes
    )

    if missing_permissions:

        raise ValidationError(
            "Protected roles must retain all mandatory permissions.",
        )


def validate_duplicate_permission_assignments(
    permissions: Iterable[Permission],
) -> None:
    """
    Validate that duplicate permissions are not supplied
    during bulk assignment.
    """

    seen_permission_codes = set()

    for permission in permissions:

        if permission.code in seen_permission_codes:

            raise ValidationError(
                f"Duplicate permission '{permission.code}' found.",
            )

        seen_permission_codes.add(
            permission.code,
        )


def validate_assignable_permissions(
    permissions: Iterable[Permission],
) -> None:
    """
    Validate that every supplied permission is active
    before assignment.
    """

    for permission in permissions:

        validate_permission_is_active(
            permission,
        )

# ==========================================================
# Employee Role Validators
# ==========================================================

def validate_duplicate_employee_role(
    employee: Employee,
    role: Role,
) -> None:
    """
    Validate that the employee is not already assigned
    the supplied role.
    """

    if EmployeeRole.objects.filter(
        employee=employee,
        role=role,
    ).exists():

        raise ValidationError(
            "This role is already assigned to the employee.",
        )


def validate_employee_role_exists(
    employee: Employee,
    role: Role,
) -> None:
    """
    Validate that the employee currently holds
    the supplied role.
    """

    if not EmployeeRole.objects.filter(
        employee=employee,
        role=role,
    ).exists():

        raise ValidationError(
            "The employee is not assigned this role.",
        )


def validate_primary_role_assignment(
    employee: Employee,
    employee_role: EmployeeRole | None = None,
) -> None:
    """
    Validate that an employee has at most one
    active primary role.
    """

    queryset = EmployeeRole.objects.filter(
        employee=employee,
        is_primary=True,
        is_active=True,
    )

    if employee_role is not None:

        queryset = queryset.exclude(
            pk=employee_role.pk,
        )

    if queryset.exists():

        raise ValidationError(
            "The employee already has a primary role.",
        )


def validate_primary_role_removal(
    employee_role: EmployeeRole,
) -> None:
    """
    Validate that a primary role cannot be removed
    while it is still the employee's only primary role.
    """

    if not employee_role.is_primary:
        return

    remaining_primary_roles = (
        EmployeeRole.objects.filter(
            employee=employee_role.employee,
            is_primary=True,
            is_active=True,
        )
        .exclude(
            pk=employee_role.pk,
        )
    )

    if not remaining_primary_roles.exists():

        raise ValidationError(
            "An employee must always have one primary role.",
        )


def validate_role_assignment(
    employee: Employee,
    role: Role,
) -> None:
    """
    Validate that the role can be assigned
    to the employee.
    """

    validate_role_is_active(
        role,
    )

    validate_duplicate_employee_role(
        employee,
        role,
    )


def validate_role_assigner(
    assigned_by: Employee | None,
) -> None:
    """
    Validate that the assigning employee
    is active.
    """

    if assigned_by is None:
        return

    if not assigned_by.is_active:

        raise ValidationError(
            "Inactive employees cannot assign roles.",
        )


def validate_employee_role_activation(
    employee_role: EmployeeRole,
) -> None:
    """
    Validate that the employee role can
    be activated.
    """

    if employee_role.is_active:

        raise ValidationError(
            "Employee role is already active.",
        )


def validate_employee_role_deactivation(
    employee_role: EmployeeRole,
) -> None:
    """
    Validate that the employee role can
    be deactivated.
    """

    if not employee_role.is_active:

        raise ValidationError(
            "Employee role is already inactive.",
        )


def validate_employee_role_deletion(
    employee_role: EmployeeRole,
) -> None:
    """
    Validate that the employee role
    can be removed.
    """

    validate_primary_role_removal(
        employee_role,
    )


# ==========================================================
# Employee Permission Override Validators
# ==========================================================

def validate_duplicate_permission_override(
    employee: Employee,
    permission: Permission,
) -> None:
    """
    Validate that the employee does not already have
    an override for the supplied permission.
    """

    if EmployeePermissionOverride.objects.filter(
        employee=employee,
        permission=permission,
    ).exists():

        raise ValidationError(
            "A permission override already exists for this employee.",
        )

def validate_permission_override_exists(
    employee: Employee,
    permission: Permission,
) -> None:
    """
    Validate that the employee currently has
    a permission override.
    """

    if not EmployeePermissionOverride.objects.filter(
        employee=employee,
        permission=permission,
    ).exists():

        raise ValidationError(
            "Permission override does not exist.",
        )

def validate_override_permission_is_active(
    permission: Permission,
) -> None:
    """
    Validate that the permission is active
    before assigning an override.
    """

    validate_permission_is_active(
        permission,
    )

def validate_override_assigner(
    granted_by: Employee | None,
) -> None:
    """
    Validate that the granting employee
    is active.
    """

    if granted_by is None:
        return

    if not granted_by.is_active:

        raise ValidationError(
            "Inactive employees cannot grant permission overrides.",
        )

def validate_override_effect(
    effect: str,
) -> None:
    """
    Validate the override effect.
    """

    if effect not in PermissionEffect.values:

        raise ValidationError(
            "Invalid permission override effect.",
        )

def validate_permission_override_activation(
    override: EmployeePermissionOverride,
) -> None:
    """
    Validate that the permission override
    can be activated.
    """

    if override.is_active:

        raise ValidationError(
            "Permission override is already active.",
        )

def validate_permission_override_deactivation(
    override: EmployeePermissionOverride,
) -> None:
    """
    Validate that the permission override
    can be deactivated.
    """

    if not override.is_active:

        raise ValidationError(
            "Permission override is already inactive.",
        )

def validate_permission_override_deletion(
    override: EmployeePermissionOverride,
) -> None:
    """
    Validate that the permission override
    can be removed.
    """

    if not override.is_active:

        raise ValidationError(
            "Inactive permission overrides cannot be removed.",
        )


# ==========================================================
# Authorization Validators (Cross-Module)
# ==========================================================

def validate_employee_permission(
    employee: Employee,
    permission_code: str,
) -> None:
    """
    Validate that the employee possesses
    the supplied permission.
    """

    if not has_permission(
        employee,
        permission_code,
    ):

        raise ValidationError(
            "You do not have permission to perform this action.",
        )

def validate_employee_permissions(
    employee: Employee,
    permission_codes: Iterable[str],
) -> None:
    """
    Validate that the employee possesses
    every supplied permission.
    """

    if not has_all_permissions(
        employee,
        permission_codes,
    ):

        raise ValidationError(
            "Required permissions are missing.",
        )

def validate_any_permission(
    employee: Employee,
    permission_codes: Iterable[str],
) -> None:
    """
    Validate that the employee possesses
    at least one supplied permission.
    """

    if not has_any_permission(
        employee,
        permission_codes,
    ):

        raise ValidationError(
            "At least one required permission is missing.",
        )

def validate_module_access(
    employee: Employee,
    module: str,
) -> None:
    """
    Validate that the employee can
    access the supplied module.
    """

    if not can_access_module(
        employee,
        module,
    ):

        raise ValidationError(
            "You do not have access to this module.",
        )

def validate_action_access(
    employee: Employee,
    module: str,
    action: str,
) -> None:
    """
    Validate that the employee can
    perform the supplied module action.
    """

    if not can_perform_action(
        employee,
        module,
        action,
    ):

        raise ValidationError(
            "You are not authorized to perform this action.",
        )

def validate_super_admin(
    employee: Employee,
) -> None:
    """
    Validate that the employee is
    a Super Administrator.
    """

    if not is_super_admin(
        employee,
    ):

        raise ValidationError(
            "Only Super Administrators may perform this action.",
        )

def validate_system_admin(
    employee: Employee,
) -> None:
    """
    Validate that the employee is
    a System Administrator.
    """

    if not is_system_admin(
        employee,
    ):

        raise ValidationError(
            "Only System Administrators may perform this action.",
        )
