from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.employees.models import Designation


class DesignationAPITestCase(APITestCase):
    """
    Test Designation API functionality.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="AdminPassword123!",
        )

        self.client.force_authenticate(
            user=self.user,
        )

        self.active_designation_1 = Designation.objects.create(
            name="Software Engineer",
            description="Software engineering role.",
            is_active=True,
        )

        self.active_designation_2 = Designation.objects.create(
            name="HR Executive",
            description="Human resources role.",
            is_active=True,
        )

        self.inactive_designation = Designation.objects.create(
            name="Old Designation",
            description="Inactive designation.",
            is_active=False,
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def designation_list_url(self):
        return reverse(
            "designation-list",
        )

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    def test_designation_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            self.designation_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ========================================================
    # LIST
    # ========================================================

    def test_designation_list_returns_active_designations(self):
        response = self.client.get(
            self.designation_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        returned_ids = {
            designation["id"]
            for designation in response.data
        }

        self.assertIn(
            self.active_designation_1.id,
            returned_ids,
        )

        self.assertIn(
            self.active_designation_2.id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_designation.id,
            returned_ids,
        )

    def test_designation_list_is_ordered_by_name(self):
        response = self.client.get(
            self.designation_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        names = [
            designation["name"]
            for designation in response.data
        ]

        self.assertEqual(
            names,
            sorted(names),
        )

    def test_designation_list_returns_expected_fields(self):
        response = self.client.get(
            self.designation_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        designation = response.data[0]

        self.assertEqual(
            set(designation.keys()),
            {
                "id",
                "name",
                "description",
                "is_active",
            },
        )
