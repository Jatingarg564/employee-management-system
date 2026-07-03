from apps.employees.models import Employee


class EmployeeService:
    """
    Business logic for employee operations.
    """

    @staticmethod
    def create_employee(validated_data):
        """
        Create a new employee.
        """
        employee = Employee.objects.create(**validated_data)
        return employee
    