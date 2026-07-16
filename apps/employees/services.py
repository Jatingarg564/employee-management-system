from django.contrib.auth.models import User
from django.db import transaction
from apps.employees.models import Employee


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

    @staticmethod
    @transaction.atomic
    def create_employee(validated_data):
        """
        Create a new employee and its corresponding user account.
        """
        # Extract authentication credentials
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        # Extract employee information
        role = validated_data["role"]
        department = validated_data["department"]
        joining_date = validated_data["date_of_joining"]
        joining_year = joining_date.year

        # Create Django user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        # Determine employee sequence
        sequence = EmployeeService.get_next_employee_sequence(
            role=role,
            department=department,
        )

        # Generate employee code
        employee_code = EmployeeService.generate_employee_code(
            role=role,
            department=department,
            joining_year=joining_year,
            sequence=sequence,
        )

        # Prepare employee data
        validated_data["user"] = user
        validated_data["employee_code"] = employee_code

        # Create employee
        employee = Employee.objects.create(
            **validated_data
        )

        return employee

    @staticmethod
    def update_employee(employee, validated_data):
        """
        Update an existing employee.
        """
        for attr, value in validated_data.items():
            setattr(employee, attr, value)

        employee.save()

        return employee

    @staticmethod
    def update_employee_status(employee, status):
        """
        Update the status of an existing employee.
        """
        employee.status = status
        employee.save()

        return employee

    @staticmethod
    def soft_delete_employee(employee):
        """
        Soft delete an existing employee.
        """
        employee.is_deleted = True
        employee.save()

        return employee

    @staticmethod
    def transfer_employee(employee_id):
        """
        Transfer an existing employee.
        """

        employee = Employee.objects.get(
            id=employee_id,
        )

        return employee