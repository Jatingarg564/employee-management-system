from apps.employees.models import Employee


class EmployeeService:
    """
    Business logic for employee operations.
    """

    @staticmethod
    def generate_employee_code(role, joining_year):
        """
        Generate an employee code.

        Format:
        <ROLE><YEAR><SEQUENCE>

        Example:
        EM20260001
        """

        employees = (
            Employee.objects.filter(
                employee_code__contains=str(joining_year)
            )
            .order_by("-employee_code")
        )

        if not employees.exists():
            sequence = 1
        else:
            last_employee = employees.first()

            last_sequence = int(
                last_employee.employee_code[-4:]
            )

            sequence = last_sequence + 1

        return f"{role}{joining_year}{sequence:04d}"

    @staticmethod
    def create_employee(validated_data):
        """
        Create a new employee.
        """

        role = validated_data["role"]

        joining_year = validated_data[
            "date_of_joining"
        ].year

        employee_code = EmployeeService.generate_employee_code(
            role,
            joining_year,
        )

        validated_data["employee_code"] = employee_code

        employee = Employee.objects.create(
            **validated_data
        )

        return employee
    