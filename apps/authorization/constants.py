"""
Authorization module constants.

This file contains business constants used throughout the
authorization system.

NOTE:
Do NOT place database choices here.
Use choices.py for model field choices.
"""

# ==========================================================
# Default System Roles
# ==========================================================

ADMIN_ROLE = "Admin"
HR_ROLE = "HR"
MANAGER_ROLE = "Manager"
EMPLOYEE_ROLE = "Employee"


DEFAULT_SYSTEM_ROLES = (
    ADMIN_ROLE,
    HR_ROLE,
    MANAGER_ROLE,
    EMPLOYEE_ROLE,
)


# ==========================================================
# Protected Roles
# ==========================================================

PROTECTED_ROLES = (
    ADMIN_ROLE,
)


# ==========================================================
# Reserved Permission Prefix
# ==========================================================

PERMISSION_SEPARATOR = "."


# ==========================================================
# Default Permission Naming Format
# ==========================================================

PERMISSION_CODE_FORMAT = "{module}.{action}"


# ==========================================================
# Override Types
# ==========================================================

GRANT_PERMISSION = True
REVOKE_PERMISSION = False


# ==========================================================
# Audit Messages
# ==========================================================

ROLE_ASSIGNED = "Role assigned"
ROLE_REMOVED = "Role removed"

PERMISSION_GRANTED = "Permission granted"
PERMISSION_REVOKED = "Permission revoked"