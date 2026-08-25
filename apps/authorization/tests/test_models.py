from django.test import TestCase

from apps.authorization.choices import (
    PermissionAction,
    PermissionModule,
)
from apps.authorization.models import Permission


class PermissionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.permission = Permission.objects.create(
            code="employee.view",
            name="View Employee",
            module=PermissionModule.EMPLOYEE,
            action=PermissionAction.VIEW,
            description="Allows viewing employee records.",
        )

    def test_permission_str(self):
        self.assertEqual(
            str(self.permission),
            "employee.view",
        )

    def test_default_is_active(self):
        self.assertTrue(self.permission.is_active)

    def test_module_saved(self):
        self.assertEqual(
            self.permission.module,
            PermissionModule.EMPLOYEE,
        )

    def test_action_saved(self):
        self.assertEqual(
            self.permission.action,
            PermissionAction.VIEW,
        )

    def test_timestamps_exist(self):
        self.assertIsNotNone(self.permission.created_at)
        self.assertIsNotNone(self.permission.updated_at)