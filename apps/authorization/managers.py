from django.db import models

from apps.authorization.choices import PermissionEffect


# ==========================================================
# Permission QuerySet & Manager
# ==========================================================

class PermissionQuerySet(models.QuerySet):
    """
    Custom queryset for Permission model.
    """

    def active(self):
        return self.filter(
            is_active=True,
        )

    def by_code(self, code):
        return self.filter(
            code=code,
        )

    def by_module(self, module):
        return self.filter(
            module=module,
        )

    def by_action(self, action):
        return self.filter(
            action=action,
        )


class PermissionManager(models.Manager):
    """
    Custom manager for Permission model.
    """

    def get_queryset(self):
        return PermissionQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def by_code(self, code):
        return self.get_queryset().by_code(
            code,
        )

    def by_module(self, module):
        return self.get_queryset().by_module(
            module,
        )

    def by_action(self, action):
        return self.get_queryset().by_action(
            action,
        )


# ==========================================================
# Role QuerySet & Manager
# ==========================================================

class RoleQuerySet(models.QuerySet):
    """
    Custom queryset for Role model.
    """

    def active(self):
        return self.filter(
            is_active=True,
        )

    def by_code(self, code):
        return self.filter(
            code=code,
        )

    def system_roles(self):
        return self.active().filter(
            is_system_role=True,
        )

    def custom_roles(self):
        return self.active().filter(
            is_system_role=False,
        )


class RoleManager(models.Manager):
    """
    Custom manager for Role model.
    """

    def get_queryset(self):
        return RoleQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def by_code(self, code):
        return self.get_queryset().by_code(
            code,
        )

    def system_roles(self):
        return self.get_queryset().system_roles()

    def custom_roles(self):
        return self.get_queryset().custom_roles()


# ==========================================================
# RolePermission QuerySet & Manager
# ==========================================================

class RolePermissionQuerySet(models.QuerySet):
    """
    Custom queryset for RolePermission model.
    """

    def active(self):
        return self.filter(
            is_active=True,
        )

    def for_role(self, role):
        return self.active().filter(
            role=role,
        )

    def for_permission(self, permission):
        return self.active().filter(
            permission=permission,
        )


class RolePermissionManager(models.Manager):
    """
    Custom manager for RolePermission model.
    """

    def get_queryset(self):
        return RolePermissionQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def for_role(self, role):
        return self.get_queryset().for_role(
            role,
        )

    def for_permission(self, permission):
        return self.get_queryset().for_permission(
            permission,
        )


# ==========================================================
# EmployeeRole QuerySet & Manager
# ==========================================================

class EmployeeRoleQuerySet(models.QuerySet):
    """
    Custom queryset for EmployeeRole model.
    """

    def active(self):
        return self.filter(
            is_active=True,
        )

    def primary(self):
        return self.active().filter(
            is_primary=True,
        )

    def for_employee(self, employee):
        return self.active().filter(
            employee=employee,
        )

    def primary_for_employee(self, employee):
        return self.primary().filter(
            employee=employee,
        )

    def for_role(self, role):
        return self.active().filter(
            role=role,
        )


class EmployeeRoleManager(models.Manager):
    """
    Custom manager for EmployeeRole model.
    """

    def get_queryset(self):
        return EmployeeRoleQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def primary(self):
        return self.get_queryset().primary()

    def for_employee(self, employee):
        return self.get_queryset().for_employee(
            employee,
        )

    def primary_for_employee(self, employee):
        return self.get_queryset().primary_for_employee(
            employee,
        )

    def for_role(self, role):
        return self.get_queryset().for_role(
            role,
        )


# ==========================================================
# EmployeePermissionOverride QuerySet & Manager
# ==========================================================

class EmployeePermissionOverrideQuerySet(models.QuerySet):
    """
    Custom queryset for EmployeePermissionOverride model.
    """

    def active(self):
        return self.filter(
            is_active=True,
        )

    def allow(self):
        return self.active().filter(
            effect=PermissionEffect.ALLOW,
        )

    def deny(self):
        return self.active().filter(
            effect=PermissionEffect.DENY,
        )

    def for_employee(self, employee):
        return self.active().filter(
            employee=employee,
        )

    def for_permission(self, permission):
        return self.active().filter(
            permission=permission,
        )


class EmployeePermissionOverrideManager(models.Manager):
    """
    Custom manager for EmployeePermissionOverride model.
    """

    def get_queryset(self):
        return EmployeePermissionOverrideQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def allow(self):
        return self.get_queryset().allow()

    def deny(self):
        return self.get_queryset().deny()

    def for_employee(self, employee):
        return self.get_queryset().for_employee(
            employee,
        )

    def for_permission(self, permission):
        return self.get_queryset().for_permission(
            permission,
        )