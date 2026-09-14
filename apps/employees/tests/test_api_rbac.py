from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.employees.choices import (
    EmploymentRole,
    EmploymentType,
    EmployeeStatus,
)
from apps.employees.models import (
    Department,
    Designation,
    Employee,
)


User = get_user_model()


class EmployeeAPIRBACTestCase(APITestCase):
    """
    API-level tests for Employee RBAC read access.

    These tests verify that the employee API respects the
    data scope defined by get_accessible_employees().
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.designation = Designation.objects.create(
            name="Software Engineer",
        )

        cls.other_designation = Designation.objects.create(
            name="Accountant",
        )

        # ---------------------------------------------------------
        # Departments
        # ---------------------------------------------------------

        cls.it_department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        cls.finance_department = Department.objects.create(
            name="Finance",
            code="FIN",
        )

        cls.hr_department = Department.objects.create(
            name="Human Resources",
            code="HR",
        )

        # ---------------------------------------------------------
        # Admin
        # ---------------------------------------------------------

        cls.admin = cls.create_employee(
            username="admin",
            email="admin@test.com",
            phone_number="9000000001",
            first_name="Admin",
            last_name="User",
            department=cls.it_department,
            role=EmploymentRole.ADMIN,
        )

        # ---------------------------------------------------------
        # HR
        # ---------------------------------------------------------

        cls.hr = cls.create_employee(
            username="hr",
            email="hr@test.com",
            phone_number="9000000002",
            first_name="HR",
            last_name="User",
            department=cls.hr_department,
            role=EmploymentRole.HR,
        )

        # ---------------------------------------------------------
        # Manager
        # ---------------------------------------------------------

        cls.manager = cls.create_employee(
            username="manager",
            email="manager@test.com",
            phone_number="9000000003",
            first_name="Manager",
            last_name="User",
            department=cls.it_department,
            role=EmploymentRole.MANAGER,
        )

        # Direct subordinate
        cls.direct_subordinate = cls.create_employee(
            username="direct",
            email="direct@test.com",
            phone_number="9000000004",
            first_name="Direct",
            last_name="Subordinate",
            department=cls.it_department,
            reporting_to=cls.manager,
            role=EmploymentRole.EMPLOYEE,
        )

        # Indirect subordinate
        cls.indirect_manager = cls.create_employee(
            username="indirectmanager",
            email="indirectmanager@test.com",
            phone_number="9000000005",
            first_name="Indirect",
            last_name="Manager",
            department=cls.it_department,
            reporting_to=cls.manager,
            role=EmploymentRole.MANAGER,
        )

        cls.indirect_subordinate = cls.create_employee(
            username="indirectemployee",
            email="indirectemployee@test.com",
            phone_number="9000000006",
            first_name="Indirect",
            last_name="Employee",
            department=cls.it_department,
            reporting_to=cls.indirect_manager,
            role=EmploymentRole.EMPLOYEE,
        )

        # Employee unrelated to manager
        cls.unrelated_employee = cls.create_employee(
            username="unrelated",
            email="unrelated@test.com",
            phone_number="9000000007",
            first_name="Unrelated",
            last_name="Employee",
            department=cls.hr_department,
            role=EmploymentRole.EMPLOYEE,
        )

        # ---------------------------------------------------------
        # HOD
        # ---------------------------------------------------------

        cls.hod = cls.create_employee(
            username="hod",
            email="hod@test.com",
            phone_number="9000000008",
            first_name="Finance",
            last_name="HOD",
            department=cls.it_department,
            role=EmploymentRole.MANAGER,
        )

        cls.finance_department.head = cls.hod
        cls.finance_department.save(
            update_fields=["head"],
        )

        cls.finance_employee = cls.create_employee(
            username="financeemployee",
            email="financeemployee@test.com",
            phone_number="9000000009",
            first_name="Finance",
            last_name="Employee",
            department=cls.finance_department,
            role=EmploymentRole.EMPLOYEE,
        )

        # Employee outside HOD's headed department
        cls.hod_outside_employee = cls.create_employee(
            username="hodoutside",
            email="hodoutside@test.com",
            phone_number="9000000010",
            first_name="Outside",
            last_name="Employee",
            department=cls.hr_department,
            role=EmploymentRole.EMPLOYEE,
        )

        # ---------------------------------------------------------
        # Normal Employee
        # ---------------------------------------------------------

        cls.employee = cls.create_employee(
            username="employee",
            email="employee@test.com",
            phone_number="9000000011",
            first_name="Normal",
            last_name="Employee",
            department=cls.it_department,
            role=EmploymentRole.EMPLOYEE,
        )

    @classmethod
    def create_employee(
        cls,
        username,
        email,
        phone_number,
        first_name,
        last_name,
        department,
        role,
        reporting_to=None,
    ):
        """
        Create a User and corresponding Employee.
        """

        user = User.objects.create_user(
            username=username,
            email=email,
            password="Admin@123",
        )

        return Employee.objects.create(
            user=user,
            employee_code=f"TEST{phone_number[-4:]}",
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date.today(),
            department=department,
            designation=cls.designation,
            reporting_to=reporting_to,
            role=role,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

    def authenticate_as(self, employee):
        """
        Authenticate the API client as the User belonging
        to the supplied Employee.
        """

        self.client.force_authenticate(
            user=employee.user,
        )

    def employee_list_url(self):
        return "/api/employees/"

    def employee_detail_url(self, employee):
        return f"/api/employees/{employee.id}/"

    # ============================================================
    # LIST API TESTS
    # ============================================================

    def test_admin_can_list_all_employees(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            self.employee_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            employee["id"]
            for employee in response.data
        }

        expected_ids = set(
            Employee.objects.values_list(
                "id",
                flat=True,
            )
        )

        self.assertEqual(
            returned_ids,
            expected_ids,
        )

    def test_hr_can_list_all_employees(self):
        self.authenticate_as(self.hr)

        response = self.client.get(
            self.employee_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            employee["id"]
            for employee in response.data
        }

        expected_ids = set(
            Employee.objects.values_list(
                "id",
                flat=True,
            )
        )

        self.assertEqual(
            returned_ids,
            expected_ids,
        )

    def test_manager_can_list_direct_subordinates_only(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            self.employee_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            employee["id"]
            for employee in response.data
        }

        self.assertEqual(
            returned_ids,
            {
                self.direct_subordinate.id,
                self.indirect_manager.id,
            },
        )

        self.assertNotIn(
            self.indirect_subordinate.id,
            returned_ids,
        )

        self.assertNotIn(
            self.unrelated_employee.id,
            returned_ids,
        )

    def test_hod_can_list_employees_in_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.get(
            self.employee_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            employee["id"]
            for employee in response.data
        }

        self.assertIn(
            self.finance_employee.id,
            returned_ids,
        )

        self.assertNotIn(
            self.hod_outside_employee.id,
            returned_ids,
        )

    def test_employee_can_list_self_only(self):
        self.authenticate_as(self.employee)

        response = self.client.get(
            self.employee_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            employee["id"]
            for employee in response.data
        }

        self.assertEqual(
            returned_ids,
            {
                self.employee.id,
            },
        )

    # ============================================================
    # RETRIEVE API TESTS
    # ============================================================

    def test_admin_can_retrieve_any_employee(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            self.employee_detail_url(
                self.unrelated_employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.unrelated_employee.id,
        )

    def test_hr_can_retrieve_any_employee(self):
        self.authenticate_as(self.hr)

        response = self.client.get(
            self.employee_detail_url(
                self.unrelated_employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.unrelated_employee.id,
        )

    def test_manager_can_retrieve_direct_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            self.employee_detail_url(
                self.direct_subordinate,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.direct_subordinate.id,
        )

    def test_manager_cannot_retrieve_indirect_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            self.employee_detail_url(
                self.indirect_subordinate,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_cannot_retrieve_unrelated_employee(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            self.employee_detail_url(
                self.unrelated_employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_hod_can_retrieve_employee_in_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.get(
            self.employee_detail_url(
                self.finance_employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.finance_employee.id,
        )

    def test_hod_cannot_retrieve_employee_outside_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.get(
            self.employee_detail_url(
                self.hod_outside_employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_employee_can_retrieve_self(self):
        self.authenticate_as(self.employee)

        response = self.client.get(
            self.employee_detail_url(
                self.employee,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.employee.id,
        )

    def test_employee_cannot_retrieve_another_employee(self):
        self.authenticate_as(self.employee)

        response = self.client.get(
            self.employee_detail_url(
                self.direct_subordinate,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ============================================================
    # FIELD VISIBILITY TESTS
    # ============================================================

    def assert_fields_present(self, response, fields):
        for field in fields:
            self.assertIn(field, response.data)

    def assert_fields_hidden(self, response, fields):
        for field in fields:
            self.assertNotIn(field, response.data)

    def test_admin_can_see_all_employee_business_fields(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            self.employee_detail_url(self.employee)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assert_fields_present(
            response,
            {
                "id",
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "date_of_birth",
                "profile_photo",
                "address",
                "department",
                "designation",
                "reporting_to",
                "date_of_joining",
                "employment_type",
                "role",
                "status",
                "salary",
            },
        )

        self.assert_fields_hidden(
            response,
            {
                "created_at",
                "updated_at",
            },
        )

    def test_hr_can_see_all_employee_business_fields(self):
        self.authenticate_as(self.hr)

        response = self.client.get(
            self.employee_detail_url(self.employee)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assert_fields_present(
            response,
            {
                "id",
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "date_of_birth",
                "profile_photo",
                "address",
                "department",
                "designation",
                "reporting_to",
                "date_of_joining",
                "employment_type",
                "role",
                "status",
                "salary",
            },
        )

        self.assert_fields_hidden(
            response,
            {
                "created_at",
                "updated_at",
            },
        )

    def test_hod_cannot_see_private_employee_fields(self):
        self.authenticate_as(self.hod)

        response = self.client.get(
            self.employee_detail_url(self.finance_employee)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assert_fields_present(
            response,
            {
                "id",
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "profile_photo",
                "department",
                "designation",
                "reporting_to",
                "date_of_joining",
                "employment_type",
                "role",
                "status",
            },
        )

        self.assert_fields_hidden(
            response,
            {
                "date_of_birth",
                "address",
                "salary",
                "created_at",
                "updated_at",
            },
        )

    def test_manager_cannot_see_private_employee_fields(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            self.employee_detail_url(self.direct_subordinate)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assert_fields_present(
            response,
            {
                "id",
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "profile_photo",
                "department",
                "designation",
                "reporting_to",
                "date_of_joining",
                "employment_type",
                "role",
                "status",
            },
        )

        self.assert_fields_hidden(
            response,
            {
                "date_of_birth",
                "address",
                "salary",
                "created_at",
                "updated_at",
            },
        )

    def test_employee_can_see_own_business_fields(self):
        self.authenticate_as(self.employee)

        response = self.client.get(
            self.employee_detail_url(self.employee)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assert_fields_present(
            response,
            {
                "id",
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "date_of_birth",
                "profile_photo",
                "address",
                "department",
                "designation",
                "reporting_to",
                "date_of_joining",
                "employment_type",
                "role",
                "status",
                "salary",
            },
        )

        self.assert_fields_hidden(
            response,
            {
                "created_at",
                "updated_at",
            },
        )

    # ============================================================
    # CREATE API TESTS
    # ============================================================

    def create_employee_payload(self):
        """
        Return valid data for creating an employee.
        """

        return {
            "username": "newemployee",
            "first_name": "New",
            "last_name": "Employee",
            "email": "newemployee@test.com",
            "phone_number": "9000000012",
            "date_of_birth": "1998-01-01",
            "address": "Test Address",
            "department": self.it_department.id,
            "designation": self.designation.id,
            "reporting_to": self.manager.id,
            "date_of_joining": date.today().isoformat(),
            "employment_type": EmploymentType.FULL_TIME,
            "role": EmploymentRole.EMPLOYEE,
            "salary": "50000.00",
        }

    def test_admin_can_create_employee(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.employee_list_url(),
            self.create_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_hr_can_create_employee(self):
        self.authenticate_as(self.hr)

        response = self.client.post(
            self.employee_list_url(),
            self.create_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_hod_cannot_create_employee(self):
        self.authenticate_as(self.hod)

        response = self.client.post(
            self.employee_list_url(),
            self.create_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_cannot_create_employee(self):
        self.authenticate_as(self.manager)

        response = self.client.post(
            self.employee_list_url(),
            self.create_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_create_employee(self):
        self.authenticate_as(self.employee)

        response = self.client.post(
            self.employee_list_url(),
            self.create_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ============================================================
    # UPDATE API TESTS
    # ============================================================

    def update_employee_payload(self, address="Updated Address"):
        """
        Return valid data for updating an employee.

        Address is deliberately used here because this step tests
        record-level authorization, not field-level permissions.
        """

        return {
            "address": address,
        }

    # ------------------------------------------------------------
    # PATCH
    # ------------------------------------------------------------

    def test_admin_can_patch_any_employee(self):
        self.authenticate_as(self.admin)

        response = self.client.patch(
            self.employee_detail_url(self.unrelated_employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hr_can_patch_any_employee(self):
        self.authenticate_as(self.hr)

        response = self.client.patch(
            self.employee_detail_url(self.unrelated_employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_can_patch_employee_in_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.patch(
            self.employee_detail_url(self.finance_employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_cannot_patch_employee_outside_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.patch(
            self.employee_detail_url(self.hod_outside_employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_can_patch_direct_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.patch(
            self.employee_detail_url(self.direct_subordinate),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_cannot_patch_indirect_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.patch(
            self.employee_detail_url(self.indirect_subordinate),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_cannot_patch_unrelated_employee(self):
        self.authenticate_as(self.manager)

        response = self.client.patch(
            self.employee_detail_url(self.unrelated_employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_can_patch_self(self):
        self.authenticate_as(self.employee)

        response = self.client.patch(
            self.employee_detail_url(self.employee),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_cannot_patch_another_employee(self):
        self.authenticate_as(self.employee)

        response = self.client.patch(
            self.employee_detail_url(self.direct_subordinate),
            self.update_employee_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # ------------------------------------------------------------------
    # PUT
    # ------------------------------------------------------------------

    def update_employee_put_payload(
        self,
        employee,
        department,
    ):
        """
        Return valid data for a full employee update.

        PUT requires all writable employee fields.

        A different department is supplied because the existing
        department-transfer validation rejects assigning an employee
        to the department they are already assigned to.

        This step tests record-level authorization only.
        """

        return {
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "phone_number": employee.phone_number,
            "date_of_birth": employee.date_of_birth.isoformat(),
            "profile_photo": None,
            "address": "Updated Address",
            "department": department.id,
            "designation": employee.designation.id,
            "reporting_to": (
                employee.reporting_to.id
                if employee.reporting_to
                else None
            ),
            "date_of_joining": employee.date_of_joining.isoformat(),
            "employment_type": employee.employment_type,
            "role": employee.role,
            "salary": str(employee.salary),
        }

    # ------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------

    def test_admin_can_put_any_employee(self):
        self.authenticate_as(self.admin)

        response = self.client.put(
            self.employee_detail_url(self.manager),
            self.update_employee_put_payload(
                self.manager,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ------------------------------------------------------------
    # HR
    # ------------------------------------------------------------

    def test_hr_can_put_any_employee(self):
        self.authenticate_as(self.hr)

        response = self.client.put(
            self.employee_detail_url(self.manager),
            self.update_employee_put_payload(
                self.manager,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ------------------------------------------------------------
    # HOD
    # ------------------------------------------------------------

    def test_hod_can_put_employee_in_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.put(
            self.employee_detail_url(self.finance_employee),
            self.update_employee_put_payload(
                self.finance_employee,
                department=self.it_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_cannot_put_employee_outside_headed_department(self):
        self.authenticate_as(self.hod)

        response = self.client.put(
            self.employee_detail_url(self.hod_outside_employee),
            self.update_employee_put_payload(
                self.hod_outside_employee,
                department=self.it_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------

    def test_manager_can_put_direct_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.put(
            self.employee_detail_url(self.direct_subordinate),
            self.update_employee_put_payload(
                self.direct_subordinate,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_cannot_put_indirect_subordinate(self):
        self.authenticate_as(self.manager)

        response = self.client.put(
            self.employee_detail_url(self.indirect_subordinate),
            self.update_employee_put_payload(
                self.indirect_subordinate,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_cannot_put_unrelated_employee(self):
        self.authenticate_as(self.manager)

        response = self.client.put(
            self.employee_detail_url(self.unrelated_employee),
            self.update_employee_put_payload(
                self.unrelated_employee,
                department=self.it_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ------------------------------------------------------------
    # Employee
    # ------------------------------------------------------------

    def test_employee_can_put_self(self):
        self.authenticate_as(self.employee)

        response = self.client.put(
            self.employee_detail_url(self.employee),
            self.update_employee_put_payload(
                self.employee,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_cannot_put_another_employee(self):
        self.authenticate_as(self.employee)

        response = self.client.put(
            self.employee_detail_url(self.manager),
            self.update_employee_put_payload(
                self.manager,
                department=self.finance_department,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )