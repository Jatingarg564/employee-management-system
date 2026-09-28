from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.employees.choices import EmploymentRole, EmploymentType, EmployeeStatus
from apps.employees.models import Department, Designation, Employee

User = get_user_model()


class EmployeeSelfProfileAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        cls.other_department = Department.objects.create(
            name="Finance",
            code="FIN",
        )

        cls.designation = Designation.objects.create(
            name="Software Engineer",
        )

        cls.user = User.objects.create_user(
            username="selfprofileuser",
            email="selfprofileuser@test.com",
            password="StrongPassword@123",
            is_active=True,
        )

        cls.employee = Employee.objects.create(
            user=cls.user,
            employee_code="EMP000001",
            first_name="Self",
            last_name="Profile",
            email="selfprofileuser@test.com",
            phone_number="9000000001",
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date.today(),
            department=cls.department,
            designation=cls.designation,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
            address="Old address",
        )

    def test_self_profile_patch_allows_phone_and_address_update(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            "/api/employees/me/",
            {
                "phone_number": "9000000099",
                "address": "New Delhi, India",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.phone_number, "9000000099")
        self.assertEqual(self.employee.address, "New Delhi, India")

    def test_self_profile_patch_allows_profile_photo_update(self):
        self.client.force_authenticate(user=self.user)

        image = Image.new("RGB", (50, 50), color="blue")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        response = self.client.patch(
            "/api/employees/me/",
            {
                "profile_photo": SimpleUploadedFile(
                    "profile.png",
                    buffer.read(),
                    content_type="image/png",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.profile_photo)

    def test_self_profile_patch_rejects_protected_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            "/api/employees/me/",
            {
                "role": EmploymentRole.MANAGER,
                "department": self.other_department.id,
                "salary": "99999.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.role, EmploymentRole.EMPLOYEE)
        self.assertEqual(self.employee.department, self.department)
        self.assertEqual(self.employee.salary, Decimal("50000"))

    def test_self_profile_requires_authentication(self):
        response = self.client.patch(
            "/api/employees/me/",
            {
                "address": "Unauthenticated",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
