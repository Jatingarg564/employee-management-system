from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

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
from apps.employees.permissions import (
    get_accessible_employees,
)


User = get_user_model()


class EmployeePermissionTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.designation = Designation.objects.create(
            name="Software Engineer",
        )

        cls.it_department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        cls.hr_department = Department.objects.create(
            name="Human Resource",
            code="HR",
        )

        cls.finance_department = Department.objects.create(
            name="Finance",
            code="FN",
        )

        # -----------------------------------------------------
        # Admin
        # -----------------------------------------------------

        cls.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="Admin@123",
        )

        cls.admin = Employee.objects.create(
            user=cls.admin_user,
            employee_code="EMP000001",
            first_name="Admin",
            last_name="User",
            email="admin@test.com",
            phone_number="9000000001",
            date_of_birth=date(1990, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            role=EmploymentRole.ADMIN,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("100000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # HR
        # -----------------------------------------------------

        cls.hr_user = User.objects.create_user(
            username="hr",
            email="hr@test.com",
            password="Admin@123",
        )

        cls.hr = Employee.objects.create(
            user=cls.hr_user,
            employee_code="EMP000002",
            first_name="Human",
            last_name="Resources",
            email="hr@test.com",
            phone_number="9000000002",
            date_of_birth=date(1991, 1, 1),
            date_of_joining=date.today(),
            department=cls.hr_department,
            designation=cls.designation,
            role=EmploymentRole.HR,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("80000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # Manager
        # -----------------------------------------------------

        cls.manager_user = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="Admin@123",
        )

        cls.manager = Employee.objects.create(
            user=cls.manager_user,
            employee_code="EMP000003",
            first_name="John",
            last_name="Manager",
            email="manager@test.com",
            phone_number="9000000003",
            date_of_birth=date(1990, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            role=EmploymentRole.MANAGER,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("70000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # Direct subordinate of manager
        # -----------------------------------------------------

        cls.direct_subordinate_user = User.objects.create_user(
            username="directemployee",
            email="directemployee@test.com",
            password="Admin@123",
        )

        cls.direct_subordinate = Employee.objects.create(
            user=cls.direct_subordinate_user,
            employee_code="EMP000004",
            first_name="Direct",
            last_name="Employee",
            email="directemployee@test.com",
            phone_number="9000000004",
            date_of_birth=date(1998, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            reporting_to=cls.manager,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # Indirect subordinate of manager
        # -----------------------------------------------------

        cls.indirect_manager_user = User.objects.create_user(
            username="indirectmanager",
            email="indirectmanager@test.com",
            password="Admin@123",
        )

        cls.indirect_manager = Employee.objects.create(
            user=cls.indirect_manager_user,
            employee_code="EMP000005",
            first_name="Indirect",
            last_name="Manager",
            email="indirectmanager@test.com",
            phone_number="9000000005",
            date_of_birth=date(1992, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            reporting_to=cls.manager,
            role=EmploymentRole.MANAGER,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("60000"),
            status=EmployeeStatus.ACTIVE,
        )

        cls.indirect_subordinate_user = User.objects.create_user(
            username="indirectemployee",
            email="indirectemployee@test.com",
            password="Admin@123",
        )

        cls.indirect_subordinate = Employee.objects.create(
            user=cls.indirect_subordinate_user,
            employee_code="EMP000006",
            first_name="Indirect",
            last_name="Employee",
            email="indirectemployee@test.com",
            phone_number="9000000006",
            date_of_birth=date(1998, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            reporting_to=cls.indirect_manager,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("45000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # HOD
        # -----------------------------------------------------

        cls.hod_user = User.objects.create_user(
            username="hod",
            email="hod@test.com",
            password="Admin@123",
        )

        cls.hod = Employee.objects.create(
            user=cls.hod_user,
            employee_code="EMP000007",
            first_name="Department",
            last_name="Head",
            email="hod@test.com",
            phone_number="9000000007",
            date_of_birth=date(1988, 1, 1),
            date_of_joining=date.today(),
            department=cls.finance_department,
            designation=cls.designation,
            role=EmploymentRole.MANAGER,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("90000"),
            status=EmployeeStatus.ACTIVE,
        )

        cls.finance_department.head = cls.hod
        cls.finance_department.save(
            update_fields=["head"],
        )

        # -----------------------------------------------------
        # Employee inside HOD department
        # -----------------------------------------------------

        cls.finance_employee_user = User.objects.create_user(
            username="financeemployee",
            email="financeemployee@test.com",
            password="Admin@123",
        )

        cls.finance_employee = Employee.objects.create(
            user=cls.finance_employee_user,
            employee_code="EMP000008",
            first_name="Finance",
            last_name="Employee",
            email="financeemployee@test.com",
            phone_number="9000000008",
            date_of_birth=date(1998, 1, 1),
            date_of_joining=date.today(),
            department=cls.finance_department,
            designation=cls.designation,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

        # -----------------------------------------------------
        # Employee outside HOD department
        # -----------------------------------------------------

        cls.it_employee_user = User.objects.create_user(
            username="itemployee",
            email="itemployee@test.com",
            password="Admin@123",
        )

        cls.it_employee = Employee.objects.create(
            user=cls.it_employee_user,
            employee_code="EMP000009",
            first_name="IT",
            last_name="Employee",
            email="itemployee@test.com",
            phone_number="9000000009",
            date_of_birth=date(1998, 1, 1),
            date_of_joining=date.today(),
            department=cls.it_department,
            designation=cls.designation,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

    # ---------------------------------------------------------
    # Admin
    # ---------------------------------------------------------

    def test_admin_can_access_all_employees(self):

        accessible_employees = get_accessible_employees(
            self.admin,
        )

        self.assertCountEqual(
            accessible_employees,
            Employee.objects.all(),
        )

    # ---------------------------------------------------------
    # HR
    # ---------------------------------------------------------

    def test_hr_can_access_all_employees(self):

        accessible_employees = get_accessible_employees(
            self.hr,
        )

        self.assertCountEqual(
            accessible_employees,
            Employee.objects.all(),
        )

    # ---------------------------------------------------------
    # Manager
    # ---------------------------------------------------------

    def test_manager_can_access_direct_subordinates(self):

        accessible_employees = get_accessible_employees(
            self.manager,
        )

        self.assertIn(
            self.direct_subordinate,
            accessible_employees,
        )

        self.assertIn(
            self.indirect_manager,
            accessible_employees,
        )

    def test_manager_cannot_access_indirect_subordinates(self):

        accessible_employees = get_accessible_employees(
            self.manager,
        )

        self.assertNotIn(
            self.indirect_subordinate,
            accessible_employees,
        )

    def test_manager_cannot_access_unrelated_employees(self):

        accessible_employees = get_accessible_employees(
            self.manager,
        )

        self.assertNotIn(
            self.hr,
            accessible_employees,
        )

        self.assertNotIn(
            self.hod,
            accessible_employees,
        )

    # ---------------------------------------------------------
    # HOD
    # ---------------------------------------------------------

    def test_hod_can_access_all_employees_in_headed_department(self):

        accessible_employees = get_accessible_employees(
            self.hod,
        )

        self.assertIn(
            self.hod,
            accessible_employees,
        )

        self.assertIn(
            self.finance_employee,
            accessible_employees,
        )

    def test_hod_cannot_access_employees_outside_headed_department(self):

        accessible_employees = get_accessible_employees(
            self.hod,
        )

        self.assertNotIn(
            self.it_employee,
            accessible_employees,
        )

        self.assertNotIn(
            self.manager,
            accessible_employees,
        )

    # ---------------------------------------------------------
    # Employee
    # ---------------------------------------------------------

    def test_employee_can_access_only_themselves(self):

        accessible_employees = get_accessible_employees(
            self.finance_employee,
        )

        self.assertEqual(
            accessible_employees.count(),
            1,
        )

        self.assertIn(
            self.finance_employee,
            accessible_employees,
        )

    def test_employee_cannot_access_other_employees(self):

        accessible_employees = get_accessible_employees(
            self.finance_employee,
        )

        self.assertNotIn(
            self.hod,
            accessible_employees,
        )

        self.assertNotIn(
            self.manager,
            accessible_employees,
        )

        self.assertNotIn(
            self.finance_employee,
            accessible_employees.exclude(
                id=self.finance_employee.id,
            ),
        )