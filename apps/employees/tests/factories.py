from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.employees.models import (
    Department,
    Designation,
    Employee,
)

from apps.employees.choices import (
    EmploymentRole,
    EmploymentType,
    EmployeeStatus,
)

User = get_user_model()


class EmployeeFactory:

    counter = 1

    @classmethod
    def create_department(cls):

        return Department.objects.create(
            name=f"Department {cls.counter}",
            code=f"D{cls.counter}"
        )

    @classmethod
    def create_designation(cls):

        return Designation.objects.create(
            name=f"Designation {cls.counter}"
        )

    @classmethod
    def create_employee(
        cls,
        department=None,
        designation=None,
        reporting_to=None,
        status=EmployeeStatus.ACTIVE,
    ):

        number = cls.counter
        cls.counter += 1

        if department is None:
            department = cls.create_department()

        if designation is None:
            designation = cls.create_designation()

        user = User.objects.create_user(
            username=f"user{number}",
            email=f"user{number}@test.com",
            password="Admin@123"
        )

        return Employee.objects.create(
            user=user,
            employee_code=f"EMP{Employee.objects.count()+1:04d}",
            first_name="Test",
            last_name=f"User{number}",
            email=f"user{number}@test.com",
            phone_number=f"99999999{number:02d}",
            date_of_birth=date(1998, 1, 1),
            date_of_joining=date.today(),
            department=department,
            designation=designation,
            reporting_to=reporting_to,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=status
        )