from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.employees.choices import (
    EmployeeStatus,
)
from apps.employees.models import (
    Department,
    Employee,
)
from apps.employees.validators import (
    validate_department_transfer,
    validate_status_transition,
    validate_department_leadership_integrity,
)


class EmployeeService:
    """
    Business logic for employee operations.
    """

    @staticmethod
    def get_next_employee_sequence(role, department):
        """
        Get the next employee sequence for a role and department.
        """

        last_employee = (
            Employee.objects.filter(
                role=role,
                department=department,
            )
            .order_by("-id")
            .first()
        )

        if last_employee is None:
            return 1

        return int(last_employee.employee_code[-4:]) + 1

    @staticmethod
    def get_employee_sequence(employee_code):
        """
        Extract the sequence number from an employee code.
        """

        return int(employee_code[-4:])

    @staticmethod
    def generate_employee_code(
        role,
        department,
        joining_year,
        sequence,
    ):
        """
        Generate an employee code.

        Format:
        <ROLE><DEPARTMENT><YEAR><SEQUENCE>

        Example:
        EMIT20260001
        """

        return (
            f"{role}"
            f"{department.code}"
            f"{joining_year}"
            f"{sequence:04d}"
        )

    @classmethod
    @transaction.atomic
    def create_employee(cls, validated_data):
        """
        Create a new employee and its corresponding user account.
        """

        username = validated_data.pop("username")
        password = validated_data.pop("password")

        role = validated_data["role"]
        department = validated_data["department"]
        joining_date = validated_data["date_of_joining"]
        joining_year = joining_date.year

        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        sequence = cls.get_next_employee_sequence(
            role=role,
            department=department,
        )

        employee_code = cls.generate_employee_code(
            role=role,
            department=department,
            joining_year=joining_year,
            sequence=sequence,
        )

        if Employee.objects.filter(
            employee_code=employee_code
        ).exists():
            raise ValidationError(
                {
                    "employee_code": (
                        "An employee with this generated employee code "
                        "already exists."
                    )
                }
            )

        validated_data["user"] = user
        validated_data["employee_code"] = employee_code

        employee = Employee.objects.create(
            **validated_data,
        )

        return employee

    @classmethod
    @transaction.atomic
    def update_employee(
        cls,
        employee,
        validated_data,
    ):
        """
        Update employee information.

        Before applying changes, ensure that changes to role or
        department do not invalidate any department leadership
        assignments held by the employee.
        """

        old_role = employee.role
        old_department = employee.department
        old_joining_date = employee.date_of_joining

        new_role = validated_data.get(
            "role",
            employee.role,
        )

        new_department = validated_data.get(
            "department",
            employee.department,
        )

        validate_department_leadership_integrity(
            employee,
            new_role=new_role,
        )

        updatable_fields = (
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "address",
            "profile_photo",
            "department",
            "designation",
            "reporting_to",
            "date_of_joining",
            "employment_type",
            "role",
            "salary",
        )

        for field in updatable_fields:
            if field in validated_data:
                setattr(
                    employee,
                    field,
                    validated_data[field],
                )

        if (
            old_role != employee.role
            or old_department != employee.department
            or (
                old_joining_date.year
                != employee.date_of_joining.year
            )
        ):
            sequence = cls.get_employee_sequence(
                employee.employee_code,
            )

            employee.employee_code = cls.generate_employee_code(
                role=employee.role,
                department=employee.department,
                joining_year=employee.date_of_joining.year,
                sequence=sequence,
            )

        employee.save()

        return employee

    @classmethod
    @transaction.atomic
    def update_employee_status(
        cls,
        employee,
        validated_data,
    ):
        """
        Update an employee's status and perform all related
        business actions.
        """

        old_status = employee.status

        new_status = validated_data["status"]

        validate_status_transition(
            employee,
            new_status,
        )

        validate_department_leadership_integrity(
            employee=employee,
            new_status=new_status,
        )

        employee.status = new_status

        status_handlers = {
            EmployeeStatus.ACTIVE: cls._handle_active_status,
            EmployeeStatus.ON_LEAVE: cls._handle_on_leave_status,
            EmployeeStatus.INACTIVE: cls._handle_inactive_status,
            EmployeeStatus.RESIGNED: cls._handle_resigned_status,
            EmployeeStatus.TERMINATED: cls._handle_terminated_status,
        }

        handler = status_handlers.get(
            new_status,
        )

        if handler:
            handler(
                employee,
                old_status,
            )

        employee.user.save()
        employee.save()

        return employee

    @classmethod
    def _handle_active_status(
        cls,
        employee,
        old_status,
    ):
        """
        Handle ACTIVE status.
        """

        employee.user.is_active = True

    @classmethod
    def _handle_on_leave_status(
        cls,
        employee,
        old_status,
    ):
        """
        Handle ON_LEAVE status.
        """

        employee.user.is_active = True

    @classmethod
    def _handle_inactive_status(
        cls,
        employee,
        old_status,
    ):
        """
        Handle INACTIVE status.
        """

        employee.user.is_active = False

    @classmethod
    def _handle_resigned_status(
        cls,
        employee,
        old_status,
    ):
        """
        Handle RESIGNED status.
        """

        employee.user.is_active = False

        if employee.resignation_date is None:
            employee.resignation_date = timezone.now().date()

    @classmethod
    def _handle_terminated_status(
        cls,
        employee,
        old_status,
    ):
        """
        Handle TERMINATED status.
        """

        employee.user.is_active = False

        if employee.termination_date is None:
            employee.termination_date = timezone.now().date()

    @classmethod
    @transaction.atomic
    def soft_delete_employee(
        cls,
        employee,
    ):
        """
        Soft delete an employee by deactivating the account.

        An employee assigned to department leadership cannot be
        deactivated without first resolving those assignments.
        """

        validate_department_leadership_integrity(
            employee=employee,
            new_status=EmployeeStatus.INACTIVE,
        )

        employee.status = EmployeeStatus.INACTIVE
        employee.user.is_active = False

        employee.user.save()
        employee.save()

        return employee

    @classmethod
    @transaction.atomic
    def transfer_employee(
        cls,
        employee_id,
        new_department,
        reporting_to=None,
    ):
        """
        Transfer an employee to another department.
        """

        employee = Employee.objects.get(
            id=employee_id,
        )

        validate_department_transfer(
            employee,
            new_department,
        )

        validate_department_leadership_integrity(
            employee=employee,
            new_department=new_department,
        )

        employee.department = new_department

        if reporting_to is not None:
            employee.reporting_to = reporting_to

        employee.save()

        return employee


class DepartmentService:
    """
    Business logic for department operations.
    """

    @staticmethod
    @transaction.atomic
    def create_department(validated_data):
        """
        Create a new department.
        """

        department = Department.objects.create(
            **validated_data,
        )

        return department

    @staticmethod
    @transaction.atomic
    def update_department(
        department,
        validated_data,
    ):
        """
        Update an existing department.
        """

        updatable_fields = [
            "name",
            "code",
            "manager",
            "head",
            "budget",
            "location",
        ]

        for field in updatable_fields:
            if field in validated_data:
                setattr(
                    department,
                    field,
                    validated_data[field],
                )

        department.save()

        return department

    @staticmethod
    @transaction.atomic
    def deactivate_department(department):
        """
        Soft deactivate a department.

        A department cannot be deactivated while it has
        active employees.
        """

        active_employees = department.employees.filter(
            status=EmployeeStatus.ACTIVE,
        )

        if active_employees.exists():
            raise ValidationError(
                {
                    "detail": (
                        "Department cannot be deactivated "
                        "because it has active employees."
                    )
                }
            )

        department.is_active = False

        department.save(
            update_fields=[
                "is_active",
                "updated_at",
            ],
        )

        return department