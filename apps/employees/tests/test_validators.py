from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

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
from apps.employees.validators import (
    validate_age,
    validate_department_head,
    validate_department_transfer,
    validate_email_uniqueness,
    validate_joining_date,
    validate_reporting_hierarchy,
    validate_reporting_manager,
    validate_salary,
    validate_status_transition,
    validate_username_uniqueness,
)


class EmployeeValidatorTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.department = Department.objects.create(
            name="IT",
            code="IT"
        )

        cls.department2 = Department.objects.create(
            name="HR",
            code="HR"
        )

        cls.designation = Designation.objects.create(
            name="Software Engineer"
        )

        cls.user = User.objects.create_user(
            username="john",
            password="Admin@123",
            email="john@test.com",
        )

        cls.employee = Employee.objects.create(
            user=cls.user,
            employee_code="EMIT20260001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            phone_number="9999999999",
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date.today(),
            department=cls.department,
            designation=cls.designation,
            employment_type=EmploymentType.FULL_TIME,
            role=EmploymentRole.EMPLOYEE,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

    # ----------------------------------------------------------
    # EMAIL VALIDATOR
    # ----------------------------------------------------------

    def test_duplicate_email_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_email_uniqueness(
                None,
                "john@test.com"
            )

    def test_new_email_should_pass(self):

        validate_email_uniqueness(
            None,
            "new@test.com"
        )

    def test_same_employee_email_should_pass(self):

        validate_email_uniqueness(
            self.employee,
            "john@test.com"
        )

    # ----------------------------------------------------------
    # USERNAME VALIDATOR
    # ----------------------------------------------------------

    def test_duplicate_username_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_username_uniqueness(
                None,
                "john"
            )

    def test_new_username_should_pass(self):

        validate_username_uniqueness(
            None,
            "newuser"
        )

    def test_same_username_should_pass(self):

        validate_username_uniqueness(
            self.user,
            "john"
        )

    # ----------------------------------------------------------
    # AGE VALIDATOR
    # ----------------------------------------------------------

    def test_age_above_18_should_pass(self):

        validate_age(
            date(1995, 1, 1),
            date.today()
        )

    def test_age_exactly_18_should_pass(self):

        joining = date.today()

        dob = joining.replace(
            year=joining.year - 18
        )

        validate_age(
            dob,
            joining
        )

    def test_age_below_18_should_raise_error(self):

        joining = date.today()

        dob = joining - timedelta(days=365 * 17)

        with self.assertRaises(ValidationError):
            validate_age(
                dob,
                joining
            )

    # ----------------------------------------------------------
    # JOINING DATE
    # ----------------------------------------------------------

    def test_today_joining_should_pass(self):

        validate_joining_date(
            timezone.now().date()
        )

    def test_past_joining_should_pass(self):

        validate_joining_date(
            timezone.now().date() - timedelta(days=10)
        )

    def test_future_joining_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_joining_date(
                timezone.now().date() + timedelta(days=5)
            )

    # ----------------------------------------------------------
    # SALARY
    # ----------------------------------------------------------

    def test_positive_salary_should_pass(self):

        validate_salary(10000)

    def test_zero_salary_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_salary(0)

    def test_negative_salary_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_salary(-1)

    # ----------------------------------------------------------
    # REPORTING MANAGER
    # ----------------------------------------------------------

    def test_self_reporting_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_reporting_manager(
                self.employee,
                self.employee
            )

    def test_none_reporting_manager_should_pass(self):

        validate_reporting_manager(
            self.employee,
            None
        )

    # ----------------------------------------------------------
    # REPORTING HIERARCHY
    # ----------------------------------------------------------

    def test_valid_reporting_hierarchy(self):

        validate_reporting_hierarchy(
            self.employee,
            None
        )

    # ----------------------------------------------------------
    # DEPARTMENT HEAD
    # ----------------------------------------------------------

    def test_same_department_head_should_pass(self):

        validate_department_head(
            self.department,
            self.employee
        )

    def test_different_department_head_should_raise_error(self):

        self.employee.department = self.department2

        with self.assertRaises(ValidationError):
            validate_department_head(
                self.department,
                self.employee
            )

    def test_inactive_department_head_should_raise_error(self):

        self.employee.department = self.department
        self.employee.status = EmployeeStatus.INACTIVE

        with self.assertRaises(ValidationError):
            validate_department_head(
                self.department,
                self.employee
            )

    # ----------------------------------------------------------
    # DEPARTMENT TRANSFER
    # ----------------------------------------------------------

    def test_transfer_active_employee(self):

        validate_department_transfer(
            self.employee,
            self.department2
        )

    def test_transfer_same_department_should_raise_error(self):

        with self.assertRaises(ValidationError):
            validate_department_transfer(
                self.employee,
                self.department
            )

    def test_transfer_resigned_employee_should_raise_error(self):

        self.employee.status = EmployeeStatus.RESIGNED

        with self.assertRaises(ValidationError):
            validate_department_transfer(
                self.employee,
                self.department2
            )

    # ----------------------------------------------------------
    # STATUS TRANSITIONS
    # ----------------------------------------------------------

    def test_active_to_inactive(self):

        validate_status_transition(
            self.employee,
            EmployeeStatus.INACTIVE
        )

    def test_active_to_resigned(self):

        validate_status_transition(
            self.employee,
            EmployeeStatus.RESIGNED
        )

    def test_terminated_transition_should_raise_error(self):

        self.employee.status = EmployeeStatus.TERMINATED

        with self.assertRaises(ValidationError):
            validate_status_transition(
                self.employee,
                EmployeeStatus.ACTIVE
            )

    def test_resigned_reactivation_within_30_days(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = (
            timezone.now().date() - timedelta(days=15)
        )

        validate_status_transition(
            self.employee,
            EmployeeStatus.ACTIVE
        )

    def test_resigned_reactivation_after_30_days_should_raise_error(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = (
            timezone.now().date() - timedelta(days=35)
        )

        with self.assertRaises(ValidationError):
            validate_status_transition(
                self.employee,
                EmployeeStatus.ACTIVE
            )

    def test_resigned_without_date_should_raise_error(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = None

        with self.assertRaises(ValidationError):
            validate_status_transition(
                self.employee,
                EmployeeStatus.ACTIVE
            )