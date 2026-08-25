from django.db import transaction

from .models import Permission
from .validators import (
    validate_permission_code,
    validate_permission_code_structure,
    validate_permission_deactivation,
    validate_permission_activation,
    validate_permission_name,
    validate_reserved_permission_code,
    validate_permission_deletion,
    validate_permission_not_assigned_to_any_role,
)


class PermissionService:
    """
    Service layer responsible for managing Permission objects.
    """

    @staticmethod
    @transaction.atomic
    def create_permission(
        *,
        code: str,
        name: str,
        module: str,
        action: str,
        description: str = "",
    ) -> Permission:
        """
        Create a new permission after validating
        all permission creation rules.
        """

        validate_permission_code(
            code,
        )

        validate_permission_name(
            name,
        )

        validate_permission_code_structure(
            code,
            module,
            action,
        )

        validate_reserved_permission_code(
            code,
        )

        return Permission.objects.create(
            code=code,
            name=name,
            module=module,
            action=action,
            description=description,
        )

    @staticmethod
    @transaction.atomic
    def update_permission(
        permission: Permission,
        *,
        code: str,
        name: str,
        module: str,
        action: str,
        description: str = "",
    ) -> Permission:
        """
        Update an existing permission after validating
        all permission update rules.
        """

        validate_permission_code(
            code,
            permission=permission,
        )

        validate_permission_name(
            name,
            permission=permission,
        )

        validate_permission_code_structure(
            code,
            module,
            action,
        )

        validate_reserved_permission_code(
            code,
        )

        permission.code = code
        permission.name = name
        permission.module = module
        permission.action = action
        permission.description = description

        permission.save()

        return permission

    @staticmethod
    @transaction.atomic
    def activate_permission(
        permission: Permission,
    ) -> Permission:
        """
        Activate an inactive permission.
        """

        validate_permission_activation(
            permission,
        )

        permission.is_active = True

        permission.save(
            update_fields=(
                "is_active",
                "updated_at",
            ),
        )

        return permission

    @staticmethod
    @transaction.atomic
    def deactivate_permission(
        permission: Permission,
    ) -> Permission:
        """
        Deactivate an active permission.

        Mandatory permissions required by protected
        system roles are rejected by the validator.
        """

        validate_permission_deactivation(
            permission,
        )

        permission.is_active = False

        permission.save(
            update_fields=(
                "is_active",
                "updated_at",
            ),
        )

        return permission

    @staticmethod
    @transaction.atomic
    def delete_permission(
        permission: Permission,
    ) -> None:
        """
        Permanently delete a permission after validating
        that it is safe to remove.
        """

        validate_permission_deletion(
            permission,
        )

        validate_permission_not_assigned_to_any_role(
            permission,
        )

        permission.delete()

