from django.db import models

class PermissionModule(models.TextChoices):
    EMPLOYEE = "employee", "Employee"
    DEPARTMENT = "department", "Department"
    ATTENDANCE = "attendance", "Attendance"
    LEAVE = "leave", "Leave"
    PAYROLL = "payroll", "Payroll"
    APPRAISAL = "appraisal", "Appraisal"
    ROLE = "role", "Role"
    PERMISSION = "permission", "Permission"
    AUTHORIZATION = "authorization", "Authorization"


class PermissionAction(models.TextChoices):
    VIEW = "view", "View"
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"
    ACTIVATE = "activate", "Activate"
    DEACTIVATE = "deactivate", "Deactivate"
    ASSIGN = "assign", "Assign"
    REMOVE = "remove", "Remove"
    EXPORT = "export", "Export"
    IMPORT = "import", "Import"
    RESTORE = "restore", "Restore"


class PermissionEffect(models.TextChoices):
    ALLOW = "ALLOW", "Allow"
    DENY = "DENY", "Deny"