"""
Authorization module constants.

This module contains business constants shared across the
authorization system.

NOTE:
Do not define model choices here.
Use choices.py for model field choices.
"""

# ==========================================================
# System Role Codes
# ==========================================================

SUPER_ADMIN_ROLE_CODE = "SUPER_ADMIN"

SYSTEM_ADMIN_ROLE_CODE = "SYSTEM_ADMIN"

HR_ROLE_CODE = "HR"

MANAGER_ROLE_CODE = "MANAGER"

EMPLOYEE_ROLE_CODE = "EMPLOYEE"


DEFAULT_SYSTEM_ROLES = (
    SUPER_ADMIN_ROLE_CODE,
    SYSTEM_ADMIN_ROLE_CODE,
    HR_ROLE_CODE,
    MANAGER_ROLE_CODE,
    EMPLOYEE_ROLE_CODE,
)


# ==========================================================
# Protected Roles
# ==========================================================

PROTECTED_ROLES = (
    SUPER_ADMIN_ROLE_CODE,
    SYSTEM_ADMIN_ROLE_CODE,
)


# ==========================================================
# System Role Configuration
# ==========================================================

SYSTEM_ROLE_CONFIGURATION = {

    SUPER_ADMIN_ROLE_CODE: {
        "is_protected": True,
        "required_permissions": {
            "authorization.manage",
            "role.manage",
            "permission.manage",
        },
    },

    SYSTEM_ADMIN_ROLE_CODE: {
        "is_protected": True,
        "required_permissions": {
            "authorization.manage",
            "role.manage",
            "permission.manage",
        },
    },

    HR_ROLE_CODE: {
        "is_protected": False,
        "required_permissions": set(),
    },

    MANAGER_ROLE_CODE: {
        "is_protected": False,
        "required_permissions": set(),
    },

    EMPLOYEE_ROLE_CODE: {
        "is_protected": False,
        "required_permissions": set(),
    },

}


# ==========================================================
# Permission Naming
# ==========================================================

PERMISSION_SEPARATOR = "."

PERMISSION_CODE_FORMAT = "{module}.{action}"


# ==========================================================
# Reserved Permission Namespaces
# ==========================================================

RESERVED_PERMISSION_PREFIXES = (
    "system.",
    "internal.",
)


# ==========================================================
# Audit Event Messages
# ==========================================================

ROLE_ASSIGNED = "Role assigned"

ROLE_REMOVED = "Role removed"

PERMISSION_GRANTED = "Permission granted"

PERMISSION_REVOKED = "Permission revoked"


# ==========================================================
# Cache Keys
# ==========================================================

PERMISSION_CACHE_KEY = (
    "employee_permissions:{employee_id}"
)

ROLE_CACHE_KEY = (
    "employee_roles:{employee_id}"
)

EFFECTIVE_PERMISSION_CACHE_KEY = (
    "effective_permissions:{employee_id}"
)