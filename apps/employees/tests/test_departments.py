from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.employees.choices import (
    EmployeeStatus,
    EmploymentRole,
    EmploymentType,
)
from apps.employees.models import (
    Department,
    Designation,
    Employee,
)


class DepartmentAPITestCase(APITestCase):
    """
    Test Department API functionality and business rules.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="AdminPassword123!",
        )

        self.department = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal("500000.00"),
            location="Bangalore",
        )

        self.admin_department = Department.objects.create(
            name="Administration",
            code="ADM",
            budget=Decimal("100000.00"),
            location="Bangalore",
        )

        self.designation = Designation.objects.create(
            name="Software Engineer",
            description="Software engineering role.",
        )

        self.admin_employee = Employee.objects.create(
            user=self.user,
            employee_code=f"EMP{self.user.id:04d}",
            first_name="Test",
            last_name="Admin",
            email="admin@example.com",
            phone_number=f"98765{self.user.id:05d}",
            date_of_birth="1990-01-01",
            department=self.admin_department,
            designation=self.designation,
            date_of_joining="2020-01-01",
            employment_type=EmploymentType.FULL_TIME,
            role=EmploymentRole.ADMIN,
            status=EmployeeStatus.ACTIVE,
            salary=Decimal("50000.00"),
        )

        self.client.force_authenticate(
            user=self.user,
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def create_employee(
        self,
        username="employee1",
        role=EmploymentRole.EMPLOYEE,
        status=EmployeeStatus.ACTIVE,
        department=None,
    ):
        user = User.objects.create_user(
            username=username,
            password="EmployeePassword123!",
        )

        return Employee.objects.create(
            user=user,
            employee_code=f"EMP{user.id:04d}",
            first_name="Test",
            last_name="Employee",
            email=f"{username}@example.com",
            phone_number=f"98765{user.id:05d}",
            date_of_birth="1995-01-01",
            department=department or self.department,
            designation=self.designation,
            date_of_joining="2020-01-01",
            employment_type=EmploymentType.FULL_TIME,
            role=role,
            status=status,
            salary=Decimal("50000.00"),
        )

    def department_url(self, department_id=None):
        if department_id is None:
            return reverse(
                "department-list-create",
            )

        return reverse(
            "department-detail",
            kwargs={
                "department_id": department_id,
            },
        )

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    def test_department_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            self.department_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ========================================================
    # CREATE
    # ========================================================

    def test_create_department(self):
        data = {
            "name": "Human Resources",
            "code": "HR",
            "budget": "250000.00",
            "location": "Delhi",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Department.objects.filter(
                name="Human Resources",
                code="HR",
            ).exists()
        )

    def test_create_department_rejects_duplicate_name(self):
        data = {
            "name": "Engineering",
            "code": "ENG2",
            "budget": "100000.00",
            "location": "Delhi",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_department_rejects_duplicate_code(self):
        data = {
            "name": "Another Engineering",
            "code": "ENG",
            "budget": "100000.00",
            "location": "Delhi",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_department_rejects_negative_budget(self):
        data = {
            "name": "Finance",
            "code": "FIN",
            "budget": "-1000.00",
            "location": "Mumbai",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ========================================================
    # MANAGER / HEAD VALIDATION
    # ========================================================

    def test_create_department_accepts_active_manager(self):
        manager = self.create_employee(
            username="manager1",
            role=EmploymentRole.MANAGER,
            status=EmployeeStatus.ACTIVE,
        )

        data = {
            "name": "Product",
            "code": "PROD",
            "manager": manager.id,
            "budget": "300000.00",
            "location": "Bangalore",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        department = Department.objects.get(
            code="PROD",
        )

        self.assertEqual(
            department.manager,
            manager,
        )

    def test_create_department_rejects_non_manager_as_manager(self):
        employee = self.create_employee(
            username="normalemployee",
            role=EmploymentRole.EMPLOYEE,
            status=EmployeeStatus.ACTIVE,
        )

        data = {
            "name": "Finance",
            "code": "FIN",
            "manager": employee.id,
            "budget": "300000.00",
            "location": "Mumbai",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_department_rejects_inactive_manager(self):
        manager = self.create_employee(
            username="inactivemanager",
            role=EmploymentRole.MANAGER,
            status=EmployeeStatus.INACTIVE,
        )

        data = {
            "name": "Finance",
            "code": "FIN",
            "manager": manager.id,
            "budget": "300000.00",
            "location": "Mumbai",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_department_accepts_active_manager_as_head(self):
        manager = self.create_employee(
            username="managerhead",
            role=EmploymentRole.MANAGER,
            status=EmployeeStatus.ACTIVE,
        )

        data = {
            "name": "Operations",
            "code": "OPS",
            "manager": manager.id,
            "head": manager.id,
            "budget": "300000.00",
            "location": "Bangalore",
        }

        response = self.client.post(
            self.department_url(),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # ========================================================
    # RETRIEVE
    # ========================================================

    def test_list_departments(self):
        response = self.client.get(
            self.department_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            len(response.data) >= 1,
        )

    def test_retrieve_department(self):
        response = self.client.get(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["name"],
            "Engineering",
        )

        self.assertEqual(
            response.data["code"],
            "ENG",
        )

    def test_retrieve_nonexistent_department(self):
        response = self.client.get(
            self.department_url(999999),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def test_patch_department(self):
        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "location": "Mumbai",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.department.refresh_from_db()

        self.assertEqual(
            self.department.location,
            "Mumbai",
        )

    def test_put_department(self):
        data = {
            "name": "Engineering Updated",
            "code": "ENG2",
            "budget": "750000.00",
            "location": "Pune",
        }

        response = self.client.put(
            self.department_url(
                self.department.id,
            ),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.department.refresh_from_db()

        self.assertEqual(
            self.department.name,
            "Engineering Updated",
        )

        self.assertEqual(
            self.department.code,
            "ENG2",
        )

    def test_patch_department_cannot_change_is_active(self):
        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.department.refresh_from_db()

        self.assertTrue(
            self.department.is_active,
        )

    # ========================================================
    # LEADERSHIP INTEGRITY
    # ========================================================

    def test_manager_cannot_lose_manager_role_while_leading_department(self):
        manager = self.create_employee(
            username="leadmanager",
            role=EmploymentRole.MANAGER,
            status=EmployeeStatus.ACTIVE,
        )

        self.department.manager = manager
        self.department.save()

        response = self.client.patch(
            reverse(
                "employee-detail",
                kwargs={
                    "employee_id": manager.id,
                },
            ),
            {
                "role": EmploymentRole.EMPLOYEE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_manager_cannot_become_inactive_while_leading_department(self):
        manager = self.create_employee(
            username="activelead",
            role=EmploymentRole.MANAGER,
            status=EmployeeStatus.ACTIVE,
        )

        self.department.manager = manager
        self.department.save()

        response = self.client.patch(
            reverse(
                "employee-status",
                kwargs={
                    "employee_id": manager.id,
                },
            ),
            {
                "status": EmployeeStatus.INACTIVE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ========================================================
    # DEACTIVATION
    # ========================================================

    def test_department_deactivation_blocked_with_active_employee(self):
        self.create_employee(
            username="activeemployee",
            role=EmploymentRole.EMPLOYEE,
            status=EmployeeStatus.ACTIVE,
            department=self.department,
        )

        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.department.refresh_from_db()

        self.assertTrue(
            self.department.is_active,
        )

    def test_department_deactivation_succeeds_without_active_employees(self):
        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.department.refresh_from_db()

        self.assertFalse(
            self.department.is_active,
        )

    def test_department_deactivation_allowed_when_employee_is_inactive(self):
        self.create_employee(
            username="inactiveemployee",
            role=EmploymentRole.EMPLOYEE,
            status=EmployeeStatus.INACTIVE,
            department=self.department,
        )

        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.department.refresh_from_db()

        self.assertFalse(
            self.department.is_active,
        )

    # ========================================================
    # RBAC
    # ========================================================

    def authenticate_as_employee(self, employee):
        self.client.force_authenticate(
            user=employee.user,
        )

    def create_department_rbac_employee(
        self,
        username,
        role,
        department=None,
    ):
        return self.create_employee(
            username=username,
            role=role,
            department=department,
        )

    def test_admin_can_list_all_departments(self):
        response = self.client.get(self.department_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 2)

    def test_admin_can_access_administration(self):
        response = self.client.get(
            self.department_url(
                self.admin_department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_create_department(self):
        response = self.client.post(
            self.department_url(),
            {
                "name": "Finance",
                "code": "FIN",
                "budget": "100000.00",
                "location": "Delhi",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_admin_can_update_any_department(self):
        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "location": "Mumbai",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_deactivate_department(self):
        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_hr_can_access_non_administration_department(self):
        hr = self.create_department_rbac_employee(
            "hr_user",
            EmploymentRole.HR,
            self.department,
        )
        self.authenticate_as_employee(hr)

        response = self.client.get(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hr_cannot_access_administration_department(self):
        hr = self.create_department_rbac_employee(
            "hr_user",
            EmploymentRole.HR,
            self.department,
        )
        self.authenticate_as_employee(hr)

        response = self.client.get(
            self.department_url(
                self.admin_department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_hr_can_create_department(self):
        hr = self.create_department_rbac_employee(
            "hr_user",
            EmploymentRole.HR,
            self.department,
        )
        self.authenticate_as_employee(hr)

        response = self.client.post(
            self.department_url(),
            {
                "name": "Finance",
                "code": "FIN",
                "budget": "100000.00",
                "location": "Delhi",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_hr_cannot_deactivate_department(self):
        hr = self.create_department_rbac_employee(
            "hr_user",
            EmploymentRole.HR,
            self.department,
        )
        self.authenticate_as_employee(hr)

        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_hod_can_access_headed_department(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.get(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_cannot_access_unheaded_department(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.get(
            self.department_url(
                self.admin_department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_hod_can_update_headed_department(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "location": "Mumbai",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_can_change_budget(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "budget": "900000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_hod_cannot_change_head(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "head": None,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_hod_cannot_deactivate_department(self):
        hod = self.create_department_rbac_employee(
            "hod_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.head = hod
        self.department.save(
            update_fields=["head"],
        )

        self.authenticate_as_employee(hod)

        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_can_access_managed_department(self):
        manager = self.create_department_rbac_employee(
            "manager_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.manager = manager
        self.department.save(
            update_fields=["manager"],
        )

        self.authenticate_as_employee(manager)

        response = self.client.get(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_cannot_access_unmanaged_department(self):
        manager = self.create_department_rbac_employee(
            "manager_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.manager = manager
        self.department.save(
            update_fields=["manager"],
        )

        self.authenticate_as_employee(manager)

        response = self.client.get(
            self.department_url(
                self.admin_department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_cannot_update_department(self):
        manager = self.create_department_rbac_employee(
            "manager_user",
            EmploymentRole.MANAGER,
            self.department,
        )

        self.department.manager = manager
        self.department.save(
            update_fields=["manager"],
        )

        self.authenticate_as_employee(manager)

        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "location": "Mumbai",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_can_access_own_department(self):
        employee = self.create_department_rbac_employee(
            "normal_employee",
            EmploymentRole.EMPLOYEE,
            self.department,
        )
        self.authenticate_as_employee(employee)

        response = self.client.get(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_cannot_access_other_department(self):
        employee = self.create_department_rbac_employee(
            "normal_employee",
            EmploymentRole.EMPLOYEE,
            self.department,
        )
        self.authenticate_as_employee(employee)

        response = self.client.get(
            self.department_url(
                self.admin_department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_update_department(self):
        employee = self.create_department_rbac_employee(
            "normal_employee",
            EmploymentRole.EMPLOYEE,
            self.department,
        )
        self.authenticate_as_employee(employee)

        response = self.client.patch(
            self.department_url(
                self.department.id,
            ),
            {
                "location": "Mumbai",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_deactivate_department(self):
        employee = self.create_department_rbac_employee(
            "normal_employee",
            EmploymentRole.EMPLOYEE,
            self.department,
        )
        self.authenticate_as_employee(employee)

        response = self.client.delete(
            self.department_url(
                self.department.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )