from django.db import models
from django.utils import timezone

from apps.authorization.choices import PermissionEffect


class PermissionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            is_active=True,
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

    def get_queryset(self):
        return PermissionQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def by_module(self, module):
        return self.get_queryset().by_module(
            module,
        )

    def by_action(self, action):
        return self.get_queryset().by_action(
            action,
        )


class RoleQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            is_active=True,
        )

    def system_roles(self):
        return self.filter(
            is_system_role=True,
        )

    def custom_roles(self):
        return self.filter(
            is_system_role=False,
        )


class RoleManager(models.Manager):

    def get_queryset(self):
        return RoleQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def system_roles(self):
        return self.get_queryset().system_roles()

    def custom_roles(self):
        return self.get_queryset().custom_roles()


class RolePermissionQuerySet(models.QuerySet):

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


class EmployeeRoleQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            is_active=True,
        )

    def current(self):
        return self.active().filter(
            models.Q(
                expires_at__isnull=True,
            )
            |
            models.Q(
                expires_at__gt=timezone.now(),
            )
        )

    def expired(self):
        return self.active().filter(
            expires_at__lte=timezone.now(),
        )

    def primary(self):
        return self.current().filter(
            is_primary=True,
        )

    def for_employee(self, employee):
        return self.current().filter(
            employee=employee,
        )

    def for_role(self, role):
        return self.current().filter(
            role=role,
        )


class EmployeeRoleManager(models.Manager):

    def get_queryset(self):
        return EmployeeRoleQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def current(self):
        return self.get_queryset().current()

    def expired(self):
        return self.get_queryset().expired()

    def primary(self):
        return self.get_queryset().primary()

    def for_employee(self, employee):
        return self.get_queryset().for_employee(
            employee,
        )

    def for_role(self, role):
        return self.get_queryset().for_role(
            role,
        )


class EmployeePermissionOverrideQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            is_active=True,
        )

    def current(self):
        return self.active().filter(
            models.Q(
                expires_at__isnull=True,
            )
            |
            models.Q(
                expires_at__gt=timezone.now(),
            )
        )

    def expired(self):
        return self.active().filter(
            expires_at__lte=timezone.now(),
        )

    def allow(self):
        return self.current().filter(
            effect=PermissionEffect.ALLOW,
        )

    def deny(self):
        return self.current().filter(
            effect=PermissionEffect.DENY,
        )

    def for_employee(self, employee):
        return self.current().filter(
            employee=employee,
        )


class EmployeePermissionOverrideManager(models.Manager):

    def get_queryset(self):
        return EmployeePermissionOverrideQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def current(self):
        return self.get_queryset().current()

    def expired(self):
        return self.get_queryset().expired()

    def allow(self):
        return self.get_queryset().allow()

    def deny(self):
        return self.get_queryset().deny()

    def for_employee(self, employee):
        return self.get_queryset().for_employee(
            employee,
        )